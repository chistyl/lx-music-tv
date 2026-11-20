#!/usr/bin/env python3
"""Apply Android TV layout, refined player spacing, theme colors, and remote focus adaptations."""
from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")

def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        if new in source:
            return source
        raise SystemExit(f"Could not locate patch anchor: {label}")
    return source.replace(old, new, 1)

def patch_player_controls() -> None:
    path = ROOT / "src/components/player/PlayerBar/components/ControlBtn.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { TouchableOpacity } from 'react-native'", "import { TouchableOpacity } from 'react-native'\nimport { useState } from 'react'\nimport { useSettingValue } from '@/store/setting/hook'\nimport { updateSetting } from '@/core/common'\nimport { MUSIC_TOGGLE_MODE_LIST } from '@/config/constant'", 1)
    for name in ("PlayPrevBtn", "PlayNextBtn", "TogglePlayBtn"):
        start = source.index(f"const {name} = () => {{")
        end = source.find("\n}\n", start) + 3
        block = source[start:end]
        block = block.replace("  const theme = useTheme()", "  const theme = useTheme()\n  const [tvFocused, setTvFocused] = useState(false)", 1)
        block = block.replace("style={styles.cotrolBtn}", "focusable\n      onFocus={() => setTvFocused(true)}\n      onBlur={() => setTvFocused(false)}\n      style={[styles.cotrolBtn, tvFocused ? styles.focusedControl : undefined]}", 1)
        source = source[:start] + block + source[end:]
    source = replace_once(source, "const styles = createStyle({", """const PlayModeBtn = () => {
  const theme = useTheme()
  const [tvFocused, setTvFocused] = useState(false)
  const togglePlayMethod = useSettingValue('player.togglePlayMethod')
  const modeIcons: Record<string, string> = {
    listLoop: 'list-loop',
    random: 'list-random',
    list: 'list-order',
    singleLoop: 'single-loop',
    none: 'single',
  }
  const toggleNextPlayMode = () => {
    let index = MUSIC_TOGGLE_MODE_LIST.indexOf(togglePlayMethod)
    if (++index >= MUSIC_TOGGLE_MODE_LIST.length) index = 0
    updateSetting({ 'player.togglePlayMethod': MUSIC_TOGGLE_MODE_LIST[index] })
  }
  return (
    <TouchableOpacity
      focusable
      onFocus={() => setTvFocused(true)}
      onBlur={() => setTvFocused(false)}
      style={[styles.cotrolBtn, tvFocused ? styles.focusedControl : undefined]}
      activeOpacity={0.5}
      onPress={toggleNextPlayMode}
    >
      <Icon name={modeIcons[togglePlayMethod] || 'list-loop'} color={theme['c-button-font']} size={BTN_SIZE + 6} />
    </TouchableOpacity>
  )
}

const styles = createStyle({""", "insert playback mode control")
    source = replace_once(source, "      <PlayNextBtn />\n    </>", "      <PlayNextBtn />\n      <PlayModeBtn />\n    </>", "render playback mode control")
    source = replace_once(source, "const BTN_SIZE = 24", "const BTN_SIZE = 19", "reduce player control icon size")
    source = replace_once(source, "    width: 46,\n    height: 46,", "    width: 40,\n    height: 40,", "reduce player control touch container")
    source = replace_once(source, "const styles = createStyle({\n  cotrolBtn: {", "const styles = createStyle({\n  focusedControl: { borderWidth: 3, borderColor: '#35A979', borderRadius: 30, backgroundColor: 'rgba(53,169,121,0.16)', shadowColor: '#35A979', shadowOpacity: 0.32, shadowRadius: 10, shadowOffset: { width: 0, height: 0 }, elevation: 6 },\n  cotrolBtn: {", "player focus style")
    path.write_text(source, encoding="utf-8")

