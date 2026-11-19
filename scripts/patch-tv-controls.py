#!/usr/bin/env python3
"""Apply Android TV remote focus and touch-target adaptations to LX Music RN UI."""
from pathlib import Path
import re

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
    source = source.replace("import { TouchableOpacity } from 'react-native'", "import { TouchableOpacity } from 'react-native'\nimport { useState } from 'react'", 1)
    for name in ("PlayPrevBtn", "PlayNextBtn", "TogglePlayBtn"):
        start = source.index(f"const {name} = () => {{")
        end = source.find("\n}\n", start) + 3
        block = source[start:end]
        block = block.replace("  const theme = useTheme()", "  const theme = useTheme()\n  const [tvFocused, setTvFocused] = useState(false)", 1)
        block = block.replace("style={styles.cotrolBtn}", "focusable\n      onFocus={() => setTvFocused(true)}\n      onBlur={() => setTvFocused(false)}\n      style={[styles.cotrolBtn, tvFocused ? styles.focusedControl : undefined]}", 1)
        source = source[:start] + block + source[end:]
    source = replace_once(source, "    width: 46,\n    height: 46,", "    width: 60,\n    height: 60,", "player control target")
    source = replace_once(source, "const styles = createStyle({\n  cotrolBtn: {", "const styles = createStyle({\n  focusedControl: { borderWidth: 2, borderColor: '#FFFFFF', borderRadius: 30 },\n  cotrolBtn: {", "player focus style")
    path.write_text(source, encoding="utf-8")

def patch_player_bar() -> None:
    path = ROOT / "src/components/player/PlayerBar/index.tsx"
    source = path.read_text(encoding="utf-8")
    source = replace_once(source, "    paddingVertical: 5,\n    paddingLeft: 5,", "    paddingVertical: 8,\n    paddingLeft: 8,", "player bar padding")
    source = replace_once(source, "    paddingLeft: 5,\n    paddingRight: 5,", "    paddingLeft: 8,\n    paddingRight: 8,", "player bar control spacing")
    path.write_text(source, encoding="utf-8")



