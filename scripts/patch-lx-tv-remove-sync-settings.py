from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source/src/screens/Home/Views/Setting")


def replace_once(path: str, old: str, new: str, label: str) -> None:
    target = ROOT / path
    source = target.read_text(encoding="utf-8")
    if old not in source:
        if new in source:
            print(f"Already applied: {label}")
            return
        raise SystemExit(f"Expected source block not found: {label} ({path})")
    target.write_text(source.replace(old, new, 1), encoding="utf-8")
    print(f"Applied: {label}")


# Remove only the Data Sync entry from the settings navigation and its rendered panels.
# Keep sync services and all unrelated settings/features untouched.
replace_once(
    "Main.tsx",
    "import Sync from './settings/Sync'\n",
    "",
    "remove Data Sync settings import",
)
replace_once(
    "Main.tsx",
    "  'list',\n  'sync',\n  'backup',",
    "  'list',\n  'backup',",
    "remove Data Sync from settings navigation",
)
replace_once(
    "Main.tsx",
    "      case 'list': return <List />\n      case 'sync': return <Sync />\n      case 'backup': return <Backup />",
    "      case 'list': return <List />\n      case 'backup': return <Backup />",
    "remove Data Sync settings panel",
)
replace_once(
    "Vertical/Main.tsx",
    "import Sync from '../settings/Sync'\n",
    "",
    "remove Data Sync vertical settings import",
)
replace_once(
    "Vertical/Main.tsx",
    "    case 'list': return <List />\n    case 'sync': return <Sync />\n    case 'backup': return <Backup />",
    "    case 'list': return <List />\n    case 'backup': return <Backup />",
    "remove Data Sync vertical settings panel",
)

print("Data Sync removed from the settings UI; other settings and sync internals are unchanged.")
