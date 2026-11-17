# Ironized Zink 1.1.0 — Adreno 750 profile

**Status:** Experimental / untested on the exact Lenovo Xiaoxin Pad Pro GT.

- Plugin: [GoyDevv/IronizedZink v1.1.0](https://github.com/GoyDevv/IronizedZink/releases/tag/v1.1.0)
- Renderer path: Mesa Zink + Kopper, desktop OpenGL over Vulkan
- Launcher support declared by upstream: Zalith Launcher 2 family and Fold Craft Launcher family
- GPU requirement: Vulkan 1.1+

## First diagnostic preset

Use the app's **Performance** preset. Confirm in its UI:
- OpenGL 4.6
- Threaded GL: ON
- Big-core affinity: ON
- Out-of-order drawing: ON
- No-error fast path: OFF
- VSync: OFF
- Shader disk cache: ON
- Single-file cache: ON
- Lazy descriptors: OFF for the first run
- Inline uniforms: OFF for the first run
- Force software: OFF

Do not enable No-error together with Out-of-order drawing. Do not force software rendering.

Install the APK from the separate GitHub Release asset `IRONIZED-ZINK-1.1.0-ADRENO750.zip`. Grant its requested storage permission, then select Ironized Zink in Zalith's renderer settings.

This is a reproducible starting configuration, not a benchmark result. Zink translates OpenGL to Vulkan and may not outperform a native GLES path on every device.