def patch_home_layout() -> None:
    # Landscape home: navigation becomes a top horizontal strip; the player occupies
    # a dedicated left pane beside the active content.
    home = ROOT / "src/screens/Home/Horizontal/index.tsx"
    home.write_text("""import { View } from 'react-native'
import Aside from './Aside'
import PlayerBar from '@/components/player/PlayerBar'
import StatusBar from '@/components/common/StatusBar'
import Header from './Header'
import Main from './Main'
import { createStyle } from '@/utils/tools'

const styles = createStyle({
  container: {
    flex: 1,
    flexDirection: 'column',
    overflow: 'hidden',
  },
  body: {
    flex: 1,
    flexDirection: 'row',
    overflow: 'hidden',
  },
  playerPane: {
    width: '32%',
    flexGrow: 0,
    flexShrink: 0,
    overflow: 'hidden',
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
        <View style={styles.body}>
          <View style={styles.playerPane}>
            <PlayerBar isHome />
          </View>
          <View style={styles.content}>
            <Header />
            <Main />
          </View>
        </View>
      </View>
    </>
  )
}
""", encoding="utf-8")

    aside = ROOT / "src/screens/Home/Horizontal/Aside.tsx"
    source = aside.read_text(encoding="utf-8")
    source = source.replace("import { memo } from 'react'", "import { memo, useState } from 'react'", 1)
    source = source.replace("import { ScrollView, TouchableOpacity, View } from 'react-native'", "import { ScrollView, TouchableOpacity, View, Text } from 'react-native'", 1)
    source = replace_once(source, "const NAV_WIDTH = 68", "const NAV_HEIGHT = 104", "top navigation height")
    source = replace_once(source, """  container: {
    flexGrow: 0,
    // flex: 1,
    // alignItems: 'center',
    // justifyContent: 'center',
    // padding: 10,
    borderRightWidth: BorderWidths.normal,
    paddingBottom: 10,
    width: NAV_WIDTH,
  },""", """  container: {
    flexGrow: 0,
    flexShrink: 0,
    width: '100%',
    height: NAV_HEIGHT,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: BorderWidths.normal,
  },""", "top navigation container")
    source = replace_once(source, """  header: {
    paddingTop: 15,
    paddingBottom: 15,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },""", """  header: {
    width: 360,
    height: '100%',
    justifyContent: 'center',
    alignItems: 'flex-start',
    paddingLeft: 58,
  },""", "top navigation logo")
    source = replace_once(source, """  menus: {
    flex: 1,
  },
  list: {
    // paddingTop: 10,
    paddingBottom: 15,
  },
  menuItem: {
    flexDirection: 'row',
    paddingTop: 15,
    paddingBottom: 15,
    // paddingLeft: 25,
    // paddingRight: 25,
    justifyContent: 'center',
    alignItems: 'center',
    // backgroundColor: 'rgba(0, 0, 0, 0.2)',
  },""", """  menus: {
    flex: 1,
    height: '100%',
  },
  list: {
    height: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  menuItem: {
    flexDirection: 'row',
    paddingVertical: 12,
    paddingHorizontal: 14,
    marginHorizontal: 3,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 8,
  },""", "horizontal navigation items")
    source = replace_once(source, """  text: {
    paddingLeft: 15,
    // fontWeight: '500',
  },""", """  text: {
    paddingLeft: 15,
  },""", "navigation text style")
    start = source.index("const MenuItem =")
    end = source.index("\nexport default memo", start)
    menu_component = """const MenuItem = ({ id, icon, onPress }: {
  id: IdType
  icon: string
  onPress: (id: IdType) => void
}) => {
  const activeId = useNavActiveId()
  const theme = useTheme()
  const [tvFocused, setTvFocused] = useState(false)
  const active = activeId == id

  return (
    <TouchableOpacity
      focusable
      onFocus={() => setTvFocused(true)}
      onBlur={() => setTvFocused(false)}
      style={[
        styles.menuItem,
        active ? { borderBottomWidth: 3, borderBottomColor: theme['c-primary-font-active'] } : undefined,
        tvFocused ? { borderWidth: 2, borderColor: theme['c-primary-font-active'] } : undefined,
      ]}
      onPress={() => onPress(id)}
    >
      <View style={styles.iconContent}>
        <Icon
          name={icon}
          size={24}
          color={active || tvFocused ? theme['c-primary-font-active'] : theme['c-font-label']}
        />
      </View>
      <Text style={{ marginLeft: 12, fontSize: 20, color: active || tvFocused ? theme['c-primary-font-active'] : theme['c-font-label'] }}>
        {global.i18n.t(id)}
      </Text>
    </TouchableOpacity>
  )
}
"""
    source = source[:start] + menu_component + source[end:]
    source = replace_once(source, """      <ScrollView style={styles.menus}>
        <View style={styles.list}>""", """      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.menus}>
        <View style={styles.list}>""", "horizontal navigation scrolling")
    source = source.replace("  const showExitBtn = useSettingValue('common.showExitBtn')\n", "", 1)
    source = replace_once(source, """      {
        showBackBtn ? <MenuItem id="back_home" icon="home" onPress={handlePress} /> : null
      }
      {
        showExitBtn ? <MenuItem id="nav_exit" icon="exit2" onPress={handlePress} /> : null
      }""", """      <View style={{ flexDirection: 'row', alignItems: 'center', paddingHorizontal: 6 }}>
        {showBackBtn ? <MenuItem id="back_home" icon="home" onPress={handlePress} /> : null}
      </View>""", "remove right-side exit button")
    source = source.replace("borderRightColor: theme['c-border-background']", "borderBottomColor: theme['c-border-background']", 1)
    source = source.replace("borderRightColor: theme['c-border-background']", "borderBottomColor: theme['c-border-background']", 1)
    # Keep the Music wordmark reproducible from a clean pinned upstream checkout.
    if "fontSize: 42, fontWeight: '700'" not in source:
        source, count = re.subn(
            r'(<Icon\s+name=["\']logo["\']\s+color=\{theme\[["\']c-primary-dark-100-alpha-300["\']\]\}\s+size=\{\d+\}\s*/>)',
            r"\1\n        <Text style={{ marginLeft: 12, fontSize: 42, fontWeight: '700', color: theme['c-primary-dark-100-alpha-300'] }}>Music</Text>",
            source,
            count=1,
        )
        if count != 1:
            raise SystemExit(f"Failed to add Music wordmark: matched {count} logo anchors")
    if "fontSize: 25, fontWeight: '700'" not in source:
        raise SystemExit("Music wordmark verification failed")

    aside.write_text(source, encoding="utf-8")

    player = ROOT / "src/components/player/PlayerBar/index.tsx"
    source = player.read_text(encoding="utf-8")
    source = replace_once(source, """    <View style={{ ...styles.container, backgroundColor: theme['c-content-background'] }}>
      <Pic isHome={isHome} />
      <View style={styles.center}>""", """    <View style={{ ...styles.container, ...(isHome ? styles.homeContainer : {}), backgroundColor: theme['c-content-background'] }}>
      <Pic isHome={isHome} />
      <View style={{ ...styles.center, ...(isHome ? styles.homeCenter : {}) }}>""", "left player panel container")
    source = replace_once(source, """      <View style={styles.right}>
        <ControlBtn />
      </View>""", """      <View style={{ ...styles.right, ...(isHome ? styles.homeRight : {}) }}>
        <ControlBtn />
      </View>""", "left player panel controls")
    source = replace_once(source, """  left: {
    // borderRadius: 3,""", """  homeContainer: {
    width: '100%',
    height: '100%',
    paddingVertical: 18,
    paddingHorizontal: 14,
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    borderTopRightRadius: 0,
    borderTopLeftRadius: 0,
  },
  homeCenter: {
    width: '100%',
    flexGrow: 0,
    flexShrink: 0,
    paddingLeft: 0,
    alignItems: 'center',
    marginTop: 14,
  },
  homeRight: {
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'center',
    paddingLeft: 0,
    paddingRight: 0,
    marginTop: 12,
  },
  left: {
    // borderRadius: 3,""", "left player panel styles")
    player.write_text(source, encoding="utf-8")

    pic = ROOT / "src/components/player/PlayerBar/components/Pic.tsx"
    source = pic.read_text(encoding="utf-8")
    source = replace_once(source, """  const musicInfo = usePlayerMusicInfo()
  const handlePress""", """  const musicInfo = usePlayerMusicInfo()
  const picSize = isHome ? scaleSizeH(350) : PIC_HEIGHT
  const handlePress""", "large home player artwork")
    source = replace_once(source, """<Image url={musicInfo.pic} nativeID={NAV_SHEAR_NATIVE_IDS.playDetail_pic} style={styles.image} onError={handleError} />""", """<Image url={musicInfo.pic} nativeID={NAV_SHEAR_NATIVE_IDS.playDetail_pic} style={[styles.image, { width: picSize, height: picSize, borderRadius: picSize / 2, borderWidth: isHome ? 2 : 0, borderColor: '#25C76A' }]} onError={handleError} />""", "home player artwork size")
    pic.write_text(source, encoding="utf-8")

    print("Applied LX Music TV home layout: top navigation, left-side player panel, and enlarged player artwork.")