def patch_player_bar() -> None:
    path = ROOT / "src/components/player/PlayerBar/index.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace(
        "<Pic isHome={isHome} />",
        "<Pic isHome={isHome} size={isHome ? 120 : 46} />",
        1,
    )
    source = source.replace(
        """    <View style={{ ...styles.container, backgroundColor: theme['c-content-background'] }}>""",
        """    <View style={[
      styles.container,
      isHome ? styles.homeContainer : undefined,
      { backgroundColor: theme['c-content-background'] },
    ]}>""",
        1,
    )
    source = source.replace(
        """      <View style={styles.center}>""",
        """      <View style={isHome ? styles.homeCenter : styles.center}>""",
        1,
    )
    source = source.replace(
        """      <View style={styles.right}>""",
        """      <View style={isHome ? styles.homeRight : styles.right}>""",
        1,
    )
    source = source.replace(
        """  container: {
    width: '100%',""",
        """  homeContainer: {
    width: '100%',
    height: '100%',
    flexDirection: 'column',
    justifyContent: 'flex-start',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 26,
    paddingBottom: 20,
    borderTopLeftRadius: 0,
    borderTopRightRadius: 0,
    elevation: 0,
  },
  homeCenter: {
    width: '100%',
    flexGrow: 0,
    flexShrink: 1,
    alignItems: 'center',
    paddingLeft: 0,
    marginTop: 22,
  },
  homeRight: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    flexGrow: 0,
    flexShrink: 0,
    paddingLeft: 0,
    paddingRight: 0,
    marginTop: 20,
  },
  container: {
    width: '100%',""",
        1,
    )
    path.write_text(source, encoding="utf-8")

    pic = ROOT / "src/components/player/PlayerBar/components/Pic.tsx"
    source = pic.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "export default ({ isHome }: { isHome: boolean }) => {",
        "export default ({ isHome, size = 46 }: { isHome: boolean, size?: number }) => {",
        "player cover size prop",
    )
    source = replace_once(
        source,
        "  const musicInfo = usePlayerMusicInfo()",
        "  const musicInfo = usePlayerMusicInfo()" + chr(10) + "  const imageSize = scaleSizeH(size)",
        "player cover image size",
    )
    source = replace_once(
        source,
        "style={styles.image}",
        "style={{ width: imageSize, height: imageSize, borderRadius: imageSize / 2 }}",
        "player cover circular image",
    )
    source = source.replace(
        "import { StyleSheet, TouchableOpacity } from 'react-native'",
        "import { StyleSheet, TouchableOpacity, Animated, Easing } from 'react-native'",
        1,
    )
    source = source.replace(
        "import { usePlayerMusicInfo } from '@/store/player/hook'",
        "import { usePlayerMusicInfo, useIsPlay } from '@/store/player/hook'",
        1,
    )
    source = source.replace("import { useCallback } from 'react'", "import { useCallback, useEffect, useRef } from 'react'", 1)
    source = replace_once(
        source,
        "  const musicInfo = usePlayerMusicInfo()",
        """  const musicInfo = usePlayerMusicInfo()
  const isPlay = useIsPlay()
  const rotateValue = useRef(new Animated.Value(0)).current

  useEffect(() => {
    if (isHome && isPlay) {
      const animation = Animated.loop(Animated.timing(rotateValue, {
        toValue: 1,
        duration: 9000,
        easing: Easing.linear,
        useNativeDriver: true,
      }))
      animation.start()
      return () => animation.stop()
    }
    rotateValue.stopAnimation()
    rotateValue.setValue(0)
  }, [isHome, isPlay, rotateValue])
  const rotate = rotateValue.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '360deg'] })""",
        "rotate album art while playing",
    )
    source = replace_once(
        source,
        "<Image url={musicInfo.pic} nativeID={NAV_SHEAR_NATIVE_IDS.playDetail_pic} style={{ width: imageSize, height: imageSize, borderRadius: imageSize / 2 }} onError={handleError} />",
        "<Animated.View style={{ width: imageSize, height: imageSize, borderRadius: imageSize / 2, overflow: 'hidden', transform: [{ rotate: isHome ? rotate : '0deg' }] }}><Image url={musicInfo.pic} nativeID={NAV_SHEAR_NATIVE_IDS.playDetail_pic} style={{ width: imageSize, height: imageSize, borderRadius: imageSize / 2 }} onError={handleError} /></Animated.View>",
        "rotating circular player artwork",
    )
    pic.write_text(source, encoding="utf-8")


def patch_button() -> None:
    target = ROOT / "src/components/common/Button.tsx"
    source = target.read_text(encoding="utf-8")
    source = source.replace(
        "import { useMemo, useRef, useImperativeHandle, forwardRef } from 'react'",
        "import { useMemo, useRef, useImperativeHandle, forwardRef, useState } from 'react'",
        1,
    )
    source = replace_once(
        source,
        """  const ripple = useMemo(() => ({
    color: theme['c-primary-light-200-alpha-700'],
    ...propsRipple,
  }), [theme, propsRipple])""",
        """  const ripple = useMemo(() => ({
    color: theme['c-primary-light-200-alpha-700'],
    ...propsRipple,
  }), [theme, propsRipple])
  const baseStyle = StyleSheet.flatten(style)
  const focusRadius = baseStyle?.borderRadius ?? 8""",
        "derive focus radius from original control shape",
    )
    source = replace_once(
        source,
        "({ ripple: propsRipple = {}, disabled, children, style, ...props }, ref) => {",
        "({ ripple: propsRipple = {}, disabled, children, style, onFocus, onBlur, ...props }, ref) => {",
        "shared button focus callbacks",
    )
    if "const [tvFocused, setTvFocused] = useState(false)" not in source:
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
        """      android_ripple={ripple}
      disabled={disabled}
      style={StyleSheet.compose({ opacity: disabled ? 0.3 : 1 }, style)}
      {...props}
      ref={btnRef}""",
        """      android_ripple={ripple}
      disabled={disabled}
      focusable
      onFocus={handleFocus}
      onBlur={handleBlur}
      style={StyleSheet.compose(
        StyleSheet.compose({ opacity: disabled ? 0.3 : 1 }, style),
        tvFocused ? {
          borderWidth: 2,
          borderColor: '#35A979',
          borderRadius: focusRadius,
          backgroundColor: 'rgba(53,169,121,0.14)',
          shadowColor: '#35A979',
          shadowOpacity: 0.32,
          shadowRadius: 9,
          shadowOffset: { width: 0, height: 0 },
          elevation: 6,
        } : undefined,
      )}
      {...props}
      ref={btnRef}""",
        "shared button shape-preserving focus ring",
    )
    target.write_text(source, encoding="utf-8")


