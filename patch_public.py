from pathlib import Path
root=Path('/tmp/lgpub')
def read(p): return (root/p).read_text()
def write(p,s): (root/p).write_text(s)

# Clean duplicate imports/exports and fix malformed literal newline introduced in prior patch.
p=Path('artifacts/api-server/src/lib/firebase-admin.ts')
s=read(p)
s=s.replace("import { getStorage } from 'firebase-admin/storage';\nimport { getStorage } from 'firebase-admin/storage';", "import { getStorage } from 'firebase-admin/storage';")
s=s.replace("export const adminBucket = getStorage(app).bucket(process.env.FIREBASE_STORAGE_BUCKET || (projectId ? `${projectId}.firebasestorage.app` : undefined));\nexport const adminBucket = getStorage(app).bucket(process.env.FIREBASE_STORAGE_BUCKET || (projectId ? `${projectId}.firebasestorage.app` : undefined));", "export const adminBucket = getStorage(app).bucket(process.env.FIREBASE_STORAGE_BUCKET || (projectId ? `${projectId}.firebasestorage.app` : undefined));")
write(p,s)
p=Path('artifacts/lineguard/app/detail/[id].tsx')
s=read(p).replace('useState(false);\\n  const [publicApologyDraft', 'useState(false);\n  const [publicApologyDraft')
s=s.replace('reviewCaseApology } from "@/lib/cases-api";', 'reviewCaseApology, setPublicListingConsent } from "@/lib/cases-api";')
s=s.replace('  const [publicApologyDraft, setPublicApologyDraft] = useState("");', '  const [publicApologyDraft, setPublicApologyDraft] = useState("");\n  const [publicConsentBusy, setPublicConsentBusy] = useState(false);')
# Consent handler after review handler
anchor='  const handleDispute = async () => {'
handler='''  const handlePublicConsent = async (enabled: boolean) => {
    try {
      setPublicConsentBusy(true);
      await setPublicListingConsent(report.id, enabled);
      await refreshCases();
      Alert.alert(enabled ? "Public listing consent saved" : "Public listing consent withdrawn", enabled ? "The public Shameboard listing will appear only after both participants consent and the apology is approved." : "This case will be removed from the public Shameboard.");
    } catch (error: any) {
      Alert.alert("Could not update public consent", error?.message || "Please try again.");
    } finally { setPublicConsentBusy(false); }
  };

'''
s=s.replace(anchor,handler+anchor)
# Add consent panel after apology UI and before metadata
needle='''          <View style={styles.metaRow}>
'''
consent='''          {isParticipant && report.caseStatus === "agreed" && report.apologyStatus === "approved" ? (
            <View style={{ marginTop: 16, padding: 16, borderRadius: 16, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, gap: 10 }}>
              <Text style={{ color: colors.foreground, fontSize: 15, fontWeight: "800" }}>Public Shameboard permission</Text>
              <Text style={{ color: colors.mutedForeground, fontSize: 12, lineHeight: 18 }}>The public listing can show both participants’ names, the incident description, the approved apology and attached images/videos. Anyone may copy or share public material. Exact contact details and email addresses are never shown. Both participants must opt in; either can withdraw consent later.</Text>
              <Text style={{ color: colors.foreground, fontSize: 13, fontWeight: "700" }}>Your consent: {((isOwner && report.reporterPublicConsent) || (!isOwner && report.accusedPublicConsent)) ? "Granted" : "Not granted"}</Text>
              <TouchableOpacity disabled={publicConsentBusy} onPress={() => handlePublicConsent(!((isOwner && report.reporterPublicConsent) || (!isOwner && report.accusedPublicConsent)))} style={{ backgroundColor: ((isOwner && report.reporterPublicConsent) || (!isOwner && report.accusedPublicConsent)) ? colors.card : colors.primary, borderWidth: 1, borderColor: colors.primary, borderRadius: 10, padding: 13, alignItems: "center", opacity: publicConsentBusy ? 0.6 : 1 }}>
                <Text style={{ color: ((isOwner && report.reporterPublicConsent) || (!isOwner && report.accusedPublicConsent)) ? colors.primary : "#fff", fontWeight: "800" }}>{publicConsentBusy ? "Please wait…" : ((isOwner && report.reporterPublicConsent) || (!isOwner && report.accusedPublicConsent)) ? "Withdraw public consent" : "I consent to public listing"}</Text>
              </TouchableOpacity>
              <Text style={{ color: colors.mutedForeground, fontSize: 11 }}>Reporter: {report.reporterPublicConsent ? "Consented" : "Not yet"} · Accused: {report.accusedPublicConsent ? "Consented" : "Not yet"}</Text>
            </View>
          ) : null}

'''
s=s.replace(needle,consent+needle,1)
write(p,s)

