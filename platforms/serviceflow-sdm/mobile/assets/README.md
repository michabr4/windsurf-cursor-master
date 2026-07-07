# Mobile assets

`app.json` no longer references these paths by default (Expo built-in icon/splash). Add files here when preparing a **production** mobile release, then wire paths back into `app.json`:

| File | Purpose |
| --- | --- |
| `icon.png` | App icon (1024×1024 recommended) |
| `splash.png` | Splash screen (1284×2778 or similar) |
| `adaptive-icon.png` | Android adaptive icon foreground (1024×1024) |

Optional **48×48 dev placeholders** in this folder can be used while developing asset wiring; replace with full-resolution brand assets before store submission.