def patch_tv_focus_surfaces() -> None:
    # Settings category rail: preserve the active marker and add a rounded focus surface.
    path = ROOT / "src/screens/Home/Views/Setting/Horizontal/NavList.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { memo, useRef, useState } from 'react'", "import { memo, useRef, useState } from 'react'", 1)
    source = replace_once(
        source,
        "  const theme = useTheme()\n  const t = useI18n()",
        "  const theme = useTheme()\n  const t = useI18n()\n  const [tvFocused, setTvFocused] = useState(false)",
        "settings navigation focus state",
    )
    source = replace_once(
        source,
        '<TouchableOpacity style={styles.listName} onPress={handlePress}>',
        '<TouchableOpacity focusable onFocus={() => setTvFocused(true)} onBlur={() => setTvFocused(false)} style={[styles.listName, tvFocused ? styles.tvFocused : undefined]} onPress={handlePress}>',
        "settings navigation focus target",
    )
    source = replace_once(
        source,
        "const styles = createStyle({\n  container:",
        "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 8, backgroundColor: 'rgba(53,169,121,0.12)', elevation: 5 },\n  container:",
        "settings navigation focus shape",
    )
    path.write_text(source, encoding="utf-8")

    # Search type tabs: focus the whole tab, while keeping the selected underline.
    path = ROOT / "src/screens/Home/Views/Search/SearchTypeSelector.tsx"
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "  const [type, setType] = useState<SearchType>('music')",
        "  const [type, setType] = useState<SearchType>('music')\n  const [focusedType, setFocusedType] = useState<SearchType | null>(null)",
        "search type focus state",
    )
    source = replace_once(
        source,
        '<TouchableOpacity style={styles.button} onPress={() => { handleTypeChange(t.id) }} key={t.id}>',
        '<TouchableOpacity focusable onFocus={() => setFocusedType(t.id)} onBlur={() => setFocusedType(null)} style={[styles.button, focusedType === t.id ? styles.tvFocused : undefined]} onPress={() => { handleTypeChange(t.id) }} key={t.id}>',
        "search type focus target",
    )
    source = replace_once(
        source,
        "const styles = createStyle({\n  container:",
        "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 9, backgroundColor: 'rgba(53,169,121,0.12)', elevation: 5 },\n  container:",
        "search type focus shape",
    )
    path.write_text(source, encoding="utf-8")

    # Context menu items are independent TV focus targets; preserve the menu's item geometry.
    path = ROOT / "src/components/common/Menu.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace(
        "import { View, Animated, TouchableHighlight } from 'react-native'",
        "import { View, Animated, TouchableHighlight } from 'react-native'",
        1,
    )
    source = replace_once(
        source,
        "  const theme = useTheme()\n  const windowSize = useWindowSize()",
        "  const theme = useTheme()\n  const windowSize = useWindowSize()",
        "context menu theme anchor",
    )
    source = replace_once(
        source,
        """                    <TouchableHighlight
                      key={menu.action}
                      style={{ ...styles.menuItem, width: menuItemStyle.width, height: menuItemStyle.height }}
                      underlayColor={theme['c-primary-background-active']}
                      onPress={() => { menuPress(menu) }}
                    >""",
        """                    <TouchableHighlight
                      key={menu.action}
                      focusable
                      hasTVPreferredFocus={index === 0}
                      style={{ ...styles.menuItem, width: menuItemStyle.width, height: menuItemStyle.height, borderRadius: 6 }}
                      underlayColor={theme['c-primary-background-active']}
                      onPress={() => { menuPress(menu) }}
                    >""",
        "context menu remote focus target",
    )
    path.write_text(source, encoding="utf-8")

    # Checkbox controls: keep the square checkbox silhouette and provide a rounded focus frame.
    path = ROOT / "src/components/common/CheckBox/Checkbox.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import * as React from 'react'", "import * as React from 'react'", 1)
    source = replace_once(
        source,
        "  const checked = status === 'checked'",
        "  const [tvFocused, setTvFocused] = React.useState(false)\n  const checked = status === 'checked'",
        "checkbox focus state",
    )
    source = replace_once(
        source,
        """      {...rest}
      onPress={onPress}
      disabled={disabled}
      accessibilityRole="checkbox"
      accessibilityState={{ disabled, checked }}
      accessibilityLiveRegion="polite"
      style={{ ...styles.container, padding: PADDING, marginLeft: -PADDING }}""",
        """      {...rest}
      focusable
      onFocus={() => setTvFocused(true)}
      onBlur={() => setTvFocused(false)}
      onPress={onPress}
      disabled={disabled}
      accessibilityRole="checkbox"
      accessibilityState={{ disabled, checked }}
      accessibilityLiveRegion="polite"
      style={[
        styles.container,
        { padding: PADDING, marginLeft: -PADDING },
        tvFocused ? styles.focusedContainer : undefined,
      ]}""",
        "checkbox remote focus target",
    )
    source = replace_once(
        source,
        "const styles = createStyle({\n  container:",
        "const styles = createStyle({\n  focusedContainer: { borderWidth: 2, borderColor: '#35A979', borderRadius: 7, backgroundColor: 'rgba(53,169,121,0.12)', elevation: 5 },\n  container:",
        "checkbox focus frame shape",
    )
    path.write_text(source, encoding="utf-8")

