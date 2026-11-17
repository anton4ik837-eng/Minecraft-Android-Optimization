# ULTRA-FPS Android 0.1.0

- Minecraft: **1.21.1**
- Loader: Fabric (stable loader selected by Fabric Meta at build time)
- Java: **21**
- Renderer: **Ironized Zink 1.1.0** (separate bundle)
- Target: Lenovo Xiaoxin Pad Pro GT / Snapdragon 8 Gen 3 / Adreno 750
- Status: **Experimental / Untested** on the exact device

The MCBBS archive is built by `scripts/packaging/build_modpack.py` and published as a GitHub Release asset. It contains the MCBBS root metadata and the mods under `overrides/mods/`.

The initial pack deliberately excludes Iris, shaders, Fresh Animations and HD resource packs. First capture a clean baseline log with the renderer and core performance mods; add visual components only after confirming stability.

Do not treat expected performance as measured performance. The 400+ FPS target is aspirational, not a guarantee.
