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
    # Only relocate the existing navigation and player. Keep the original page content untouched.
    home = ROOT / "src/screens/Home/Horizontal/index.tsx"
    home.write_text("""import { View } from 'react-native'
import TopNavigation from './TopNavigation'
import LeftPlayerPanel from './LeftPlayerPanel'
import StatusBar from '@/components/common/StatusBar'
import Main from './Main'
import { createStyle } from '@/utils/tools'

const styles = createStyle({
  container: { flex: 1, flexDirection: 'column' },
  content: { flex: 1, flexDirection: 'row', overflow: 'hidden' },
  main: { flex: 1, overflow: 'hidden' },
})

export default () => (
  <>
    <StatusBar />
    <View style={styles.container}>
      <TopNavigation />
      <View style={styles.content}>
        <LeftPlayerPanel />
        <View style={styles.main}>
          <Main />
        </View>
      </View>
    </View>
  </>
)
""", encoding="utf-8")

    nav = ROOT / "src/screens/Home/Horizontal/TopNavigation.tsx"
    nav.write_text("""import { memo, useState } from 'react'
import { ScrollView, TouchableOpacity, View } from 'react-native'
import { useNavActiveId, useStatusbarHeight } from '@/store/common/hook'
import { useTheme } from '@/store/theme/hook'
import { Icon } from '@/components/common/Icon'
import Text from '@/components/common/Text'
import { createStyle } from '@/utils/tools'
import { NAV_MENUS } from '@/config/constant'
import type { InitState } from '@/store/common/state'
import { exitApp, setNavActiveId } from '@/core/common'
import { confirmDialog, exitApp as backHome } from '@/utils/tools'
import { useSettingValue } from '@/store/setting/hook'
import { useI18n } from '@/lang'

type IdType = InitState['navActiveId'] | 'nav_exit' | 'back_home'

const MenuItem = ({ id, icon, active, onPress }: {
  id: IdType, icon: string, active: boolean, onPress: (id: IdType) => void
}) => {
  const theme = useTheme()
  const t = useI18n()
  const [focused, setFocused] = useState(false)
  return (
    <TouchableOpacity
      focusable
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      onPress={() => onPress(id)}
      style={[styles.item, active ? styles.active : undefined, focused ? styles.focused : undefined]}
    >
      <Icon name={icon} size={19} color={active ? '#FFFFFF' : theme['c-font-label']} />
      <Text size={13} color={active ? '#FFFFFF' : theme['c-font-label']}>{t(id)}</Text>
    </TouchableOpacity>
  )
}

export default memo(() => {
  const activeId = useNavActiveId()
  const theme = useTheme()
  const statusBarHeight = useStatusbarHeight()
  const showBackBtn = useSettingValue('common.showBackBtn')
  const showExitBtn = useSettingValue('common.showExitBtn')

  const handlePress = (id: IdType) => {
    if (id === 'nav_exit') {
      void confirmDialog({
        message: global.i18n.t('exit_app_tip'),
        confirmButtonText: global.i18n.t('list_remove_tip_button'),
      }).then(isExit => { if (isExit) exitApp('Exit Btn') })
      return
    }
    if (id === 'back_home') { backHome(); return }
    global.app_event.changeMenuVisible(false)
    setNavActiveId(id)
  }

  return (
    <View style={[styles.container, { paddingTop: statusBarHeight, borderBottomColor: theme['c-border-background'] }]}>
      <View style={styles.logo}>
        <Icon name="logo" color={theme['c-primary-dark-100-alpha-300']} size={19} />
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.items}>
        {NAV_MENUS.map(menu => (
          <MenuItem key={menu.id} id={menu.id} icon={menu.icon} active={activeId === menu.id} onPress={handlePress} />
        ))}
        {showBackBtn ? <MenuItem id="back_home" icon="home" active={false} onPress={handlePress} /> : null}
        {showExitBtn ? <MenuItem id="nav_exit" icon="exit2" active={false} onPress={handlePress} /> : null}
      </ScrollView>
    </View>
  )
})

const styles = createStyle({
  container: {
    height: 58,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    paddingHorizontal: 14,
  },
  logo: { width: 42, alignItems: 'flex-start', justifyContent: 'center' },
  items: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  item: {
    height: 38, minWidth: 88, paddingHorizontal: 13, borderRadius: 9,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
  },
  active: { backgroundColor: '#16866A' },
  focused: { borderWidth: 2, borderColor: '#FFFFFF' },
})
""", encoding="utf-8")

    panel = ROOT / "src/screens/Home/Horizontal/LeftPlayerPanel.tsx"
    panel.write_text("""import { View } from 'react-native'
import Pic from '@/components/player/PlayerBar/components/Pic'
import Title from '@/components/player/PlayerBar/components/Title'
import PlayInfo from '@/components/player/PlayerBar/components/PlayInfo'
import ControlBtn from '@/components/player/PlayerBar/components/ControlBtn'
import { useTheme } from '@/store/theme/hook'
import { createStyle } from '@/utils/tools'

export default () => {
  const theme = useTheme()
  return (
    <View style={[styles.container, { backgroundColor: theme['c-content-background'], borderRightColor: theme['c-border-background'] }]}>
      <View style={styles.cover}><Pic isHome size={112} /></View>
      <View style={styles.title}><Title isHome /></View>
      <View style={styles.lyric}><PlayInfo isHome /></View>
      <View style={styles.controls}><ControlBtn /></View>
    </View>
  )
}

const styles = createStyle({
  container: {
    width: 224, flexGrow: 0, flexShrink: 0,
    borderRightWidth: 1, paddingHorizontal: 14, paddingVertical: 18,
    alignItems: 'center',
  },
  cover: { width: 112, height: 112, marginBottom: 16 },
  title: { width: '100%', minHeight: 34, justifyContent: 'center', alignItems: 'center' },
  lyric: { width: '100%', minHeight: 54, justifyContent: 'center', marginTop: 6 },
  controls: { width: '100%', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginTop: 12 },
})
""", encoding="utf-8")

    pic = ROOT / "src/components/player/PlayerBar/components/Pic.tsx"
    source = pic.read_text(encoding="utf-8")
    source = source.replace("export default ({ isHome }: { isHome: boolean }) => {", "export default ({ isHome, size = 46 }: { isHome: boolean, size?: number }) => {", 1)
    source = source.replace("  const musicInfo = usePlayerMusicInfo()", "  const musicInfo = usePlayerMusicInfo()" + chr(10) + "  const imageSize = scaleSizeH(size)", 1)
    source = source.replace("<Image url={musicInfo.pic} nativeID={NAV_SHEAR_NATIVE_IDS.playDetail_pic} style={styles.image} onError={handleError} />", "<Image url={musicInfo.pic} nativeID={NAV_SHEAR_NATIVE_IDS.playDetail_pic} style={{ width: imageSize, height: imageSize, borderRadius: 3 }} onError={handleError} />", 1)
    pic.write_text(source, encoding="utf-8")

patch_home_layout()
patch_button()
patch_player_controls()
patch_player_bar()
patch_my_lists()
print("Applied TV layout relocation and remote focus adaptations.")
