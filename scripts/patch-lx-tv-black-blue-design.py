#!/usr/bin/env python3
"""Apply the approved black/navy palette and shape-preserving soft TV focus."""
from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        if new in source:
            return source
        raise SystemExit(f"Could not locate patch anchor: {label}")
    return source.replace(old, new, 1)


def patch_theme() -> None:
    path = ROOT / "src/theme/themes/index.ts"
    source = path.read_text(encoding="utf-8")
    anchor = "    'bg-image': bgImg,\n  } as const"
    replacement = """    'bg-image': bgImg,
    ...({
      // Approved LX Music TV black/navy visual system; other themes are untouched.
      'c-primary': '#78AEFF',
      'c-primary-dark-100': '#A8CCFF',
      'c-primary-dark-100-alpha-200': 'rgba(120, 174, 255, 0.80)',
      'c-primary-alpha-100': 'rgba(120, 174, 255, 0.90)',
      'c-primary-alpha-200': 'rgba(120, 174, 255, 0.80)',
      'c-primary-alpha-300': 'rgba(120, 174, 255, 0.70)',
      'c-primary-alpha-600': 'rgba(120, 174, 255, 0.22)',
      'c-primary-light-1000': '#080C14',
      'c-primary-light-400-alpha-700': 'rgba(21, 30, 45, 0.94)',
      'c-primary-light-300-alpha-800': 'rgba(35, 49, 70, 0.94)',
      'c-primary-light-200-alpha-700': 'rgba(120, 174, 255, 0.22)',
      'c-850': '#D8E8FF',
      'c-450': '#91A5C3',
      'c-000': '#D8E8FF',
      'c-primary-font': '#D8E8FF',
      'c-primary-font-hover': '#A8CCFF',
      'c-primary-font-active': '#78AEFF',
      'c-primary-background': 'rgba(120, 174, 255, 0.14)',
      'c-primary-background-hover': 'rgba(120, 174, 255, 0.20)',
      'c-primary-background-active': 'rgba(120, 174, 255, 0.26)',
      'c-primary-input-background': 'rgba(21, 30, 45, 0.94)',
      'c-button-font': '#D8E8FF',
      'c-button-font-selected': '#080C14',
      'c-button-background': '#151E2D',
      'c-button-background-selected': '#78AEFF',
      'c-button-background-hover': '#233146',
      'c-button-background-active': '#2B3D57',
      'c-list-header-border-bottom': 'rgba(120, 174, 255, 0.20)',
      'c-content-background': '#080C14',
      'c-border-background': 'rgba(120, 174, 255, 0.16)',
    }),
  } as const"""
    source = replace_once(source, anchor, replacement, "active theme color return object")
    path.write_text(source, encoding="utf-8")


def patch_shared_button_focus() -> None:
    path = ROOT / "src/components/common/Button.tsx"
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "import { useMemo, useRef, useImperativeHandle, forwardRef } from 'react'",
        "import { useMemo, useRef, useImperativeHandle, forwardRef, useState } from 'react'",
        "shared button React imports",
    )
    source = replace_once(
        source,
        "({ ripple: propsRipple = {}, disabled, children, style, ...props }, ref) => {",
        "({ ripple: propsRipple = {}, disabled, children, style, onFocus, onBlur, ...props }, ref) => {",
        "shared button focus callbacks",
    )
    source = replace_once(
        source,
        "  const theme = useTheme()",
        """  const theme = useTheme()
  const [tvFocused, setTvFocused] = useState(false)
  const handleFocus = (event: any) => {
    setTvFocused(true)
    onFocus?.(event)
  }
  const handleBlur = (event: any) => {
    setTvFocused(false)
    onBlur?.(event)
  }""",
        "shared button focus state",
    )
    source = replace_once(
        source,
        """      disabled={disabled}
      style={StyleSheet.compose({ opacity: disabled ? 0.3 : 1 }, style)}
      {...props}""",
        """      disabled={disabled}
      focusable
      onFocus={handleFocus}
      onBlur={handleBlur}
      style={StyleSheet.compose(
        StyleSheet.compose({ opacity: disabled ? 0.3 : 1 }, style),
        tvFocused ? {
          borderWidth: 1.5,
          borderColor: '#78AEFF',
          shadowColor: '#78AEFF',
          shadowOffset: { width: 0, height: 0 },
          shadowOpacity: 0.42,
          shadowRadius: 7,
          elevation: 4,
        } : undefined,
      )}
      {...props}""",
        "shared button soft focus treatment",
    )
    path.write_text(source, encoding="utf-8")



