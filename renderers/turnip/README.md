# Turnip 26.3.0-V5.0 — Adreno 750

**Status:** Experimental / not yet tested on the exact Lenovo Xiaoxin Pad Pro GT.

- Upstream package: [JustCallMeJade/Drivers_Android_Mesa v26.3.0-V5.0](https://github.com/JustCallMeJade/Drivers_Android_Mesa/releases/tag/v26.3.0-V5.0)
- GPU support list in the upstream release explicitly includes Adreno 750.
- Package type: AdrenoTools-compatible Android Vulkan driver package.
- Turnip is a Vulkan driver, not a Minecraft renderer or mod.

## Installation

1. Open Zalith Launcher's GPU/Vulkan driver management screen.
2. Import the supplied package from the GitHub Release if the installed Zalith build exposes AdrenoTools/custom driver import.
3. Select Turnip for the Minecraft profile and restart the game.
4. If there is no custom-driver import option, do not install the library manually into Android system folders.

## Compatibility notes

- The upstream GPU list is not proof of testing on this exact tablet.
- Ironized Zink 1.1.0 bundles its own Mesa components. Selecting a separate Turnip driver may not replace the Mesa version used internally by Zink.
- Test Turnip separately with a Vulkan-based backend. Keep the previous driver available for rollback.
- Compare identical worlds and settings; do not assume a higher Mesa version means higher FPS.

Source release: https://github.com/JustCallMeJade/Drivers_Android_Mesa/releases/tag/v26.3.0-V5.0
