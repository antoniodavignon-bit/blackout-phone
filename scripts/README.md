# Field scripts

These live on the device in `$PREFIX/bin` and are the entire daily interface.

| Command | Does |
|---|---|
| `cap "…"` | Timestamps a note into the capture inbox. Offline. |
| `vs "…"` | Full-text search across the notes vault. |
| `ask "…"` | Runs the local model on a bounded text task. |
| `home` | rsync the inbox to the Mac when a network returns. |

Committed here as they are written and tested on hardware — see the phase docs for the current state.