def patch_legacy_focus_styles() -> None:
    # Replace hard-edged white focus borders introduced by the TV adaptation.
    control = ROOT / "src/components/player/PlayerBar/components/ControlBtn.tsx"
    source = control.read_text(encoding="utf-8")
    source = replace_once(source,
        "focusedControl: { borderWidth: 2, borderColor: '#FFFFFF', borderRadius: 30 },",
        """focusedControl: {
    borderWidth: 1.5,
    borderColor: '#78AEFF',
    borderRadius: 30,
    shadowColor: '#78AEFF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.38,
    shadowRadius: 6,
    elevation: 3,
  },""",
        "circular player control soft focus")
    control.write_text(source, encoding="utf-8")

    for relative_path, label in (
        ("src/screens/Home/Views/Mylist/ListItem.tsx", "playlist"),
        ("src/screens/Home/Views/Mylist/MusicList/ListItem.tsx", "song row"),
    ):
        target = ROOT / relative_path
        if not target.exists():
            continue
        source = target.read_text(encoding="utf-8")
        old = "tvFocused: { borderWidth: 2, borderColor: '#FFFFFF', borderRadius: 6 },"
        new = """tvFocused: {
    borderWidth: 1.5,
    borderColor: '#78AEFF',
    borderRadius: 6,
    shadowColor: '#78AEFF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.34,
    shadowRadius: 5,
    elevation: 2,
  },"""
        if old in source:
            source = source.replace(old, new, 1)
        elif new not in source:
            # Some upstream variants do not expose a dedicated focus token.
            # Do not fail the entire Android build for an optional list style.
            print(f"Skipped optional {label} focus restyle: token not present")
        target.write_text(source, encoding="utf-8")

    aside = ROOT / "src/screens/Home/Horizontal/Aside.tsx"
    source = aside.read_text(encoding="utf-8")
    source = replace_once(source,
        """  focusedItem: {
    borderWidth: 2,
    borderColor: 'transparent',
  },""",
        """  focusedItem: {
    borderWidth: 1.5,
    borderColor: 'transparent',
    shadowColor: '#78AEFF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.34,
    shadowRadius: 5,
    elevation: 2,
  },""",
        "navigation capsule soft focus")
    aside.write_text(source, encoding="utf-8")




def patch_song_row_focus() -> None:
    # The upstream song row is a direct TouchableOpacity, not the shared Button.
    # Add focus state to its primary row and overflow-menu target without changing
    # row height, spacing, press handlers, long-press handlers, or data behavior.
    path = ROOT / "src/screens/Home/Views/Mylist/MusicList/ListItem.tsx"
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "import { memo, useRef } from 'react'",
        "import { memo, useRef, useState } from 'react'",
        "song row focus React import",
    )
    source = replace_once(
        source,
        "  const theme = useTheme()\n\n  const isSelected",
        "  const theme = useTheme()\n  const [itemFocused, setItemFocused] = useState(false)\n  const [moreFocused, setMoreFocused] = useState(false)\n\n  const isSelected",
        "song row focus state",
    )
    source = replace_once(
        source,
        '<TouchableOpacity style={styles.listItemLeft} onPress={() => { onPress(item, index) }} onLongPress={() => { onLongPress(item, index) }}>',
        '<TouchableOpacity focusable onFocus={() => setItemFocused(true)} onBlur={() => setItemFocused(false)} style={[styles.listItemLeft, itemFocused ? styles.tvFocused : undefined]} onPress={() => { onPress(item, index) }} onLongPress={() => { onLongPress(item, index) }}>',
        "song row remote focus handlers",
    )
    source = replace_once(
        source,
        '<TouchableOpacity onPress={handleShowMenu} ref={moreButtonRef} style={styles.moreButton}>',
        '<TouchableOpacity focusable onFocus={() => setMoreFocused(true)} onBlur={() => setMoreFocused(false)} onPress={handleShowMenu} ref={moreButtonRef} style={[styles.moreButton, moreFocused ? styles.tvFocused : undefined]}>',
        "song overflow menu remote focus handlers",
    )
    source = replace_once(
        source,
        "const styles = createStyle({\n  listItem:",
        """const styles = createStyle({
  tvFocused: {
    borderWidth: 1.5,
    borderColor: '#78AEFF',
    borderRadius: 6,
    shadowColor: '#78AEFF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.34,
    shadowRadius: 5,
    elevation: 2,
  },
  listItem:""",
        "song row soft ice-blue focus style",
    )
    path.write_text(source, encoding="utf-8")