def patch_input_focus() -> None:
    target = ROOT / "src/components/common/Input.tsx"
    source = target.read_text(encoding="utf-8")
    source = source.replace(
        "import { useRef, useImperativeHandle, forwardRef, useCallback } from 'react'",
        "import { useRef, useImperativeHandle, forwardRef, useCallback, useState } from 'react'",
        1,
    )
    source = replace_once(
        source,
        "({ onChangeText, onClearText, clearBtn, style, size = 14, ...props }, ref) => {",
        "({ onChangeText, onClearText, clearBtn, style, size = 14, onFocus, onBlur, ...props }, ref) => {",
        "input focus callbacks",
    )
    source = replace_once(
        source,
        "  const inputRef = useRef<TextInput>(null)\n  const theme = useTheme()",
        "  const inputRef = useRef<TextInput>(null)\n  const theme = useTheme()\n  const [tvFocused, setTvFocused] = useState(false)",
        "input focus state",
    )
    source = replace_once(
        source,
        """        onChangeText={changeText}
        autoComplete="off"
        style={StyleSheet.compose({ ...styles.input, color: theme['c-font'], fontSize: setSpText(size) }, style)}""",
        """        onChangeText={changeText}
        autoComplete="off"
        onFocus={(event) => { setTvFocused(true); onFocus?.(event) }}
        onBlur={(event) => { setTvFocused(false); onBlur?.(event) }}
        style={StyleSheet.compose(
          StyleSheet.compose({ ...styles.input, color: theme['c-font'], fontSize: setSpText(size) }, style),
          tvFocused ? { borderWidth: 2, borderColor: '#35A979', backgroundColor: 'rgba(53,169,121,0.12)', elevation: 4 } : undefined,
        )}""",
        "input remote focus treatment",
    )
    target.write_text(source, encoding="utf-8")



def patch_slider_focus() -> None:
    # Native sliders remain adjustable with the D-pad; the focus frame follows
    # the rectangular track container rather than changing the thumb geometry.
    for relative_path in (
        "src/components/common/Slider.tsx",
        "src/screens/Home/Views/Setting/components/Slider.tsx",
    ):
        path = ROOT / relative_path
        source = path.read_text(encoding="utf-8")
        source = source.replace("import { memo } from 'react'", "import { memo, useState } from 'react'", 1)
        source = replace_once(
            source,
            "  const theme = useTheme()",
            "  const theme = useTheme()\n  const [tvFocused, setTvFocused] = useState(false)",
            f"slider focus state: {relative_path}",
        )
        source = replace_once(
            source,
            "      value={value}\n      style={styles.slider}",
            "      value={value}\n      focusable\n      onFocus={() => setTvFocused(true)}\n      onBlur={() => setTvFocused(false)}\n      style={[styles.slider, tvFocused ? styles.tvFocused : undefined]}",
            f"slider remote focus target: {relative_path}",
        )
        source = replace_once(
            source,
            "const styles = createStyle({\n  slider:",
            "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 10, backgroundColor: 'rgba(53,169,121,0.12)', elevation: 5 },\n  slider:",
            f"slider focus frame: {relative_path}",
        )
        path.write_text(source, encoding="utf-8")

def patch_navigation(relative_path: str) -> None:
    target = ROOT / relative_path
    source = target.read_text(encoding="utf-8")
    source = source.replace("import { memo } from 'react'", "import { memo, useState } from 'react'", 1)
    old = """  const activeId = useNavActiveId()
  const theme = useTheme()

  return activeId == id"""
    new = """  const activeId = useNavActiveId()
  const theme = useTheme()
  const [tvFocused, setTvFocused] = useState(false)

  return activeId == id"""
    if old in source:
        source = source.replace(old, new, 1)
    old_open = """    : <TouchableOpacity style={styles.menuItem} onPress={() => { onPress(id) }}>"""
    new_open = """    : <TouchableOpacity
        focusable
        onFocus={() => setTvFocused(true)}
        onBlur={() => setTvFocused(false)}
        style={[styles.menuItem, tvFocused ? { borderWidth: 2, borderColor: theme['c-primary-font-active'], borderRadius: 10, backgroundColor: 'rgba(53,169,121,0.12)', shadowColor: '#35A979', shadowOpacity: 0.28, shadowRadius: 9, shadowOffset: { width: 0, height: 2 }, elevation: 5 } : undefined]}
        onPress={() => { onPress(id) }}
      >"""
    if old_open in source:
        source = source.replace(old_open, new_open, 1)
    if "focusable" not in source:
        raise SystemExit(f"Failed to add focusable navigation item: {relative_path}")
    target.write_text(source, encoding="utf-8")

def patch_android_abis() -> None:
    path = ROOT / "android/app/build.gradle"
    source = path.read_text(encoding="utf-8")
    source = replace_once(source, 'return value ? value.split(",") : ["armeabi-v7a", "x86", "x86_64", "arm64-v8a"]', 'return value ? value.split(",") : ["x86", "x86_64"]', "default Android TV ABIs")
    source = replace_once(source, "universalApk true  // If true, also generate a universal APK", "universalApk true  // Generate a universal APK in addition to x86 and x86_64 APKs", "enable universal APK")
    path.write_text(source, encoding="utf-8")


