# LX Music TV upstream baseline

## Selected upstream

- Repository: https://github.com/shellsec/lx-music-mobile-auto-source
- Branch: `main`
- Pinned commit: `b51debddf09a0d3e20084f59ddbed256d0b455c9`
- License: Apache-2.0 (retain upstream LICENSE, NOTICE, and copyright notices)
- Application stack: React Native `0.73.11`, React `18.2.0`
- Android application identity in upstream: `LX Music`

This is the selected application source of truth. Do not replace its screens, navigation, player, lyric rendering, source runtime, or data model with a newly invented native implementation.

## TV adaptation requirements

1. Preserve the upstream mobile application's feature set, visual language, and interaction flows.
2. Adapt focus, directional navigation, Back handling, and focus visibility for Android TV remote control.
3. Keep source management user-driven. A fresh installation must not bundle third-party source scripts.
4. Do not impose a global platform allow-list on imported source scripts. A source may expose the platforms/actions it declares itself.
5. Remove application version-check, update prompts, and in-app update/download flows.
6. Remove source-subscription catalog updates and automatic subscription recovery/update flows. Do not remove local source import, source selection, source ordering, or source deletion.
7. Keep the upstream Apache-2.0 license and attribution notices.

## Porting guardrails

- The selected upstream is React Native, not the previous Kotlin/QuickJS prototype.
- The previous `feature/lx-mobile-original-ui-r1` Kotlin implementation is not the new application base.
- Do not claim Android TV/D-pad compatibility until the relevant navigation behavior has been implemented and tested.
- Do not mark an APK as accepted until CI artifacts are generated and the user has tested it on the target TV.

## Initial implementation sequence

1. Bring the pinned upstream application source into this project without redesigning it.
2. Establish a reproducible Android build from that source.
3. Remove update and subscription-update paths while preserving local source import and the upstream script runtime.
4. Add Android TV remote focus and navigation support incrementally, screen by screen.
5. Build and deliver both the APK and complete source ZIP.
