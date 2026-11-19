#!/usr/bin/env python3
"""Patch shared LX Music Pressable controls with visible Android TV focus state."""
from pathlib import Path

target = Path("upstream/lx-music-mobile-auto-source/src/components/common/Button.tsx")
source = target.read_text(encoding="utf-8")

old_import = "import { useMemo, useRef, useImperativeHandle, forwardRef } from 'react'"
new_import = "import { useMemo, useRef, useImperativeHandle, forwardRef, useState } from 'react'"
if old_import not in source:
    if new_import not in source:
        raise SystemExit("Unexpected Button.tsx React import; refusing unsafe patch")
else:
    source = source.replace(old_import, new_import, 1)

old_sig = "({ ripple: propsRipple = {}, disabled, children, style, ...props }, ref) => {"
new_sig = "({ ripple: propsRipple = {}, disabled, children, style, onFocus, onBlur, ...props }, ref) => {"
if old_sig not in source:
    if new_sig not in source:
        raise SystemExit("Unexpected Button.tsx component signature; refusing unsafe patch")
else:
    source = source.replace(old_sig, new_sig, 1)

anchor = "  const theme = useTheme()\n"
focus_state = """  const theme = useTheme()
  const [tvFocused, setTvFocused] = useState(false)
  const handleFocus = (event: any) => {
    setTvFocused(true)
    onFocus?.(event)
  }
  const handleBlur = (event: any) => {
    setTvFocused(false)
    onBlur?.(event)
  }
"""
if focus_state not in source:
    if anchor not in source:
        raise SystemExit("Unexpected Button.tsx theme anchor; refusing unsafe patch")
    source = source.replace(anchor, focus_state, 1)

old_pressable = """      disabled={disabled}
      style={StyleSheet.compose({ opacity: disabled ? 0.3 : 1 }, style)}
      {...props}
"""
new_pressable = """      disabled={disabled}
      focusable
      onFocus={handleFocus}
      onBlur={handleBlur}
      style={StyleSheet.compose(
        StyleSheet.compose({ opacity: disabled ? 0.3 : 1 }, style),
        tvFocused ? { borderWidth: 2, borderColor: theme['c-primary-font-active'], borderRadius: 6 } : undefined,
      )}
      {...props}
"""
if old_pressable in source:
    source = source.replace(old_pressable, new_pressable, 1)
elif new_pressable not in source:
    raise SystemExit("Unexpected Button.tsx Pressable block; refusing unsafe patch")

target.write_text(source, encoding="utf-8")
print("Android TV focus support applied to shared Pressable button component.")