def patch_my_lists() -> None:
    path = ROOT / "src/screens/Home/Views/Mylist/MyList/List.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { memo, useEffect, useRef } from 'react'", "import { memo, useEffect, useRef, useState } from 'react'", 1)
    source = replace_once(source, "const ITEM_HEIGHT = scaleSizeH(40)", "const ITEM_HEIGHT = scaleSizeH(60)", "playlist row height")
    source = replace_once(source, "  const theme = useTheme()\n  const moreButtonRef", "  const theme = useTheme()\n  const [nameFocused, setNameFocused] = useState(false)\n  const [moreFocused, setMoreFocused] = useState(false)\n  const moreButtonRef", "playlist focus state")
    source = replace_once(source, '<TouchableOpacity style={styles.listName} onPress={handlePress}>', '<TouchableOpacity focusable onFocus={() => setNameFocused(true)} onBlur={() => setNameFocused(false)} style={[styles.listName, nameFocused ? styles.tvFocused : undefined]} onPress={handlePress}>', "playlist name focus")
    source = replace_once(source, '<TouchableOpacity onPress={handleShowMenu} ref={moreButtonRef} style={styles.listMoreBtn}>', '<TouchableOpacity focusable onFocus={() => setMoreFocused(true)} onBlur={() => setMoreFocused(false)} onPress={handleShowMenu} ref={moreButtonRef} style={[styles.listMoreBtn, moreFocused ? styles.tvFocused : undefined]}>', "playlist menu focus")
    source = replace_once(source, "const styles = createStyle({\n  container:", "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 6 },\n  container:", "playlist focus style")
    source = replace_once(source, "    width: 36,", "    width: 52,", "playlist menu target")
    path.write_text(source, encoding="utf-8")

    path = ROOT / "src/screens/Home/Views/Mylist/MusicList/ListItem.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { memo, useRef } from 'react'", "import { memo, useRef, useState } from 'react'", 1)
    source = replace_once(source, "  const theme = useTheme()\n\n  const isSelected", "  const theme = useTheme()\n  const [itemFocused, setItemFocused] = useState(false)\n  const [moreFocused, setMoreFocused] = useState(false)\n\n  const isSelected", "song row focus state")
    source = replace_once(source, '<TouchableOpacity style={styles.listItemLeft} onPress=', '<TouchableOpacity focusable onFocus={() => setItemFocused(true)} onBlur={() => setItemFocused(false)} style={[styles.listItemLeft, itemFocused ? styles.tvFocused : undefined]} onPress=', "song row focus")
    source = replace_once(source, '<TouchableOpacity onPress={handleShowMenu} ref={moreButtonRef} style={styles.moreButton}>', '<TouchableOpacity focusable onFocus={() => setMoreFocused(true)} onBlur={() => setMoreFocused(false)} onPress={handleShowMenu} ref={moreButtonRef} style={[styles.moreButton, moreFocused ? styles.tvFocused : undefined]}>', "song menu focus")
    source = replace_once(source, "const styles = createStyle({\n  listItem:", "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 6 },\n  listItem:", "song row focus style")
    source = replace_once(source, "    height: '80%',\n    paddingLeft: 16,\n    paddingRight: 16,", "    height: '100%',\n    minWidth: 52,\n    paddingLeft: 12,\n    paddingRight: 12,", "song menu target")
    path.write_text(source, encoding="utf-8")




def patch_home_layout() -> None:
    # Keep the original navigation and player components and move only their placement.
    home = ROOT / "src/screens/Home/Horizontal/index.tsx"
    source = home.read_text(encoding="utf-8")
    source = source.replace(
        "import Aside from './Aside'\nimport PlayerBar from '@/components/player/PlayerBar'",
        "import Aside from './Aside'\nimport PlayerBar from '@/components/player/PlayerBar'",
        1,
    )
    old_layout = """const styles = createStyle({
  container: {
    flex: 1,
    flexDirection: 'row',
  },
  content: {
    flex: 1,
    overflow: 'hidden',
  },
})

export default () => {
  return (
    <>
      <StatusBar />
      <View style={styles.container}>
        <Aside />
        <View style={styles.content}>
          <Header />
          <Main />
          <PlayerBar isHome />
        </View>
      </View>
    </>
  )
}
"""
    new_layout = """const styles = createStyle({
  container: {
    flex: 1,
    flexDirection: 'column',
    overflow: 'hidden',
  },
  content: {
    flex: 1,
    minHeight: 0,
    flexDirection: 'row',
    overflow: 'hidden',
  },
  player: {
    width: '26%',
    flexGrow: 0,
    flexShrink: 0,
    overflow: 'hidden',
  },
  main: {
    flex: 1,
    minWidth: 0,
    overflow: 'hidden',
  },
})

export default () => (
  <>
    <StatusBar />
    <View style={styles.container}>
      <Aside />
      <View style={styles.content}>
        <View style={styles.player}>
          <PlayerBar isHome />
        </View>
        <View style={styles.main}>
          <Header />
          <Main />
        </View>
      </View>
    </View>
  </>
)
"""
    source = replace_once(source, old_layout, new_layout, "home horizontal layout")
    home.write_text(source, encoding="utf-8")

    aside = ROOT / "src/screens/Home/Horizontal/Aside.tsx"
    aside.write_text("""import { memo, useState } from 'react'
import { ScrollView, TouchableOpacity, View } from 'react-native'
import { useNavActiveId, useStatusbarHeight } from '@/store/common/hook'
import { useTheme } from '@/store/theme/hook'
import { useI18n } from '@/lang'
import { Icon } from '@/components/common/Icon'
import Text from '@/components/common/Text'
import { createStyle } from '@/utils/tools'
import { NAV_MENUS } from '@/config/constant'
import type { InitState } from '@/store/common/state'
import { setNavActiveId } from '@/core/common'


type IdType = InitState['navActiveId']

const MenuItem = ({ id, icon, onPress }: {
  id: IdType
  icon: string
  onPress: (id: IdType) => void
}) => {
  const activeId = useNavActiveId()
  const theme = useTheme()
  const t = useI18n()
  const [focused, setFocused] = useState(false)
  const active = activeId === id

  return (
    <TouchableOpacity
      focusable
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      onPress={() => onPress(id)}
      style={[styles.menuItem, active ? styles.activeItem : undefined, focused ? [styles.focusedItem, { borderColor: theme['c-primary-font-active'] }] : undefined]}
    >
      <Icon name={icon} size={20} color={active || focused ? theme['c-primary-font-active'] : theme['c-font-label']} />
      <Text size={14} color={active || focused ? theme['c-primary-font-active'] : theme['c-font-label']}>{t(id)}</Text>
    </TouchableOpacity>
  )
}

export default memo(() => {
  const theme = useTheme()
  const statusBarHeight = useStatusbarHeight()

  const handlePress = (id: IdType) => {
    global.app_event.changeMenuVisible(false)
    setNavActiveId(id)
  }

  return (
    <View style={[styles.container, {
      paddingTop: statusBarHeight,
      borderBottomColor: theme['c-border-background'],
      backgroundColor: theme['c-content-background'],
    }]}>
      <View style={styles.logo}>
        <Icon name="logo" color={theme['c-primary-font-active']} size={25} />
        <Text size={18} color={theme['c-primary-font-active']} style={styles.logoText}>Music</Text>
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.menuList}>
        {NAV_MENUS.map(menu => <MenuItem key={menu.id} id={menu.id} icon={menu.icon} onPress={handlePress} />)}
      </ScrollView>
    </View>
  )
})

const styles = createStyle({
  container: {
    width: '100%',
    height: 72,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    paddingHorizontal: 20,
    flexGrow: 0,
    flexShrink: 0,
  },
  logo: {
    width: 138,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-start',
    gap: 10,
  },
  logoText: {
    fontWeight: '600',
    letterSpacing: 0.3,
  },
  menuList: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingRight: 4,
  },
  menuItem: {
    flex: 1,
    minWidth: 0,
    height: 44,
    paddingHorizontal: 8,
    borderRadius: 9,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 7,
  },
  activeItem: {
    backgroundColor: 'transparent',
  },
  focusedItem: {
    borderWidth: 2,
    borderColor: 'transparent',
    backgroundColor: 'rgba(53,169,121,0.12)',
    shadowColor: '#35A979',
    shadowOpacity: 0.28,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 0 },
    elevation: 5,
  },
})
""", encoding="utf-8")