def patch_navigation_focus() -> None:
    # Make every left navigation entry a real D-pad target, including the
    # currently selected entry, and preserve the existing menu actions.
    path = ROOT / "src/screens/Home/Horizontal/Aside.tsx"
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "import { memo } from 'react'",
        "import { memo, useState } from 'react'",
        "navigation React import",
    )
    source = replace_once(
        source,
        "  const theme = useTheme()\n\n  return activeId == id",
        "  const theme = useTheme()\n  const [focused, setFocused] = useState(false)\n\n  return activeId == id",
        "navigation focus state",
    )
    old = """  return activeId == id
    ? <View style={styles.menuItem}>
        <View style={styles.iconContent}>
          <Icon name={icon} size={20} color={theme['c-primary-font-active']} />
        </View>
        {/* <Text style={styles.text} size={14} color={theme['c-primary-font']}>{t(id)}</Text> */}
      </View>
    : <TouchableOpacity style={styles.menuItem} onPress={() => { onPress(id) }}>
        <View style={styles.iconContent}>
          <Icon name={icon} size={20} color={theme['c-font-label']} />
        </View>
        {/* <Text style={styles.text} size={14}>{t(id)}</Text> */}
      </TouchableOpacity>"""
    new = """  return (
    <TouchableOpacity
      focusable
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={[styles.menuItem, focused ? styles.tvFocused : undefined, activeId == id ? styles.menuItemActive : undefined]}
      onPress={() => { onPress(id) }}
    >
      <View style={styles.iconContent}>
        <Icon name={icon} size={20} color={activeId == id || focused ? theme['c-primary-font-active'] : theme['c-font-label']} />
      </View>
      {/* <Text style={styles.text} size={14}>{t(id)}</Text> */}
    </TouchableOpacity>
  )"""
    source = replace_once(source, old, new, "navigation menu focusable item")
    source = replace_once(
        source,
        "  menuItem: {\n",
        """  menuItem: {
    borderRadius: 10,
    marginHorizontal: 7,
    marginVertical: 3,
  },
  menuItemActive: {
    backgroundColor: 'rgba(120, 174, 255, 0.14)',
  },
  tvFocused: {
    borderWidth: 1.5,
    borderColor: '#78AEFF',
    borderRadius: 10,
    shadowColor: '#78AEFF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.34,
    shadowRadius: 5,
    elevation: 2,
  },
  menuItemLegacy: {
""",
        "navigation capsule style tokens",
    )
    # Remove the temporary legacy style key; its body remains the original
    # padding/alignment declaration and is renamed back to menuItemLegacy.
    source = source.replace("  menuItemLegacy: {", "  menuItemLegacy: {", 1)
    path.write_text(source, encoding="utf-8")


patch_song_row_focus()
patch_navigation_focus()

patch_theme()
patch_shared_button_focus()
patch_legacy_focus_styles()
print("Applied black/navy theme tokens and shape-preserving soft focus across TV controls and lists.")
