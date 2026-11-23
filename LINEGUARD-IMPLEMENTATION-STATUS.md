# LineGuard implementation status — 16 Nov 2026

This is an implementation source update, not a Play Store release.

## Changes in this update
- Added authenticated API middleware that verifies Firebase ID tokens with revocation checks.
- Added server-side case creation, one-use invitation join, participant access checks, same-amount two-party confirmation, dispute endpoint, and event audit records.
- Mobile report creation now calls the secure API and presents the case ID plus one-time invitation code; case list is fetched from the API.
- Firestore rules deny direct client reads/writes to cases, events and payments.
- Removed the client-side false payment-success path. A client action cannot mark a case paid.
- Added Razorpay order creation after agreement, a hosted Razorpay Checkout page, and HMAC-verified `payment.captured` webhook processing. The webhook calculates the 50/50 gross ledger and attempts a server-side Razorpay Route transfer to the reporter’s approved linked account; it records blocked/failed/in-progress transfer states instead of claiming settlement.
- Added admin-UID-gated Google Sheets export endpoint.
- Added EAS production AAB profile and Android versionCode.

## Not complete / cannot honestly claim release-ready
- No API deployment URL, Firebase Admin service account secret, Razorpay merchant credentials, webhook secret, Sheets service account or spreadsheet ID are configured.
- Automatic reporter transfer is coded but cannot operate until Razorpay Route is enabled and the reporter has an approved linked account ID recorded server-side. Linked-account onboarding is still an external provider/admin step. Provider fees remain separate; their allocation is not decided.
- Mobile invitation joining, two-party confirmation, dispute submission and hosted checkout are connected to the secure API. Payment checkout is shown only after both participants confirm the same amount.
- Evidence uploads now use short-lived signed Firebase Storage upload URLs, are moved under case-specific paths, and are served back through short-lived participant-authorized read URLs. Images/videos are limited to five files and 25 MB each.
- Communities and posts remain local demo data.
- Account deletion, moderation operations, abuse prevention/rate limits, legal/privacy review, Play Data safety declarations and production SMS validation remain outstanding.
- Dependencies were not installed and lockfile was not regenerated because npm registry access failed. TypeScript syntax transpilation passed for the updated source files, but full typecheck/build was not run.
- No APK/AAB was built or tested on a physical Android device.

## Required validation sequence
1. Install dependencies and regenerate lockfile in a network-enabled environment.
2. Run workspace typecheck and API/app production builds; fix all errors.
3. Deploy Firestore rules and API with service account secrets held only in secret manager.
4. Configure Firebase Android SHA fingerprints, Play Integrity/reCAPTCHA and verify OTP on supported devices.
5. Configure Razorpay test mode + webhook and run two-user end-to-end tests, including duplicate/invalid webhooks.
6. Complete provider Route onboarding and linked-account transfer/refund tests before enabling live marketplace payments.
7. Configure and test admin Google Sheets export.
8. Complete remaining client screens and evidence storage, privacy/security/legal checks, then produce and test a signed Android App Bundle.


## Apology and compensation workflow update
- Added authenticated accused-only public apology submission after both participants confirm the same compensation.
- Added reporter-only approve/request-changes review actions.
- Only approved apology text is displayed as public apology content on the case detail screen.
- Existing secure payment checkout remains dependent on deployed backend configuration, Razorpay credentials, signed webhook configuration, and an eligible reporter linked account. A source-code change or APK build does not activate real payments or payouts.
- This update does not claim the Android app has been built or end-to-end tested.


## Public Shameboard endpoint and consent-gated listing
- Added public read-only `GET /api/public/shameboard` endpoint.
- A case is eligible only after its apology is approved and both reporter and accused separately opt in to public listing.
- Added authenticated `POST /api/cases/:caseId/public-consent`; either participant can withdraw their own consent.
- Public response contains consenting participant names, incident description, approved apology, and short-lived signed evidence URLs. It omits account IDs, emails, exact location, and payment details.
- The Feed now loads public listings from the public endpoint and refreshes from the backend. Private participant cases remain available in My Cases and are not automatically exposed.
- Disputed/dismissed cases are excluded from the public endpoint. Withdrawing consent removes the case from subsequent public feed responses; already-issued signed media URLs may remain usable until their short expiry.
- Backend deployment and Firebase service credentials are required. This source change does not itself deploy the endpoint or verify production behavior.