def patch_full_settings_focus() -> None:
    # Settings category list (vertical layout).
    path = ROOT / "src/screens/Home/Views/Setting/Vertical/NavList.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { memo, useCallback, useState } from 'react'", "import { memo, useCallback, useState } from 'react'", 1)
    source = replace_once(
        source,
        "  const t = useI18n()\n\n  const active = activeId == id",
        "  const t = useI18n()\n  const [tvFocused, setTvFocused] = useState(false)\n\n  const active = activeId == id",
        "vertical settings navigation focus state",
    )
    old_target = '<TouchableOpacity style={styles.listName} onPress={handlePress}>'
    new_target = '<TouchableOpacity focusable onFocus={() => setTvFocused(true)} onBlur={() => setTvFocused(false)} style={[styles.listName, tvFocused ? styles.tvFocused : undefined]} onPress={handlePress}>'
    if old_target in source:
        source = source.replace(old_target, new_target, 1)
    elif "tvFocused ? styles.tvFocused" not in source:
        source = source.replace("<TouchableOpacity", new_target, 1)
    else:
        raise SystemExit("Could not locate vertical settings navigation focus target")
    source = replace_once(
        source,
        "const styles = createStyle({\n  container:",
        "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 9, backgroundColor: 'rgba(53,169,121,0.12)', elevation: 4 },\n  container:",
        "vertical settings navigation focus appearance",
    )
    path.write_text(source, encoding="utf-8")

    # Compact setting category selector in vertical mode.
    path = ROOT / "src/screens/Home/Views/Setting/Vertical/Header.tsx"
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "  const t = useI18n()\n",
        "  const t = useI18n()\n  const [tvFocused, setTvFocused] = useState(false)\n",
        "vertical settings header focus state",
    )
    source = replace_once(
        source,
        '<TouchableOpacity onPress={onShowNavBar} style={{ ...styles.currentList, borderBottomColor: theme[\'c-border-background\'] }}>',
        '<TouchableOpacity focusable onFocus={() => setTvFocused(true)} onBlur={() => setTvFocused(false)} onPress={onShowNavBar} style={[styles.currentList, { borderBottomColor: theme[\'c-border-background\'] }, tvFocused ? styles.tvFocused : undefined]}>',
        "vertical settings header focus target",
    )
    source = replace_once(
        source,
        "const styles = createStyle({\n  currentList:",
        "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 8, backgroundColor: 'rgba(53,169,121,0.12)', elevation: 4 },\n  currentList:",
        "vertical settings header focus appearance",
    )
    path.write_text(source, encoding="utf-8")

    # Checkbox label/help controls are separate focus targets, not mouse-only hit areas.
    path = ROOT / "src/components/common/CheckBox/index.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { useCallback, useEffect, useMemo, useState } from 'react'", "import { useCallback, useEffect, useMemo, useState } from 'react'", 1)
    source = replace_once(
        source,
        "  const [isDisabled, setDisabled] = useState(false)",
        "  const [isDisabled, setDisabled] = useState(false)\n  const [labelFocused, setLabelFocused] = useState(false)\n  const [helpFocused, setHelpFocused] = useState(false)",
        "checkbox label and help focus states",
    )
    source = replace_once(
        source,
        '<TouchableOpacity style={styles.helpBtn} onPress={handleShowHelp}>',
        '<TouchableOpacity focusable onFocus={() => setHelpFocused(true)} onBlur={() => setHelpFocused(false)} style={[styles.helpBtn, helpFocused ? styles.tvFocused : undefined]} onPress={handleShowHelp}>',
        "checkbox help focus target",
    )
    source = replace_once(
        source,
        '<TouchableOpacity style={labelStyle} activeOpacity={0.3} onPress={handleLabelPress}>',
        '<TouchableOpacity focusable onFocus={() => setLabelFocused(true)} onBlur={() => setLabelFocused(false)} style={[labelStyle, labelFocused ? styles.tvFocused : undefined]} activeOpacity={0.3} onPress={handleLabelPress}>',
        "checkbox label focus target",
    )
    source = replace_once(
        source,
        "const styles = createStyle({\n  content:",
        "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 8, backgroundColor: 'rgba(53,169,121,0.12)', elevation: 4 },\n  content:",
        "checkbox label focus appearance",
    )
    path.write_text(source, encoding="utf-8")

    # Dialog and popup close buttons must be D-pad reachable and visibly focused.
    path = ROOT / "src/components/common/Dialog.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { useImperativeHandle, forwardRef, useMemo, useRef } from 'react'", "import { useImperativeHandle, forwardRef, useMemo, useRef, useState } from 'react'", 1)
    source = replace_once(source, "  const modalRef = useRef<ModalType>(null)", "  const modalRef = useRef<ModalType>(null)\n  const [closeFocused, setCloseFocused] = useState(false)", "dialog close focus state")
    source = replace_once(
        source,
        "return closeBtn\n      ? <TouchableHighlight style={{ ...styles.closeBtn, width: scaleSizeH(HEADER_HEIGHT) }}",
        "return closeBtn\n      ? <TouchableHighlight focusable onFocus={() => setCloseFocused(true)} onBlur={() => setCloseFocused(false)} style={[styles.closeBtn, { width: scaleSizeH(HEADER_HEIGHT) }, closeFocused ? styles.closeBtnFocused : undefined]}",
        "dialog close focus target",
    )
    source = replace_once(
        source,
        "  closeBtn: {",
        "  closeBtnFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 7, backgroundColor: 'rgba(53,169,121,0.14)', elevation: 5 },\n  closeBtn: {",
        "dialog close focus appearance",
    )
    path.write_text(source, encoding="utf-8")

    path = ROOT / "src/components/common/Popup.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { forwardRef, useImperativeHandle, useMemo, useRef } from 'react'", "import { forwardRef, useImperativeHandle, useMemo, useRef, useState } from 'react'", 1)
    source = replace_once(source, "  const modalRef = useRef<ModalType>(null)", "  const modalRef = useRef<ModalType>(null)\n  const [closeFocused, setCloseFocused] = useState(false)", "popup close focus state")
    source = replace_once(
        source,
        "? <TouchableOpacity style={styles.closeBtn} onPress={() => modalRef.current?.setVisible(false)}>",
        "? <TouchableOpacity focusable onFocus={() => setCloseFocused(true)} onBlur={() => setCloseFocused(false)} style={[styles.closeBtn, closeFocused ? styles.closeBtnFocused : undefined]} onPress={() => modalRef.current?.setVisible(false)}>",
        "popup close focus target",
    )
    source = replace_once(
        source,
        "  closeBtn: {",
        "  closeBtnFocused: { borderWidth: 2, borderColor: '#35A979', borderRadius: 8, backgroundColor: 'rgba(53,169,121,0.14)', elevation: 5 },\n  closeBtn: {",
        "popup close focus appearance",
    )
    path.write_text(source, encoding="utf-8")

    path = ROOT / "src/screens/Home/Views/Setting/settings/Basic/SourceQuickAdd.tsx"
    source = path.read_text(encoding="utf-8")
    source = replace_once(source, "  const [url, setUrl] = useState('')", "  const [url, setUrl] = useState('')\n  const [urlFocused, setUrlFocused] = useState(false)", "quick add input focus state")
    source = replace_once(
        source,
        '<TextInput value={url} onChangeText={setUrl} placeholder="输入源链接或订阅地址" accessibilityLabel="快速添加地址" autoCapitalize="none" autoCorrect={false} style={{ color: theme[\'c-font\'] }} />',
        '<TextInput focusable value={url} onFocus={() => setUrlFocused(true)} onBlur={() => setUrlFocused(false)} onChangeText={setUrl} placeholder="输入源链接或订阅地址" accessibilityLabel="快速添加地址" autoCapitalize="none" autoCorrect={false} style={{ color: theme[\'c-font\'], borderWidth: urlFocused ? 2 : 0, borderColor: "#35A979", borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8 }} />',
        "quick add input focus target",
    )
    path.write_text(source, encoding="utf-8")

