# LineGuard build and production-readiness notes

This source archive contains the Expo/React Native app and a GitHub Actions workflow that builds a release APK.

## Changes in this revision

- The Feed tab is labelled **Board** and presents a public case-board heading and an allegation/dispute notice.
- Removed fabricated sample public incident reports, including the old sample ₹500 payment.
- Replaced the sample community post claiming a ₹1,000 payment with responsible-reporting guidance.
- Added a client-side validation that rejects resolution amounts above ₹100.
- Resolution UI copy now states that a locally recorded amount is **not proof of payment**.
- GitHub Actions workflow runs TypeScript checking, Expo prebuild, Gradle release build, APK verification and artifact upload.

## Important limitations — do not treat this as production-ready

The existing app authentication in `context/AppContext.tsx` is local AsyncStorage email/password storage. It is **not Firebase Authentication**, does not provide phone OTP, and must not be used for real user accounts. A wrong OTP cannot be validated because OTP authentication is not implemented in this source.

Reports, communities, comments and resolution records are also stored locally on one device. There is no shared cloud case database, reporter/accused identity verification, secure case invitation/QR, moderation backend, dispute workflow, or audit trail. The public board therefore is not a live multi-user public service.

The ₹100 check currently exists in the app client only. It is not server-enforced. Do not accept real money or rely on the amount as a contractual payment rule until a trusted backend enforces the limit and verifies provider callbacks/webhooks. The current resolution screen does not initiate or verify UPI/Stripe payments; it records a local demo state only.

The APK produced by GitHub Actions is an installable build of this source, not proof that Firebase, OTP, payments, identity verification, cloud sync, or moderation are operational. Those services require implementation, configuration, credentials and end-to-end testing before public launch.

## Build

Upload this ZIP to the repository root, extract its `LineGuard-Recovered-Original/` folder into the repository root (or upload the contents of that folder), then run **Actions → LineGuard Android Release APK → Run workflow**. Download the `LineGuard-Android-APK` artifact only after the workflow succeeds.
