# LineGuard secure backend foundation

## Implemented in this source
- Firebase Admin ID-token verification on case and admin endpoints.
- Server-only Firestore case writes; Firestore client rules deny direct case/payment writes.
- High-entropy, one-use invitation code; only its SHA-256 digest is stored.
- Two-party confirmation of the same compensation amount (₹0–₹100).
- Dispute endpoint and append-only case event records.
- Razorpay order creation only after agreement; webhook HMAC verification and idempotent captured-payment ledger.
- 50/50 gross allocation ledger in paise; processing fee is recorded as unknown until provider settlement data is reconciled.
- Admin-only Google Sheets export with limited operational fields (no evidence URLs or private content).
- Mobile case creation/list calls use the authenticated API; the client cannot mark payment successful.

## Required before deployment
1. Create a Firebase Admin service account in Google Cloud and store its JSON outside source control in the host's secret manager. Never commit it or send it in chat.
2. Deploy `artifacts/api-server` with `FIREBASE_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`, and `PORT`.
3. Set `EXPO_PUBLIC_API_URL` to the deployed HTTPS API URL and rebuild the native Android app.
4. Configure Razorpay test credentials and a webhook URL `/api/webhooks/razorpay` for `payment.captured`. Use sandbox credentials only for testing.
5. **Marketplace settlement is not activated by this code.** Razorpay Route/linked-account onboarding, reporter linked accounts, transfer creation, refund/dispute handling, KYC, provider fee allocation and provider approval must be completed and tested before live payments. Current ledger records the 50/50 split but does not transfer funds automatically.
6. Create a Google Sheet with a `Cases` tab, share it with the service-account email as Editor, and set the spreadsheet ID plus admin UID allowlist.
7. Deploy the root `firestore.rules` to Firebase.
8. Test with two separate Firebase accounts: invitation use, authorization boundaries, duplicate confirmations, disputes, duplicate webhook delivery, invalid signatures and wrong captured amounts.

## Important limitations
- Existing community posts, communities, and evidence upload storage are not yet migrated to a secure cloud workflow. Evidence URIs are currently metadata only and may be local device paths; do not rely on them as durable shared evidence.
- The admin sheet is a manual admin-triggered export endpoint, not a background sync worker.
- Do not publish until legal review, privacy policy, account deletion, moderation/report handling, Data safety declarations, production OTP, provider approval, device testing and Play policy checks are complete.

## Build note
The API package now declares `firebase-admin` and `googleapis`. The lockfile could not be regenerated in this environment because the package registry was unreachable. Run `pnpm install` (not frozen-lockfile) in a network-enabled environment, review the lockfile changes, then run typecheck and builds.


## Evidence storage and payment settlement additions
- Set `FIREBASE_STORAGE_BUCKET` to the project's private Firebase Storage bucket. The API issues short-lived signed upload URLs, moves uploads into a case-specific object path, and returns short-lived signed read URLs only to case participants. Evidence is limited to five files, supported image/video MIME types, and 25 MB per file. Configure Firebase Storage lifecycle rules and retention according to your privacy policy.
- Set `PUBLIC_API_URL` to the public HTTPS API origin. The API serves a hosted Razorpay Checkout page at `/api/checkout/:orderId`; the app opens it using the system browser. Razorpay's signed webhook remains the sole source of truth for captured payments.
- For automatic reporter settlement, each reporter must first be onboarded and approved as a Razorpay Route Linked Account. Store the resulting linked-account identifier on that user's server-side `users/{uid}.razorpayLinkedAccountId` record only after provider verification. Never accept this ID from a mobile client. The webhook then requests a transfer of the reporter's 50% share. The other 50% remains in the LineGuard merchant account. Provider fees are recorded separately and their allocation is not yet defined.
- Route transfers are not guaranteed: they require Razorpay Route enablement, eligible merchant onboarding, linked-account KYC, and sufficient provider permissions. Missing linked-account configuration is recorded as a blocked settlement, not falsely marked settled.
- Test checkout and transfers in Razorpay test mode with provider-approved test linked accounts before enabling live credentials.


## Cloud Run deployment template
The repository includes `Dockerfile.lineguard-api` and `cloudbuild-lineguard-api.yaml` as deployment templates for Google Cloud Run in `asia-south1`. Before using them, regenerate and commit `pnpm-lock.yaml` from a network-enabled environment, review the Docker build, create a dedicated Cloud Run runtime service account, and grant only the required Firebase/Firestore/Storage permissions. Deploy with secrets supplied from Secret Manager; do not bake credentials into the image. Configure `FIREBASE_PROJECT_ID`, `FIREBASE_STORAGE_BUCKET`, `PUBLIC_API_URL`, Razorpay test keys, webhook secret, and `GOOGLE_SHEETS_SPREADSHEET_ID`. Set `EXPO_PUBLIC_API_URL` in the mobile build environment to the deployed HTTPS API origin.

For Sheets, the preferred Cloud Run setup uses Application Default Credentials from the attached runtime service account. Share the target spreadsheet with that service account's email as Editor. Alternatively, supply `GOOGLE_SERVICE_ACCOUNT_EMAIL` and `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY` through Secret Manager. Set `LINEGUARD_ADMIN_UIDS` to the Firebase UID(s) allowed to trigger sync.

Subscribe the Razorpay webhook to `payment.captured`, `transfer.processed`, and `transfer.failed`, and set its signing secret as `RAZORPAY_WEBHOOK_SECRET`. A successful payment capture is not treated as final resolution until Razorpay confirms the reporter transfer as processed.


## Compensation cap and commission
The agreed total compensation is capped at ₹200 so that the reporter's 50% share can never exceed ₹100. LineGuard receives the other 50%. Payment-provider processing fees are separate and their allocation has not yet been decided; do not silently deduct them from either party without an explicit product decision and clear checkout disclosure.
