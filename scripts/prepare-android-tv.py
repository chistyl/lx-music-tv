#!/usr/bin/env python3
"""Apply Android TV manifest declarations to the pinned LX Music Android project."""
from pathlib import Path
import xml.etree.ElementTree as ET

manifest = Path("upstream/lx-music-mobile-auto-source/android/app/src/main/AndroidManifest.xml")
ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
ET.register_namespace("tools", "http://schemas.android.com/tools")
android = "{http://schemas.android.com/apk/res/android}"

tree = ET.parse(manifest)
root = tree.getroot()

def ensure_feature(name: str, required: str) -> None:
    for node in root.findall("uses-feature"):
        if node.get(android + "name") == name:
            node.set(android + "required", required)
            return
    node = ET.Element("uses-feature")
    node.set(android + "name", name)
    node.set(android + "required", required)
    root.insert(0, node)

# TV devices do not necessarily have a touchscreen; retain phone/tablet compatibility.
ensure_feature("android.hardware.touchscreen", "false")
ensure_feature("android.software.leanback", "true")

app = root.find("application")
if app is None:
    raise SystemExit("AndroidManifest.xml has no application element")

activity = app.find("activity")
if activity is None:
    raise SystemExit("AndroidManifest.xml has no launcher activity")

activity.set(android + "screenOrientation", "landscape")
launcher = False
for intent in activity.findall("intent-filter"):
    actions = {x.get(android + "name") for x in intent.findall("action")}
    categories = {x.get(android + "name") for x in intent.findall("category")}
    if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in categories:
        category = ET.SubElement(intent, "category")
        category.set(android + "name", "android.intent.category.LEANBACK_LAUNCHER")
        launcher = True
        break
if not launcher:
    raise SystemExit("Could not find the MAIN/LAUNCHER intent filter")

tree.write(manifest, encoding="utf-8", xml_declaration=True)
print("Android TV manifest configured: Leanback launcher, landscape, no touchscreen requirement.")
