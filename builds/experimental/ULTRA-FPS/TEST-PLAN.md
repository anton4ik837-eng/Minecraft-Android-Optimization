# First-run test plan

1. Import `ULTRA-FPS-1.21.1-MCBBS.zip` in Zalith Launcher 2.
2. Install the separate Ironized Zink 1.1.0 bundle and select the Performance preset.
3. Keep Iris, shaders and resource packs disabled.
4. Launch a new single-player world. Stand still for 60 seconds, then travel into unexplored terrain for 2 minutes.
5. Exit normally and collect:
   - `.minecraft/logs/latest.log`
   - `.minecraft/crash-reports/*` if a crash occurred
   - Zalith launcher log/export
   - F3 screenshot showing renderer, OpenGL version and FPS
6. Record device temperature, battery/performance mode, render distance and DH distance.

Do not change multiple renderer settings between runs. Preserve the first-run logs unchanged.
