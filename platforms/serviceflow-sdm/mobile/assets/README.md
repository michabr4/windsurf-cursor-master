# Mobile assets

Expo expects these files (see `mobile/app.json`):

| File | Purpose |
| --- | --- |
| `icon.png` | App icon (1024×1024 recommended for store builds) |
| `splash.png` | Splash screen (1284×2778 or similar; `resizeMode: contain`) |
| `adaptive-icon.png` | Android adaptive icon foreground (1024×1024) |

## Before `expo run` or EAS Build

Add real PNGs here. **Expo Go** may start without custom assets in some setups, but `expo prebuild` / store builds will fail if these paths are missing.

Committed **48×48 dev placeholders** (`icon.png`, `splash.png`, `adaptive-icon.png`) unblock `expo prebuild` locally. Replace with full-resolution brand assets before App Store / Play Store submission.
