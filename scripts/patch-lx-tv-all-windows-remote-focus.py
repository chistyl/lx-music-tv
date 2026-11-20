#!/usr/bin/env python3
"""Make every touchable in every TV screen and modal D-pad focusable with a shape-aware focus frame."""
from pathlib import Path
import re

ROOT = Path("upstream/lx-music-mobile-auto-source")
SRC = ROOT / "src"

WRAPPER = r"""import React, { forwardRef, useState } from 'react'
import {
  Pressable as RNPressable,
  StyleSheet,
  TouchableHighlight as RNTouchableHighlight,
  TouchableOpacity as RNTouchableOpacity,
  View,
} from 'react-native'
import { useTheme } from '@/store/theme/hook'

const useTVFocus = (style: any, onFocus?: (event: any) => void, onBlur?: (event: any) => void, focusable?: boolean) => {
  const [focused, setFocused] = useState(false)
  const theme = useTheme()
  const flatStyle = style && typeof style !== 'function' ? StyleSheet.flatten(style) : undefined
  const radius = flatStyle?.borderRadius
    ?? (typeof flatStyle?.width === 'number' && flatStyle.width === flatStyle.height ? flatStyle.width / 2 : 6)

  return {
    focusable: focusable !== false,
    onFocus: (event: any) => {
      setFocused(true)
      onFocus?.(event)
    },
    onBlur: (event: any) => {
      setFocused(false)
      onBlur?.(event)
    },
    frame: focused ? (
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          {
            borderWidth: 2,
            borderColor: theme['c-primary-font-active'] || '#FFFFFF',
            borderRadius: radius,
          },
        ]}
      />
    ) : null,
  }
}

export const TVTouchableOpacity = forwardRef<any, any>((props, ref) => {
  const { children, style, onFocus, onBlur, focusable, ...rest } = props
  const focus = useTVFocus(style, onFocus, onBlur, focusable)
  return (
    <RNTouchableOpacity {...rest} ref={ref} style={style} focusable={focus.focusable} onFocus={focus.onFocus} onBlur={focus.onBlur}>
      {children}
      {focus.frame}
    </RNTouchableOpacity>
  )
})

export const TVTouchableHighlight = forwardRef<any, any>((props, ref) => {
  const { children, style, onFocus, onBlur, focusable, ...rest } = props
  const focus = useTVFocus(style, onFocus, onBlur, focusable)
  return (
    <RNTouchableHighlight {...rest} ref={ref} style={style} focusable={focus.focusable} onFocus={focus.onFocus} onBlur={focus.onBlur}>
      {children}
      {focus.frame}
    </RNTouchableHighlight>
  )
})

export const TVPressable = forwardRef<any, any>((props, ref) => {
  const { children, style, onFocus, onBlur, focusable, ...rest } = props
  const focus = useTVFocus(style, onFocus, onBlur, focusable)
  const content = typeof children === 'function'
    ? (state: any) => <>{children(state)}{focus.frame}</>
    : <>{children}{focus.frame}</>
  return (
    <RNPressable {...rest} ref={ref} style={style} focusable={focus.focusable} onFocus={focus.onFocus} onBlur={focus.onBlur}>
      {content}
    </RNPressable>
  )
})

TVTouchableOpacity.displayName = 'TVTouchableOpacity'
TVTouchableHighlight.displayName = 'TVTouchableHighlight'
TVPressable.displayName = 'TVPressable'
"""

def main() -> None:
    wrapper_path = ROOT / "src/components/common/TVFocusable.tsx"
    wrapper_path.write_text(WRAPPER, encoding="utf-8")
    totals = {"TouchableOpacity": 0, "TouchableHighlight": 0, "Pressable": 0}
    import_re = re.compile(r"""import\s*\{([^}]+)\}\s*from\s*['"]react-native['"]""", re.S)
    tag_patterns = {
        "TouchableOpacity": (re.compile(r"(?<![A-Za-z0-9_$])<TouchableOpacity(?=[\s/>])"), "<TVTouchableOpacity"),
        "TouchableHighlight": (re.compile(r"(?<![A-Za-z0-9_$])<TouchableHighlight(?=[\s/>])"), "<TVTouchableHighlight"),
        "Pressable": (re.compile(r"(?<![A-Za-z0-9_$])<Pressable(?=[\s/>])"), "<TVPressable"),
    }
    closing_patterns = {
        "TouchableOpacity": (re.compile(r"</TouchableOpacity\s*>"), "</TVTouchableOpacity>"),
        "TouchableHighlight": (re.compile(r"</TouchableHighlight\s*>"), "</TVTouchableHighlight>"),
        "Pressable": (re.compile(r"</Pressable\s*>"), "</TVPressable>"),
    }
    already_focused = {
        "components/common/Button.tsx",
        "components/player/PlayerBar/components/ControlBtn.tsx",
        "screens/Home/Horizontal/Aside.tsx",
        "screens/Home/Views/Mylist/MyList/List.tsx",
        "screens/Home/Views/Mylist/MusicList/ListItem.tsx",
    }
    for path in SRC.rglob("*.tsx"):
        if path.relative_to(SRC).as_posix() in already_focused:
            continue
        source = path.read_text(encoding="utf-8")
        imports = list(import_re.finditer(source))
        enabled = []
        for match in imports:
            names = match.group(1)
            for name in totals:
                if re.search(r"(?<![A-Za-z0-9_$])" + name + r"(?![A-Za-z0-9_$])", names):
                    enabled.append(name)
        if not enabled:
            continue
        changed = source
        for name in enabled:
            pattern, replacement = tag_patterns[name]
            changed, count = pattern.subn(replacement, changed)
            totals[name] += count
            close_pattern, close_replacement = closing_patterns[name]
            changed = close_pattern.sub(close_replacement, changed)
        if changed != source and "@/components/common/TVFocusable" not in changed:
            aliases = ", ".join(
                {"TouchableOpacity": "TVTouchableOpacity", "TouchableHighlight": "TVTouchableHighlight", "Pressable": "TVPressable"}[name]
                for name in enabled
            )
            changed = "import { " + aliases + " } from '@/components/common/TVFocusable'\n" + changed
        path.write_text(changed, encoding="utf-8")

    print("Applied TV D-pad focus wrappers:", ", ".join(f"{name}={count}" for name, count in totals.items()))
    if not any(totals.values()):
        raise SystemExit("No React Native touchable controls were found; refusing an empty focus patch.")

if __name__ == "__main__":
    main()
