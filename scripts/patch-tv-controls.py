#!/usr/bin/env python3
"""Apply Android TV remote focus and touch-target adaptations to LX Music RN UI."""
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
      <Icon name={modeIcons[togglePlayMethod] || 'list-loop'} color={theme['c-button-font']} size={BTN_SIZE} />
    </TouchableOpacity>
  )
}

const styles = createStyle({""", "insert playback mode control")
    source = replace_once(source, "      <PlayNextBtn />\n    </>", "      <PlayNextBtn />\n      <PlayModeBtn />\n    </>", "render playback mode control")
    source = replace_once(source, "    width: 46,\n    height: 46,", "    width: 60,\n    height: 60,", "player control target")
    source = replace_once(source, "const styles = createStyle({\n  cotrolBtn: {", "const styles = createStyle({\n  focusedControl: { borderWidth: 2, borderColor: '#FFFFFF', borderRadius: 30 },\n  cotrolBtn: {", "player focus style")
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
    pic.write_text(source, encoding="utf-8")


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
      style={[styles.menuItem, active ? styles.activeItem : undefined, focused ? styles.focusedItem : undefined]}
    >
      <Icon name={icon} size={20} color={active || focused ? '#16866A' : theme['c-font-label']} />
      <Text size={14} color={active || focused ? '#16866A' : theme['c-font-label']}>{t(id)}</Text>
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
        <Icon name="logo" color="#16866A" size={25} />
        <Text size={18} color="#16866A" style={styles.logoText}>Music</Text>
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
    height: 76,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    paddingHorizontal: 24,
    flexGrow: 0,
    flexShrink: 0,
  },
  logo: {
    width: 150,
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
    gap: 8,
  },
  menuItem: {
    height: 48,
    minWidth: 104,
    paddingHorizontal: 14,
    borderRadius: 9,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 9,
  },
  activeItem: {
    backgroundColor: 'transparent',
  },
  focusedItem: {
    borderWidth: 2,
    borderColor: '#16866A',
  },
})
""", encoding="utf-8")

patch_home_layout()
patch_player_controls()
patch_player_bar()
print("Applied TV layout relocation and remote focus adaptations.")