def patch_global_touchable_focus() -> None:
    # Wrap raw React Native touchables so every screen shares one shape-aware focus system.
    wrapper = ROOT / "src/components/common/TVTouchableOpacity.tsx"
    wrapper.write_text("""import { forwardRef, useState } from 'react'
import {
  TouchableOpacity as NativeTouchableOpacity,
  TouchableHighlight as NativeTouchableHighlight,
  type TouchableOpacityProps,
  type TouchableHighlightProps,
  StyleSheet,
} from 'react-native'
import { useTheme } from '@/store/theme/hook'

const focusSurface = (style: any, color: string) => {
  const base = StyleSheet.flatten(style) || {}
  const radius = base.borderRadius ?? 8
  return {
    borderWidth: 2,
    borderColor: color,
    borderRadius: radius,
    backgroundColor: 'rgba(53,169,121,0.12)',
    shadowColor: color,
    shadowOpacity: 0.28,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 5,
  }
}

const TVTouchableOpacity = forwardRef<any, TouchableOpacityProps>(({ style, onFocus, onBlur, focusable = true, ...props }, ref) => {
  const [focused, setFocused] = useState(false)
  const theme = useTheme()
  const color = theme['c-primary-font-active'] || '#35A979'
  return (
    <NativeTouchableOpacity
      {...props}
      ref={ref}
      focusable={focusable}
      onFocus={event => { setFocused(true); onFocus?.(event) }}
      onBlur={event => { setFocused(false); onBlur?.(event) }}
      style={[style, focused ? focusSurface(style, color) : undefined]}
    />
  )
})

export const TVTouchableHighlight = forwardRef<any, TouchableHighlightProps>(({ style, onFocus, onBlur, focusable = true, ...props }, ref) => {
  const [focused, setFocused] = useState(false)
  const theme = useTheme()
  const color = theme['c-primary-font-active'] || '#35A979'
  return (
    <NativeTouchableHighlight
      {...props}
      ref={ref}
      focusable={focusable}
      onFocus={event => { setFocused(true); onFocus?.(event) }}
      onBlur={event => { setFocused(false); onBlur?.(event) }}
      style={[style, focused ? focusSurface(style, color) : undefined]}
    />
  )
})

export default TVTouchableOpacity
""", encoding="utf-8")

    import re
    for path in (ROOT / "src").rglob("*.tsx"):
        if path == wrapper:
            continue
        source = path.read_text(encoding="utf-8")
        changed = False
        def rewrite_import(match):
            nonlocal changed
            names = match.group(1)
            additions = []
            if re.search(r"\bTouchableOpacity\b", names):
                names = re.sub(r"\bTouchableOpacity\b(?!\s+as)", "TouchableOpacity as NativeTouchableOpacity", names)
                additions.append("import TouchableOpacity from '@/components/common/TVTouchableOpacity'")
            if re.search(r"\bTouchableHighlight\b", names):
                names = re.sub(r"\bTouchableHighlight\b(?!\s+as)", "TouchableHighlight as NativeTouchableHighlight", names)
                additions.append("import { TVTouchableHighlight as TouchableHighlight } from '@/components/common/TVTouchableOpacity'")
            if additions:
                changed = True
                return "import {" + names + "} from 'react-native'\n" + "\n".join(additions)
            return match.group(0)
        updated = re.sub(r"import\s*\{([^}]+)\}\s*from\s*'react-native'", rewrite_import, source, flags=re.S)
        if changed:
            updated = updated.replace("useRef<TouchableOpacity>", "useRef<NativeTouchableOpacity>")
            path.write_text(updated, encoding="utf-8")


