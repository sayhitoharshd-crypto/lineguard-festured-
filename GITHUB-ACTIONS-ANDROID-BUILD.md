# Build LineGuard Android APK with GitHub Actions

The canonical workflow is `.github/workflows/android-apk.yml`.

## Run it

1. Create or open a GitHub repository for this project.
2. Upload the **contents** of this source archive to the repository root. Do not put the whole project inside an extra nested folder. The root must contain `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `package.json`, `artifacts/`, `lib/`, and `.github/`.
3. Push the files to the `main` branch.
4. In GitHub, open **Actions → Build LineGuard Android APK → Run workflow**. It also runs on pushes to `main` when app or dependency files change.
5. Wait for the workflow to finish. Open the successful run, scroll to **Artifacts**, and download `LineGuard-standalone-release-APK`.
6. Extract that artifact. It contains `LineGuard-release.apk` and `SHA256SUMS.txt`.

## Optional GitHub secret

Add repository secret `EXPO_PUBLIC_API_URL` if the app needs a production API URL at build time. Set it to the deployed HTTPS API base URL. Do not put Firebase Admin credentials, payment secrets, or service-account private keys in `EXPO_PUBLIC_*` variables.

The project includes `artifacts/lineguard/google-services.json` for Firebase Android configuration. Confirm it belongs to the intended Firebase project and has the Android package `com.lineguard.app` before using the APK with real accounts.

## What the workflow does

- Uses Node.js 22, pnpm 10, Java 17, and Android SDK.
- Installs the exact workspace lockfile dependencies.
- Runs the app TypeScript check.
- Generates the native Android project with Expo prebuild.
- Runs Gradle `assembleRelease`.
- Checks that the APK exists, includes the embedded JavaScript bundle, and has application ID `com.lineguard.app`.
- Calculates SHA-256 and uploads the APK plus checksum as a GitHub Actions artifact.

## Signing

This workflow does not configure a private Play Store upload key. Expo/React Native's generated Gradle release configuration may use the default debug signing configuration unless a release signing setup is added. Treat the resulting APK as an installable test build, not a Play Store production-signed release.

## If the workflow fails

Open the failed workflow run and inspect the first failing step. Dependency, TypeScript, Expo prebuild, and Gradle errors must be fixed before an APK can be considered built. A successful workflow artifact is the actual APK; the workflow file itself is not an APK.
