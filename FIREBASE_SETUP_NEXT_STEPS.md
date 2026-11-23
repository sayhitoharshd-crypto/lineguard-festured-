# LineGuard Firebase setup — phase 1

## Implemented in this source
- React Native Firebase native app, Authentication, and Firestore modules are configured.
- Firebase Email/Password account creation and sign-in replace the old local account store (which stored passwords in AsyncStorage).
- Native Firebase Authentication manages the signed-in session.
- User profile documents are stored in Firestore at `users/{uid}`.
- Password reset email action is wired to the existing Sign In screen.
- Initial Firestore rules: users can access only their own profile; cases and payment records are server-only until the authenticated API is implemented.
- Existing Android `google-services.json` is configured for package `com.lineguard.app`.

## Required Firebase Console steps
1. Open Firebase Console → Authentication → Sign-in method.
2. Enable **Email/Password** and save.
3. Open Firestore Database and create the database in the intended region.
4. Publish the repository's `firestore.rules` rules to the `lineguard-68bb0` project.
5. Before enabling phone OTP, enable **Phone** under Authentication → Sign-in method and add the SHA-1 and SHA-256 fingerprints for the Android build certificate in Project settings → Your apps → Android app. Test the Play Integrity / reCAPTCHA fallback on a real device.

## Important limitations in this phase
- Phone OTP screens and verification callbacks are not yet implemented. The native Firebase Auth module is included so this can be added in the next phase. Phone provider enablement and Android app verification setup (SHA fingerprints / Play Integrity and reCAPTCHA fallback) are still required and must be tested on a real Android build.
- Existing reports, communities, and posts are still local AsyncStorage data. They have not yet been migrated to Firestore.
- No API server / Firebase Admin verification, Google Sheets sync, payment sandbox, or live payments have been connected yet.
- React Native Firebase uses native code and cannot run inside Expo Go. Build a custom development APK / EAS development build after installing dependencies.
- Package dependencies are declared in `artifacts/lineguard/package.json`. Run `pnpm install` from the workspace root to regenerate `pnpm-lock.yaml` before building. This environment could not reach the package registry, so dependency installation and typechecking were not run here.
- The `google-services.json` file is a client configuration file. Never put Firebase Admin service-account private keys in the APK or source repository.


## Phone OTP implementation (added)

The Android app now includes a native Firebase Phone Authentication screen at `artifacts/lineguard/app/auth/phone.tsx`. Users can request an SMS code, confirm the six-digit code, and create/read their own Firestore user profile after Firebase verifies the phone credential. Phone-only profiles store the verified E.164 phone number and a null email. The welcome screen and email sign-in screen link to this flow.

Before testing on a physical Android device, add the app's SHA-1 and SHA-256 signing certificate fingerprints in Firebase Console > Project settings > Your apps > Android app. For local testing, use Firebase Authentication > Sign-in method > Phone > Phone numbers for testing where available. Firebase Phone Auth also requires an appropriate Android app verification path (Play Integrity or reCAPTCHA fallback), a working device, and permitted SMS delivery. Merely enabling the Phone provider does not guarantee SMS delivery. A new native development build is required; Expo Go cannot load React Native Firebase native modules.

Phone OTP and email/password currently create/sign into Firebase identities independently. Account linking between an existing email identity and a phone identity is not implemented yet. Case data, server-side payment verification, Google Sheets sync, and a production backend remain unfinished.
