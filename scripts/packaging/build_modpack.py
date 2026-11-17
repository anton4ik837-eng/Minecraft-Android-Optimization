#!/usr/bin/env python3
"""Build an Android MCBBS modpack plus Ironized Zink and Turnip driver bundles."""
import argparse, hashlib, json, os, pathlib, sys, time, zipfile
import requests

MC = "1.21.1"
SEEDS = [
    "fabric-api",
    "sodium",
    "lithium",
    "ferrite-core",
    "immediatelyfast",
    "entityculling",
    "distanthorizons",
    "modmenu",
]
API = "https://api.modrinth.com/v2"
PUBLIC_HEADERS = {"User-Agent": "MinecraftAndroidOptimizationLab/0.1.0 (modpack builder)"}
HEADERS = dict(PUBLIC_HEADERS)
# Use the workflow token for GitHub API metadata only. Do not send it to
# browser_download_url redirects, which serve binary release assets.

if os.getenv("GITHUB_TOKEN"):
    HEADERS["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    HEADERS["X-GitHub-Api-Version"] = "2022-11-28"

def get_json(url, params=None):
    r = requests.get(url, params=params, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()

def latest_release(project):
    versions = get_json(f"{API}/project/{project}/version",
                        {"game_versions": json.dumps([MC]), "loaders": json.dumps(["fabric"])})
    candidates = [v for v in versions if v.get("version_type") == "release"]
    if not candidates:
        raise RuntimeError(f"No stable Fabric {MC} release found for {project}")
    return max(candidates, key=lambda v: v.get("date_published", ""))

def resolve_mods():
    resolved = {}
    pending = [("slug", slug) for slug in SEEDS]
    while pending:
        kind, value = pending.pop(0)
        if kind == "version":
            version = get_json(f"{API}/version/{value}")
        else:
            version = latest_release(value)
        project_id = version.get("project_id")
        if project_id in resolved:
            continue
        if MC not in version.get("game_versions", []) or "fabric" not in version.get("loaders", []):
            raise RuntimeError(f"Incompatible dependency selected: {version.get('name')}")
        resolved[project_id] = version
        for dep in version.get("dependencies", []):
            if dep.get("dependency_type") != "required":
                continue
            if dep.get("version_id"):
                pending.append(("version", dep["version_id"]))
            elif dep.get("project_id"):
                pending.append(("slug", dep["project_id"]))
    return list(resolved.values())

def download_mod(version, dest):
    files = version.get("files", [])
    jar_files = [f for f in files if f.get("filename", "").lower().endswith(".jar")]
    if not jar_files:
        raise RuntimeError(f"No JAR found for {version.get('name')}")
    file = next((f for f in jar_files if f.get("primary")), jar_files[0])
    target = dest / pathlib.Path(file["filename"]).name
    r = requests.get(file["url"], headers=HEADERS, timeout=180)
    r.raise_for_status()
    data = r.content
    expected = file.get("hashes", {}).get("sha512")
    actual = hashlib.sha512(data).hexdigest()
    if expected and actual.lower() != expected.lower():
        raise RuntimeError(f"SHA-512 mismatch for {file['filename']}")
    target.write_bytes(data)
    return {"project": version.get("name"), "version": version.get("version_number"),
            "filename": target.name, "sha512": actual, "source": file["url"]}

def fabric_loader_version():
    versions = get_json(f"https://meta.fabricmc.net/v2/versions/loader/{MC}")
    stable = [v["loader"]["version"] for v in versions if v.get("loader", {}).get("stable")]
    if not stable:
        raise RuntimeError("Fabric Meta did not return a stable loader for " + MC)
    return stable[0]

def write_modpack(out):
    stage = out / "stage"
    mods_dir = stage / "overrides" / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "manifestType": "minecraftModpack",
        "manifestVersion": 2,
        "name": "ULTRA-FPS Android",
        "version": "0.1.0",
        "author": "Minecraft Android Optimization Lab",
        "url": "https://github.com/anton4ik837-eng/Minecraft-Android-Optimization",
        "files": [],
        "settings": {
            "install_mods": True,
            "install_resourcepack": True
        },
        "launchInfo": {
            "minMemory": 4096,
            "supportJava": [21],
            "launchArgument": [],
            "javaArgument": []
        },
        "addons": [
            {"id": "game", "version": MC},
            {"id": "fabric", "version": fabric_loader_version()}
        ]
    }
    records = []
    for version in resolve_mods():
        records.append(download_mod(version, mods_dir))
    (stage / "mcbbs.packmeta").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    readme = """ULTRA-FPS Android — experimental test build
Minecraft Java 1.21.1 / Fabric / Java 21

Included: Fabric API, Sodium, Lithium, FerriteCore, ImmediatelyFast,
EntityCulling, Distant Horizons and Mod Menu (plus required dependencies).

Renderer is installed separately: use the Ironized Zink bundle.
Initial test is intentionally shader-free. Do not add Iris, shader packs,
Fresh Animations or HD resource packs until the first clean log is captured.

Zalith Launcher 2: import this ZIP as an MCBBS modpack. The archive contains
mcbbs.packmeta at its root and the game files under overrides/.
After import, select Ironized Zink in Settings > Renderer and choose its
Performance preset. The renderer package has separate instructions.

Status: EXPERIMENTAL / UNTESTED on the exact Lenovo Xiaoxin Pad Pro GT.
No FPS guarantee. Please retain latest.log and launcher logs after the first run.
"""
    (stage / "overrides" / "PACK-README.txt").write_text(readme, encoding="utf-8")
    (out / "ULTRA-FPS-1.21.1-MCBBS.zip").parent.mkdir(parents=True, exist_ok=True)
    pack_path = out / "ULTRA-FPS-1.21.1-MCBBS.zip"
    with zipfile.ZipFile(pack_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.write(stage / "mcbbs.packmeta", "mcbbs.packmeta")
        for p in sorted((stage / "overrides").rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(stage).as_posix())
    (out / "mod-list.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return pack_path, manifest, records

def write_renderer_bundle(out):
    api = "https://api.github.com/repos/GoyDevv/IronizedZink/releases/tags/v1.1.0"
    rel = get_json(api)
    assets = [a for a in rel.get("assets", []) if a.get("name", "").lower().endswith(".apk")]
    if not assets:
        raise RuntimeError("Ironized Zink v1.1.0 release has no APK asset")
    asset = assets[0]
    r = requests.get(asset["browser_download_url"], headers=PUBLIC_HEADERS, timeout=240)
    r.raise_for_status()
    apk = r.content
    tmp = out / "IronizedZink.apk"
    tmp.write_bytes(apk)
    sha = hashlib.sha256(apk).hexdigest()
    instructions = """IRONIZED ZINK 1.1.0 — Android renderer bundle
Target: Zalith Launcher 2 / Lenovo Xiaoxin Pad Pro GT / Snapdragon 8 Gen 3 / Adreno 750

INSTALL
1. Install IronizedZink.apk. Allow Android to install apps from this source if asked.
2. Open Ironized Zink once and grant the requested all-files/storage permission so its saved settings can be read by the game process.
3. In Zalith Launcher open Settings > Renderer and select Ironized Zink.
4. Open the Ironized Zink app and select the Performance preset.
5. Confirm: OpenGL 4.6; Threaded GL ON; Big-core affinity ON;
   Out-of-order drawing ON; No-error fast path OFF; VSync OFF;
   Shader disk cache ON; Single-file cache ON.
6. Leave Lazy descriptors and Inline uniforms OFF for the first diagnostic run.
7. Start the ULTRA-FPS MCBBS profile without Iris or shader packs.

IMPORTANT
- Do not enable No-error together with Out-of-order drawing.
- Do not enable Force software.
- This is OpenGL-over-Vulkan (Zink/Kopper), not native GLES.
- No measured FPS claim is made for this exact tablet.
- If the app's Performance preset values differ from this note, use the app UI;
  do not paste invented environment variables into the launcher.
- If the game crashes, switch back to the previous renderer and send both
  latest.log and the launcher log.

Source: https://github.com/GoyDevv/IronizedZink/releases/tag/v1.1.0
The APK is redistributed unchanged. SHA-256: """ + sha + "\n"
    source = {"project":"GoyDevv/IronizedZink","tag":"v1.1.0","asset":asset["name"],"url":asset["browser_download_url"],"sha256":sha}
    zip_path = out / "IRONIZED-ZINK-1.1.0-ADRENO750.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.write(tmp, "IronizedZink.apk")
        z.writestr("README-RU.txt", instructions)
        z.writestr("source.json", json.dumps(source, ensure_ascii=False, indent=2))
    tmp.unlink()
    return zip_path, source


def write_turnip_bundle(out):
    # Publish a verified source/download pointer instead of repacking an upstream
    # binary whose GitHub asset endpoint is returning HTML to the runner.
    repo = "JustCallMeJade/Drivers_Android_Mesa"
    tag = "v26.3.0-V5.0"
    rel = get_json(f"https://api.github.com/repos/{repo}/releases/tags/{tag}")
    assets = [a for a in rel.get("assets", []) if a.get("name", "").lower().endswith(".zip")]
    if not assets:
        raise RuntimeError(f"No ZIP driver asset listed in {repo} {tag}")
    asset = assets[0]
    source_url = asset["browser_download_url"]
    instructions = """TURNIP 26.3.0-V5.0 — Adreno 750
Status: EXPERIMENTAL / not tested on the exact Lenovo Xiaoxin Pad Pro GT.

The upstream release explicitly lists Adreno 750 as supported.
This release asset is provided as an official download link; the driver binary
is hosted by its original publisher and is not repacked into this information ZIP.

OFFICIAL DRIVER DOWNLOAD
""" + source_url + """

INSTALL
1. Download the original ZIP from the official link above.
2. In Zalith Launcher, open its GPU/Vulkan driver management screen.
3. Import the ZIP only if your installed launcher build supports this driver format.
4. Select Turnip for the Minecraft profile and restart the game.
5. If there is no custom-driver import option, do not install libraries manually
   into Android system folders.

IMPORTANT
- Turnip is a Vulkan driver, not a Minecraft renderer or mod.
- Ironized Zink bundles its own Mesa components; Turnip may not replace the
  Mesa version used internally by Zink.
- Keep the previous driver available for rollback. No FPS improvement is promised.

Upstream release: https://github.com/JustCallMeJade/Drivers_Android_Mesa/releases/tag/v26.3.0-V5.0
Original asset: """ + asset["name"] + """
"""
    source = {"project": repo, "tag": tag, "asset": asset["name"],
              "url": source_url, "gpu_support_claim": "Adreno 750",
              "binary_included": False}
    bundle = out / "TURNIP-26.3.0-V5.0-ADRENO750-INFO.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("README-RU.txt", instructions)
        z.writestr("source.json", json.dumps(source, ensure_ascii=False, indent=2))
    return bundle, source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    out = pathlib.Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    pack, manifest, mods = write_modpack(out)
    renderer, source = write_renderer_bundle(out)
    turnip, turnip_source = write_turnip_bundle(out)
    print(json.dumps({"modpack": str(pack), "renderer": str(renderer), "turnip": str(turnip),
                      "loader": manifest["addons"][1]["version"],
                      "mods": mods, "renderer_source": source, "turnip_source": turnip_source}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