def patch_all_touchables_focusable() -> None:
    # Last pass: every remaining touch target in the TV app becomes D-pad reachable.
    import re
    for path in (ROOT / "src").rglob("*.tsx"):
        source = path.read_text(encoding="utf-8")
        updated = re.sub(r"<TouchableOpacity(?![^>]*\bfocusable)(?=[\s>])", "<TouchableOpacity focusable", source)
        updated = re.sub(r"<TouchableHighlight(?![^>]*\bfocusable)(?=[\s>])", "<TouchableHighlight focusable", updated)
        if updated != source:
            path.write_text(updated, encoding="utf-8")

patch_button()
patch_input_focus()

def patch_menu_focus_visual() -> None:
    path = ROOT / "src/components/common/Menu.tsx"
    source = path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "  const theme = useTheme()\n  const windowSize = useWindowSize()",
        "  const theme = useTheme()\n  const windowSize = useWindowSize()\n  const [focusedAction, setFocusedAction] = useState<string | null>(null)",
        "menu focus state",
    )
    source = replace_once(
        source,
        "style={{ ...styles.menuItem, width: menuItemStyle.width, height: menuItemStyle.height, borderRadius: 6 }}\n                      underlayColor={theme['c-primary-background-active']}",
        "style={[styles.menuItem, { width: menuItemStyle.width, height: menuItemStyle.height, borderRadius: 6 }, focusedAction === menu.action ? { borderWidth: 2, borderColor: '#35A979', backgroundColor: 'rgba(53,169,121,0.14)', elevation: 5 } : undefined]}\n                      onFocus={() => setFocusedAction(menu.action)}\n                      onBlur={() => setFocusedAction(null)}\n                      underlayColor={theme['c-primary-background-active']}",
        "menu row focus appearance",
    )
    path.write_text(source, encoding="utf-8")

patch_tv_focus_surfaces()
patch_menu_focus_visual()
patch_full_settings_focus()
patch_my_lists()
patch_slider_focus()
patch_home_layout()
patch_player_controls()
patch_player_bar()
patch_all_touchables_focusable()
patch_global_touchable_focus()
print("Applied TV layout relocation and remote focus adaptations.")
