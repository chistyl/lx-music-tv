# LX Music TV R1 — Apple Music Edition

## Baseline
- Upstream: bmizhou/lx-music-tv
- Fork: chistyl/lx-music-tv
- Base commit: 73f3b4db986be9b28f711e9d5bd7816d7d3b46f5
- Branch: feature/apple-music-tv-r1-android9

## R1 decisions
- Minimum Android version: Android 9 / API 28.
- Design direction: Apple Music-inspired dark interface, pure-black canvas, graphite surfaces, Apple Music red accent.
- Keep the existing Kotlin + Jetpack Compose for TV architecture and ExoPlayer playback/data services.
- Preserve existing search, music sources, favorites, lyrics, cache, and background playback while replacing presentation incrementally.

## First implementation slice
- Set minSdk to 28 and increment app version to 1.0.0-r1-apple-music.
- Establish the Apple Music dark palette in the shared Compose theme.
- Keep light mode and alternate accent presets available for regression safety.
- Next: rebuild TV home navigation/content hierarchy and player screen for remote-first operation.

## Validation
- Build debug and release APKs.
- Verify API 28 install/launch and remote focus navigation on an Android 9 TV.
- Verify audio playback, background service, lyric sync, and search/source flows.