# API client: unauthenticated public endpoint + authenticated consent endpoint.
p=Path('artifacts/lineguard/lib/cases-api.ts')
s=read(p)
s += '''

export type PublicShameboardCase = {
  caseId: string;
  reporterName: string;
  accusedName: string;
  description: string;
  apologyText: string;
  evidence: string[];
  evidenceTypes: ("image" | "video")[];
  createdAt?: any;
  paymentStatus?: string;
};

export async function listPublicShameboard(): Promise<{ cases: PublicShameboardCase[] }> {
  if (!API_BASE) throw new Error('LineGuard secure server is not configured.');
  const response = await fetch(`${API_BASE}/api/public/shameboard`);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof body.error === 'string' ? body.error : 'Could not load the public Shameboard.');
  return body as { cases: PublicShameboardCase[] };
}

export const setPublicListingConsent = (caseId: string, enabled: boolean) =>
  request<{ ok: boolean; reporterPublicConsent: boolean; accusedPublicConsent: boolean }>(`/cases/${encodeURIComponent(caseId)}/public-consent`, {
    method: 'POST', body: JSON.stringify({ enabled }),
  });
'''
# Extend ServerCase fields
s=s.replace('  apologySubmittedAt?: any; apologyReviewedAt?: any;\n};', '  apologySubmittedAt?: any; apologyReviewedAt?: any;\n  reporterPublicConsent?: boolean; accusedPublicConsent?: boolean;\n};')
write(p,s)

# Backend: add participant consent route and public read-only route.
p=Path('artifacts/api-server/src/routes/cases.ts')
s=read(p)
anchor="router.post('/cases/:caseId/dispute', requireAuth, async (req, res) => {"
routes='''router.post('/cases/:caseId/public-consent', requireAuth, async (req, res) => {
  if (typeof req.body?.enabled !== 'boolean') return res.status(400).json({ error: 'Consent must be true or false.' });
  try {
    const result = await adminDb.runTransaction(async tx => {
      const ref = adminDb.collection('cases').doc(req.params.caseId);
      const snap = await tx.get(ref);
      if (!snap.exists) throw new Error('Case not found.');
      const data = snap.data()!;
      if (!isMember(data, req.user!.uid)) throw new Error('Only case participants can change public listing consent.');
      if (data.status === 'disputed' || data.status === 'dismissed') throw new Error('Disputed or dismissed cases cannot be publicly listed.');
      if (data.apologyStatus !== 'approved') throw new Error('The apology must be approved before public listing consent can be given.');
      const field = data.reporterId === req.user!.uid ? 'reporterPublicConsent' : 'accusedPublicConsent';
      tx.update(ref, { [field]: req.body.enabled, updatedAt: FieldValue.serverTimestamp() });
      tx.create(adminDb.collection('caseEvents').doc(), { caseId: snap.id, actorId: req.user!.uid, type: req.body.enabled ? 'public_listing_consent_granted' : 'public_listing_consent_withdrawn', at: FieldValue.serverTimestamp() });
      return { reporterPublicConsent: field === 'reporterPublicConsent' ? req.body.enabled : !!data.reporterPublicConsent, accusedPublicConsent: field === 'accusedPublicConsent' ? req.body.enabled : !!data.accusedPublicConsent };
    });
    return res.json({ ok: true, ...result });
  } catch (e) { return res.status(409).json({ error: e instanceof Error ? e.message : 'Could not update public consent.' }); }
});

// Public read-only Shameboard. Only cases with both participants' explicit consent
// and an approved apology are exposed. No IDs, emails, exact locations, or payment details are returned.
router.get('/public/shameboard', async (_req, res) => {
  try {
    const snapshot = await adminDb.collection('cases').where('reporterPublicConsent', '==', true).limit(200).get();
    const eligible = snapshot.docs.filter(doc => {
      const d = doc.data();
      return d.accusedPublicConsent === true && d.apologyStatus === 'approved' && !!d.apologyText && !['disputed', 'dismissed'].includes(d.status) && !!d.accusedId;
    }).slice(0, 60);
    const cases = await Promise.all(eligible.map(async doc => {
      const d = doc.data();
      const [reporterSnap, accusedSnap] = await Promise.all([
        adminDb.collection('users').doc(d.reporterId).get(),
        adminDb.collection('users').doc(d.accusedId).get(),
      ]);
      const reporterName = clean(reporterSnap.data()?.name, 80) || 'Consenting reporter';
      const accusedName = clean(accusedSnap.data()?.name, 80) || 'Consenting participant';
      const evidencePaths: string[] = Array.isArray(d.evidence) ? d.evidence.slice(0, 5) : [];
      const evidence = await Promise.all(evidencePaths.map(async (path: string) => {
        const [url] = await adminBucket.file(path).getSignedUrl({ version: 'v4', action: 'read', expires: Date.now() + 10 * 60 * 1000 });
        return url;
      }));
      return {
        caseId: doc.id, reporterName, accusedName,
        description: clean(d.description, 1500), apologyText: clean(d.apologyText, 1500),
        evidence, evidenceTypes: Array.isArray(d.evidenceTypes) ? d.evidenceTypes.slice(0, evidence.length) : evidence.map(() => 'image'),
        createdAt: d.createdAt?.toDate?.()?.toISOString?.() || null,
      };
    }));
    return res.set('Cache-Control', 'public, max-age=30').json({ cases });
  } catch (error) {
    return res.status(500).json({ error: 'Could not load the public Shameboard.' });
  }
});

'''
if "router.get('/public/shameboard'" not in s: s=s.replace(anchor,routes+anchor)
write(p,s)