def patch_button() -> None:
    target = ROOT / "src/components/common/Button.tsx"
    source = target.read_text(encoding="utf-8")
    source = source.replace(
        "import { useMemo, useRef, useImperativeHandle, forwardRef } from 'react'",
        "import { useMemo, useRef, useImperativeHandle, forwardRef, useState } from 'react'",
        1,
    )
    source = source.replace(
        "({ ripple: propsRipple = {}, disabled, children, style, ...props }, ref) => {",
        "({ ripple: propsRipple = {}, disabled, children, style, onFocus, onBlur, ...props }, ref) => {",
        1,
    )
    if "const [tvFocused, setTvFocused] = useState(false)" not in source:
        source = source.replace(
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
            1,
        )
    source = source.replace(
        """      disabled={disabled}
      style={StyleSheet.compose({ opacity: disabled ? 0.3 : 1 }, style)}
      {...props}""",
        """      disabled={disabled}
      focusable
      onFocus={handleFocus}
      onBlur={handleBlur}
      style={StyleSheet.compose(
        StyleSheet.compose({ opacity: disabled ? 0.3 : 1 }, style),
        tvFocused ? { borderWidth: 2, borderColor: theme['c-primary-font-active'], borderRadius: 6 } : undefined,
      )}
      {...props}""",
        1,
    )
    if "focusable" not in source or "tvFocused" not in source:
        raise SystemExit("Failed to patch shared Button.tsx focus handling")
    target.write_text(source, encoding="utf-8")

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
        style={[styles.menuItem, tvFocused ? { borderWidth: 2, borderColor: theme['c-primary-font-active'], borderRadius: 6 } : undefined]}
        onPress={() => { onPress(id) }}
      >"""
    if old_open in source:
        source = source.replace(old_open, new_open, 1)
    if "focusable" not in source:
        raise SystemExit(f"Failed to add focusable navigation item: {relative_path}")
    target.write_text(source, encoding="utf-8")


def patch_player_typography() -> None:
    title = ROOT / "src/components/player/PlayerBar/components/Title.tsx"
    source = title.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "<Text color={theme['c-font-label']} numberOfLines={1}>{title}</Text>",
        "<Text color={theme['c-font-label']} numberOfLines={2} size={22}>{title}</Text>",
        "TV player title typography",
    )
    title.write_text(source, encoding="utf-8")

    status = ROOT / "src/components/player/PlayerBar/components/Status.tsx"
    source = status.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "return <Text numberOfLines={1} size={12}>{status}</Text>",
        "return <Text numberOfLines={2} size={18}>{status}</Text>",
        "TV player lyric typography",
    )
    status.write_text(source, encoding="utf-8")

    play_info = ROOT / "src/components/player/PlayerBar/components/PlayInfo.tsx"
    source = play_info.read_text(encoding="utf-8")
    source = replace_once(source, "const FONT_SIZE = 13", "const FONT_SIZE = 16", "TV player time typography")
    play_info.write_text(source, encoding="utf-8")

def patch_android_abis() -> None:
    path = ROOT / "android/app/build.gradle"
    source = path.read_text(encoding="utf-8")
    source = replace_once(source, 'return value ? value.split(",") : ["armeabi-v7a", "x86", "x86_64", "arm64-v8a"]', 'return value ? value.split(",") : ["x86", "x86_64"]', "default Android TV ABIs")
    source = replace_once(source, "universalApk true  // If true, also generate a universal APK", "universalApk false // Deliver only the two requested Intel ABI APKs", "disable universal APK")
    path.write_text(source, encoding="utf-8")

def patch_my_lists() -> None:
    path = ROOT / "src/screens/Home/Views/Mylist/MyList/List.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { memo, useEffect, useRef } from 'react'", "import { memo, useEffect, useRef, useState } from 'react'", 1)
    source = replace_once(source, "const ITEM_HEIGHT = scaleSizeH(40)", "const ITEM_HEIGHT = scaleSizeH(60)", "playlist row height")
    source = replace_once(source, "  const theme = useTheme()\n  const moreButtonRef", "  const theme = useTheme()\n  const [nameFocused, setNameFocused] = useState(false)\n  const [moreFocused, setMoreFocused] = useState(false)\n  const moreButtonRef", "playlist focus state")
    source = replace_once(source, '<TouchableOpacity style={styles.listName} onPress={handlePress}>', '<TouchableOpacity focusable onFocus={() => setNameFocused(true)} onBlur={() => setNameFocused(false)} style={[styles.listName, nameFocused ? styles.tvFocused : undefined]} onPress={handlePress}>', "playlist name focus")
    source = replace_once(source, '<TouchableOpacity onPress={handleShowMenu} ref={moreButtonRef} style={styles.listMoreBtn}>', '<TouchableOpacity focusable onFocus={() => setMoreFocused(true)} onBlur={() => setMoreFocused(false)} onPress={handleShowMenu} ref={moreButtonRef} style={[styles.listMoreBtn, moreFocused ? styles.tvFocused : undefined]}>', "playlist menu focus")
    source = replace_once(source, "const styles = createStyle({\n  container:", "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#FFFFFF', borderRadius: 6 },\n  container:", "playlist focus style")
    source = replace_once(source, "    width: 36,", "    width: 52,", "playlist menu target")
    path.write_text(source, encoding="utf-8")

    path = ROOT / "src/screens/Home/Views/Mylist/MusicList/ListItem.tsx"
    source = path.read_text(encoding="utf-8")
    source = source.replace("import { memo, useRef } from 'react'", "import { memo, useRef, useState } from 'react'", 1)
    source = replace_once(source, "  const theme = useTheme()\n\n  const isSelected", "  const theme = useTheme()\n  const [itemFocused, setItemFocused] = useState(false)\n  const [moreFocused, setMoreFocused] = useState(false)\n\n  const isSelected", "song row focus state")
    source = replace_once(source, '<TouchableOpacity style={styles.listItemLeft} onPress=', '<TouchableOpacity focusable onFocus={() => setItemFocused(true)} onBlur={() => setItemFocused(false)} style={[styles.listItemLeft, itemFocused ? styles.tvFocused : undefined]} onPress=', "song row focus")
    source = replace_once(source, '<TouchableOpacity onPress={handleShowMenu} ref={moreButtonRef} style={styles.moreButton}>', '<TouchableOpacity focusable onFocus={() => setMoreFocused(true)} onBlur={() => setMoreFocused(false)} onPress={handleShowMenu} ref={moreButtonRef} style={[styles.moreButton, moreFocused ? styles.tvFocused : undefined]}>', "song menu focus")
    source = replace_once(source, "const styles = createStyle({\n  listItem:", "const styles = createStyle({\n  tvFocused: { borderWidth: 2, borderColor: '#FFFFFF', borderRadius: 6 },\n  listItem:", "song row focus style")
    source = replace_once(source, "    height: '80%',\n    paddingLeft: 16,\n    paddingRight: 16,", "    height: '100%',\n    minWidth: 52,\n    paddingLeft: 12,\n    paddingRight: 12,", "song menu target")
    path.write_text(source, encoding="utf-8")

patch_button()
patch_player_controls()
patch_player_bar()
patch_player_typography()
patch_my_lists()
patch_home_layout()
patch_android_abis()
print("Applied TV remote focus, home layout, and x86/x86_64-only ABI configuration.")
