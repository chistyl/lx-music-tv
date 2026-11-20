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
    ...(theme.id === 'black' ? {
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
    } : {}),
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



patch_theme()
patch_shared_button_focus()
patch_legacy_focus_styles()
print("Applied black/navy theme tokens and shape-preserving soft focus across TV controls and lists.")
