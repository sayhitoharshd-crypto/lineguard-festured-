# LineGuard build and test report — 23 November 2026

## Delivery status

**Source updates prepared; APK build NOT completed.** This archive is not an APK and must not be installed as one. No new APK is claimed.

## Changes made in this source update

- Added three verified, publisher-linked examples to the top of the Feed:
  - Chhatarpur hospital queue dispute — Hindustan Times, 20 April 2025.
  - Jama Masjid Metro AFC-gate jumping — NDTV, 15 February 2025.
  - Rajasthan toll queue bypass — India Today, 9 June 2026.
- Each is labelled exactly: “Public news example — not a LineGuard user-submitted case”.
- Used external original-article links; no publisher images/video were copied or embedded.
- Preserved the existing app, API, Firebase Auth/Firestore architecture, tabs, and app ID.
- Removed private case evidence URLs from the public Shameboard response. Public consent now applies to public text and apology only, not participant evidence.
- Added basic public-text redaction for email addresses, Indian mobile numbers, UPI-like IDs, and long numeric account identifiers. This is not a guarantee that every private detail or address will be detected.
- Updated the implementation status document with limitations.

## Validation results

### Passed

- ZIP extraction: 180 archive entries.
- Four core JSON manifests parsed successfully: root package, app package, app config, API package.
- TypeScript/TSX syntax transpilation: 37 files checked; zero syntax diagnostics.
- Static checks confirmed all three Feed examples and disclaimers are present.
- Static check confirmed the public Shameboard endpoint no longer creates signed evidence URLs.
- Static check confirmed the public case mapper no longer maps public evidence.
- Existing code inspection confirmed transactional server-side voting with per-user vote documents, toggle/change/remove semantics, participant exclusion, and the 10-downvote / 10-upvote thresholds.

### Failed or blocked

- Full app TypeScript typecheck: **blocked/fails in this environment** because the workspace dependencies (including `expo/tsconfig.base`, React Native, Expo and workspace packages) are not installed. `tsc` therefore reports missing modules and cannot provide a meaningful project typecheck.
- API typecheck: **not run**; dependencies are not installed.
- Lint: **not run**; no configured lint script was found in the app/API package manifests.
- Dependency installation: **blocked**. Corepack could not reach `registry.npmjs.org` (DNS error `EAI_AGAIN`).
- Android prebuild / Gradle `assembleRelease`: **blocked**. There is no generated `android/` project, no Android SDK (`ANDROID_HOME`/`ANDROID_SDK_ROOT` unset, `android.jar` not found), and no Gradle executable/wrapper JAR in the environment.
- APK verification / SHA-256: **not applicable**; no APK was built.
- Authentication, account registration, password reset and email verification runtime tests: **not run**. They require installed dependencies and a Firebase-connected Android runtime. The source uses Firebase email/password authentication and password reset; no email-verification call was found in this source.
- Case creation, participant confirmation, evidence upload/access: **not run**; require a deployed API and Firebase Admin credentials/Storage.
- Vote create/change/remove and moderation threshold integration tests: **not run**; require Firebase emulator/deployed Firestore and authenticated test accounts.
- Consent/apology tests: **not run**; require deployed backend and two authenticated participant accounts.
- Payment sandbox tests: **not run**; Razorpay test credentials, webhook secret, deployed public API URL, and provider callbacks are not configured.
- Backend authorization tests: **not run**; no Firebase Admin service-account credentials or running API deployment are configured.

## Important outstanding requirements

The source itself documents remaining work: deploy the API and Firestore rules; configure Firebase Admin secrets; configure Razorpay test credentials and webhook; enable and onboard Razorpay Route linked accounts before reporter settlements; configure rate limiting and moderation/admin review operations; implement/verify report and appeal workflows; complete privacy/legal review; and run device-level tests. Community posts and communities are still local demo data in the current source.

The existing API currently has voting and automatic threshold flags, but the archive does not contain a complete human moderation console/workflow or complete report/appeal flow. Those are not represented as completed here.

## Steps required to produce a real APK

1. Use a network-enabled build machine with Node 22, pnpm 10, Java 17, Android SDK platform/build-tools, and Android licenses accepted.
2. At the project root run `pnpm install --frozen-lockfile`.
3. In `artifacts/lineguard`, run `pnpm exec expo prebuild --platform android --clean`.
4. In `artifacts/lineguard/android`, run `./gradlew assembleRelease`.
5. Verify `app/build/outputs/apk/release/app-release.apk`, inspect package ID `com.lineguard.app`, and inspect the APK for the embedded `assets/index.android.bundle`.
6. Install on an Android device and execute the required end-to-end test matrix.
7. Configure release signing before distribution. The archive does not include a release signing key.

## Secrets and deployment setup

- Set `EXPO_PUBLIC_API_URL` to the deployed HTTPS API URL at app build time.
- Configure Firebase Android app/package fingerprints and provide the matching `google-services.json`.
- Configure API-side Firebase Admin service account credentials through the deployment secret manager; never commit them.
- Configure Razorpay test `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`, and `PUBLIC_API_URL` through the deployment secret manager.
- Configure Razorpay Route and each reporter's approved linked-account ID server-side before enabling payouts.
- Provider processing fees remain separately accounted for; their allocation must be explicitly decided before live launch.
- Configure Google Sheets admin export credentials and spreadsheet ID only if that optional admin export is used.

## Signing statement

No APK or AAB was produced in this execution. Therefore there is no signing status or APK checksum to report.


## GitHub Actions build workflow added

A canonical workflow is included at `.github/workflows/android-apk.yml`. It installs Node/pnpm/Java/Android SDK, installs the frozen workspace lockfile, runs the app TypeScript check, executes Expo Android prebuild and Gradle `assembleRelease`, verifies `com.lineguard.app` and the embedded JS bundle, computes SHA-256, and uploads the APK/checksum as a GitHub Actions artifact. The obsolete duplicate workflow that referenced a different, missing ZIP was removed. The workflow has not yet been run; its presence is not evidence of a successful APK build.