# Context model and mapping. Public board entries are merged with participant's private records.
p=Path('artifacts/lineguard/context/AppContext.tsx')
s=read(p)
s=s.replace('createSecureCase, listSecureCases, joinSecureCase as joinCaseApi, type ServerCase', 'createSecureCase, listSecureCases, listPublicShameboard, joinSecureCase as joinCaseApi, type ServerCase')
s=s.replace('  apologyStatus?: \'not_submitted\' | \'pending_review\' | \'approved\' | \'changes_requested\';\n}', '  apologyStatus?: \'not_submitted\' | \'pending_review\' | \'approved\' | \'changes_requested\';\n  reporterPublicConsent?: boolean;\n  accusedPublicConsent?: boolean;\n  accusedName?: string;\n  isPublicListing?: boolean;\n}')
s=s.replace('apologyText: item.apologyText, apologyStatus: item.apologyStatus,', 'apologyText: item.apologyText, apologyStatus: item.apologyStatus, reporterPublicConsent: item.reporterPublicConsent, accusedPublicConsent: item.accusedPublicConsent,')
# add public mapper before context creation
marker='const AppContext = createContext<AppContextType | undefined>(undefined);'
mapper='''function mapPublicCase(item: any): Report {
  const created = typeof item.createdAt === "string" ? item.createdAt : new Date().toISOString();
  return {
    id: item.caseId, reporterId: "public-reporter", accusedId: "public-accused", reporterName: item.reporterName || "Consenting reporter",
    reporterColor: AVATAR_COLORS[0], accusedName: item.accusedName || "Consenting participant",
    description: item.description || "", location: { latitude: 0, longitude: 0, address: "Public listing — exact location hidden" },
    mediaUris: Array.isArray(item.evidence) ? item.evidence : [], mediaTypes: item.evidenceTypes || [], timestamp: created,
    status: "guilty", caseStatus: "agreed", apologyText: item.apologyText, apologyStatus: "approved", isPublicListing: true,
  };
}

'''
s=s.replace(marker,mapper+marker)
# refreshCases loads both datasets and keeps private record precedence
s=s.replace('''    const result = await listSecureCases();
    setReports(result.cases.map(mapServerCase));
  }, []);''','''    const [result, publicResult] = await Promise.all([listSecureCases(), listPublicShameboard().catch(() => ({ cases: [] }))]);
    const privateCases = result.cases.map(mapServerCase);
    const privateIds = new Set(privateCases.map(item => item.id));
    const publicCases = publicResult.cases.map(mapPublicCase).filter(item => !privateIds.has(item.id));
    setReports([...privateCases, ...publicCases]);
  }, []);''')
