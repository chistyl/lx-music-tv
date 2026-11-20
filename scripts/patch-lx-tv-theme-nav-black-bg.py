from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        if new in source:
            return source
        raise SystemExit(f"Could not locate patch anchor: {label}")
    return source.replace(old, new, 1)


# 1) Top-level navigation: selected item gets a persistent, complete theme-color tile.
aside = ROOT / "src/screens/Home/Horizontal/Aside.tsx"
source = aside.read_text(encoding="utf-8")
source = replace_once(
    source,
    "style={[styles.menuItem, active ? styles.activeItem : undefined, focused ? styles.focusedItem : undefined]}",
    "style={[styles.menuItem, active ? styles.activeItem : undefined]}",
    "keep navigation focus visuals unchanged",
)
source = replace_once(
    source,
    "  menuList: {\n    flex: 1,",
    "  menuList: {\n    flex: 1,\n    paddingVertical: 8,\n    overflow: 'visible',",
    "keep complete selected tile within navigation row",
)
source = replace_once(
    source,
    "    minWidth: 0,",
    "    minWidth: 0,\n    flexShrink: 0,",
    "prevent navigation item width compression",
)
# Requested refinement only: reduce the selected tile height and horizontal padding; keep nav icon size unchanged.
source = replace_once(
    source,
    "    height: 44,\n    paddingHorizontal: 8,",
    "    height: 34,\n    paddingHorizontal: 6,",
    "reduce top navigation selected tile height and width",
)
source = replace_once(
    source,
    "<Icon name={icon} size={20} color={active ? theme['c-primary-font-active'] : theme['c-font-label']} />",
    "<Icon name={icon} size={18} color={active ? theme['c-primary-font-active'] : theme['c-font-label']} />",
    "slightly reduce top navigation icon size",
)
aside.write_text(source, encoding="utf-8")


# 2) Black theme only: use solid #141414 for the content background used by the
# top navigation and home player. All other themes retain their original value.
theme_file = ROOT / "src/theme/themes/index.ts"
source = theme_file.read_text(encoding="utf-8")
source = replace_once(
    source,
    "'c-content-background': theme.config.themeColors['c-primary-light-1000'],",
    "'c-content-background': theme.id === 'black' ? '#141414' : theme.config.themeColors['c-primary-light-1000'],",
    "black theme content background",
)
theme_file.write_text(source, encoding="utf-8")

print("Applied only the requested top-navigation selected tile height and icon size refinements.")
