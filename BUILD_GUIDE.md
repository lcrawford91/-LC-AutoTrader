# Build LC AutoTrader APK

This is a **UI scaffold**, not a functioning brokerage trading client. Live trading is disabled at build time and no broker credentials or order execution are implemented.

1. Upload the **contents** of this folder to the root of your GitHub repository (not the enclosing folder).
2. Open GitHub > Actions > Build Android APK > Run workflow.
3. Wait for the build to succeed, then open its Artifacts section and download `LC-AutoTrader-debug-apk`.
4. Extract the artifact ZIP and install `app-debug.apk` on Android after reviewing the source.

The workflow installs Gradle 8.9 through GitHub Actions, so no Gradle wrapper JAR is required. Android SDK components are installed by the Android Gradle plugin as needed. The test task is an Android JUnit test, not Python pytest; do not run pytest against this Android-only project.

A passing build is not evidence that live order execution, account authentication, market data, or risk management have been implemented. Do not enter exchange secrets into this app.


## GitHub Actions repair (November 2026)

Upload the **extracted files and directories** to the repository root, not the ZIP itself.
This project uses GitHub Actions `gradle/actions/setup-gradle@v4` to install Gradle 8.9,
so it does **not** require a `gradlew` file or wrapper JAR.

The workflow installs Java 17 and Android SDK 35, runs `testDebugUnitTest`,
builds `assembleDebug`, then uploads the APK artifact.

On GitHub, go to **Actions > Build Android APK > Run workflow**.
After a successful run, download the `LC-AutoTrader-debug-apk` artifact.

**Safety:** `LIVE_TRADING_ENABLED` is false. No live orders or exchange credentials
are included. An APK build does not mean live trading is implemented.

**Validation limitation:** The workflow has been checked structurally, but
the APK has not been compiled in this environment.