# Initial auth load same behaviour: load public feed alongside private cases
s=s.replace('''          const result = await listSecureCases();
          setReports(result.cases.map(mapServerCase));''','''          const [result, publicResult] = await Promise.all([listSecureCases(), listPublicShameboard().catch(() => ({ cases: [] }))]);
          const privateCases = result.cases.map(mapServerCase);
          const privateIds = new Set(privateCases.map(item => item.id));
          setReports([...privateCases, ...publicResult.cases.map(mapPublicCase).filter(item => !privateIds.has(item.id))]);''')
write(p,s)

# Report card labels subject name and video evidence safely indicated.
p=Path('artifacts/lineguard/components/ReportCard.tsx')
s=read(p)
s=s.replace('''          <Text style={[styles.description, { color: colors.foreground }]} numberOfLines={2}>
            {report.description}
          </Text>''','''          {report.accusedName ? <Text style={{ color: colors.primary, fontSize: 12, fontFamily: "Inter_700Bold" }}>Subject: {report.accusedName}</Text> : null}
          <Text style={[styles.description, { color: colors.foreground }]} numberOfLines={2}>
            {report.description}
          </Text>
          {report.apologyStatus === "approved" && report.apologyText ? <Text style={{ color: colors.success, fontSize: 12 }} numberOfLines={2}>Approved apology: {report.apologyText}</Text> : null}''')
s=s.replace('''            <Image
              source={{ uri: report.mediaUris[0] }}
              style={styles.image}
              resizeMode="cover"
            />''','''            {report.mediaTypes?.[0] === "video" ? (
              <View style={[styles.image, { backgroundColor: "#111827", alignItems: "center", justifyContent: "center" }]}><Feather name="video" size={34} color="#FFF" /><Text style={{ color: "#FFF", marginTop: 6 }}>Video evidence</Text></View>
            ) : <Image source={{ uri: report.mediaUris[0] }} style={styles.image} resizeMode="cover" />}''')
write(p,s)

# Feed: refresh from backend, not just stop the spinner; public cases are merged in AppContext.
p=Path('artifacts/lineguard/app/(tabs)/index.tsx')
s=read(p)
s=s.replace('const { reports, authUser: user } = useApp();', 'const { reports, authUser: user, refreshCases } = useApp();')
s=s.replace('''  const onRefresh = useCallback(() => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 800);
  }, []);''','''  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try { await refreshCases(); } finally { setRefreshing(false); }
  }, [refreshCases]);''')
s=s.replace('Reports are allegations, not findings. Disputed cases can be challenged. Personal contact details are not displayed.', 'Only cases with both participants’ explicit public-listing consent and an approved apology appear here. Allegations are not findings; disputed cases can be challenged. Contact details and exact locations are hidden.')
s=s.replace('{reports.length}', '{reports.filter(r => r.isPublicListing).length}')
s=s.replace('{reports.filter(r => r.status === "guilty").length}', '{reports.filter(r => r.isPublicListing && r.status === "guilty").length}')
s=s.replace('{reports.reduce((s, r) => s + (r.payment?.amount ?? 0), 0).toLocaleString()}', '{reports.filter(r => r.isPublicListing).length.toLocaleString()}')
s=s.replace('Reported Amount', 'Public Cases')
# Public feed only, keep any private cases out of board list.
s=s.replace('const filtered = reports.filter(r => {', 'const filtered = reports.filter(r => r.isPublicListing && (() => {')
s=s.replace('return matchesSearch && matchesFilter;\n  });', 'return matchesSearch && matchesFilter;\n  })());')
s=s.replace('Be the first to report a line cutter', 'No mutually approved public cases yet')
write(p,s)

# Extend type declaration ServerCase already done, ensure imports are clean.
