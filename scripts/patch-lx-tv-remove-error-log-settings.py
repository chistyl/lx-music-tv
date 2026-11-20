from pathlib import Path

target = Path("upstream/lx-music-mobile-auto-source/src/screens/Home/Views/Setting/settings/Other/index.tsx")
source = target.read_text(encoding="utf-8")

changes = [
    (
        "import Log from './Log'\n",
        "",
        "remove error log settings import",
    ),
    (
        "      <DislikeList />\n      <Log />",
        "      <DislikeList />",
        "remove complete error log settings section",
    ),
]

for old, new, label in changes:
    if old not in source:
        if new in source:
            print(f"Already applied: {label}")
            continue
        raise SystemExit(f"Expected source block not found: {label}")
    source = source.replace(old, new, 1)
    print(f"Applied: {label}")

target.write_text(source, encoding="utf-8")
print("Error log settings UI removed; underlying log utilities and other settings remain unchanged.")
