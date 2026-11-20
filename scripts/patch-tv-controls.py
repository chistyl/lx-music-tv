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


def patch_songlist_reference_style() -> None:
    root = ROOT / "src/screens/Home/Views/SongList"

    # The category column uses plain text rows, not large filled buttons.
    group = root / "TagList/TagGroup.tsx"
    group.write_text("""import { View, TouchableOpacity } from 'react-native'
import { type TagInfoItem } from '@/store/songlist/state'
import { useTheme } from '@/store/theme/hook'
import { createStyle } from '@/utils/tools'
import Text from '@/components/common/Text'

export interface TagGroupProps {
  name: string
  list: TagInfoItem[]
  onTagChange: (name: string, id: string) => void
  activeId: string
}

export default ({ name, list, onTagChange, activeId }: TagGroupProps) => {
  const theme = useTheme()
  return (
    <View>
      {name ? <Text style={styles.tagTypeTitle} color={theme['c-font-label']}>{name}</Text> : null}
      <View style={styles.tagTypeList}>
        {list.map(item => {
          const active = activeId == item.id
          return (
            <TouchableOpacity
              key={item.id}
              focusable
              onPress={() => onTagChange(item.name, item.id)}
              style={styles.tagButton}
            >
              <Text style={styles.tagButtonText} color={active ? '#55AD8B' : theme['c-font']}>{item.name}</Text>
            </TouchableOpacity>
          )
        })}
      </View>
    </View>
  )
}

const styles = createStyle({
  tagTypeTitle: { marginTop: 20, marginBottom: 10, fontSize: 16 },
  tagTypeList: { flexDirection: 'column', width: '100%' },
  tagButton: {
    width: '100%',
    minHeight: 48,
    justifyContent: 'center',
    paddingHorizontal: 12,
    marginBottom: 2,
    backgroundColor: 'transparent',
  },
  tagButtonText: { fontSize: 17 },
})
""", encoding="utf-8")

    tag_list = root / "TagList/List.tsx"
    source = tag_list.read_text(encoding="utf-8")
    source = source.replace(
        "<ScrollView style={{ flexShrink: 1, flexGrow: 0 }} keyboardShouldPersistTaps={'always'}>",
        "<ScrollView style={{ flex: 1, width: '100%' }} contentContainerStyle={{ paddingBottom: 24 }} keyboardShouldPersistTaps={'always'}>",
        1,
    )
    source = source.replace("    paddingLeft: 15,", "    paddingLeft: 18,\n    paddingRight: 12,", 1)
    tag_list.write_text(source, encoding="utf-8")

    # The upstream API returns playlist cards. Render them as compact TV rows,
    # preserving the original detail navigation and playlist data.
    list_item = root / "components/Songlist/ListItem.tsx"
    list_item.write_text("""import { memo, useState } from 'react'
import { View, TouchableOpacity } from 'react-native'
import { createStyle } from '@/utils/tools'
import { type ListInfoItem } from '@/store/songlist/state'
import Text from '@/components/common/Text'
import { NAV_SHEAR_NATIVE_IDS } from '@/config/constant'
import { useTheme } from '@/store/theme/hook'
import Image from '@/components/common/Image'

export default memo(({ item, index, width, showSource, onPress }: {
  item: ListInfoItem
  index: number
  showSource: boolean
  width: number
  onPress: (item: ListInfoItem, index: number) => void
}) => {
  const theme = useTheme()
  const [focused, setFocused] = useState(false)
  const handlePress = () => onPress(item, index)
  return item.source ? (
    <TouchableOpacity
      focusable
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      onPress={handlePress}
      style={[styles.row, { width: width - 18, borderBottomColor: theme['c-border-background'] }, focused ? styles.focused : undefined]}
    >
      <Text style={styles.index} color={theme['c-font-label']}>{index + 1}</Text>
      <Image url={item.img} nativeID={`${NAV_SHEAR_NATIVE_IDS.songlistDetail_pic}_from_${item.id}`} style={styles.cover} />
      <View style={styles.info}>
        <Text style={styles.title} numberOfLines={1}>{item.name}</Text>
        <Text style={styles.subtitle} color={theme['c-font-label']} numberOfLines={1}>{item.author || item.desc || item.source}</Text>
      </View>
      {showSource ? <Text style={styles.source} color={theme['c-font-label']}>{item.source}</Text> : null}
    </TouchableOpacity>
  ) : null
})

const styles = createStyle({
  row: {
    minHeight: 78,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    borderBottomWidth: 1,
    backgroundColor: 'transparent',
  },
  focused: { backgroundColor: '#E8F5EF', borderRadius: 6 },
  index: { width: 34, fontSize: 16 },
  cover: { width: 56, height: 56, borderRadius: 4 },
  info: { flex: 1, minWidth: 0, paddingLeft: 16, paddingRight: 10 },
  title: { fontSize: 18 },
  subtitle: { fontSize: 14, marginTop: 5 },
  source: { fontSize: 13 },
})
""", encoding="utf-8")

    list_file = root / "components/Songlist/List.tsx"
    source = list_file.read_text(encoding="utf-8")
    source = source.replace("const MIN_WIDTH = scaleSizeW(110)", "const MIN_WIDTH = scaleSizeW(900)", 1)
    source = source.replace("const GAP = scaleSizeW(20)", "const GAP = scaleSizeW(12)", 1)
    source = source.replace("const num = Math.max(Math.floor(width / computedItemWidth), 2)", "const num = 1", 1)
    source = source.replace("    let whiteItemNum = (list.length % rowInfo.num)", "    let whiteItemNum = 0 // TV songlist is a single-column row list\n    /* let whiteItemNum = (list.length % rowInfo.num)", 1)
    source = source.replace("    return list\n  }, [currentList, rowInfo])", "    return list\n    */\n  }, [currentList, rowInfo])", 1)
    source = source.replace("                columnWrapperStyle={{ justifyContent: 'space-evenly' }}\n                numColumns={rowInfo.num}", "                numColumns={1}", 1)
    source = source.replace("    paddingLeft: 10,\n    paddingRight: 10,", "    paddingLeft: 8,\n    paddingRight: 8,", 1)
    list_file.write_text(source, encoding="utf-8")

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




def patch_songlist_three_pane() -> None:
    # Keep the native LX Music tag and song data components, but pin the tag
    # categories beside the song list instead of hiding them in a swipe drawer.
    root = ROOT / "src/screens/Home/Views/SongList"
    index = root / "index.tsx"
    index.write_text("""import { View } from 'react-native'
import Content from './Content'
import TagList from './TagList'
import { createStyle } from '@/utils/tools'

export default () => (
  <View style={styles.container}>
    <View style={styles.categories}>
      <TagList />
    </View>
    <View style={styles.songs}>
      <Content />
    </View>
  </View>
)

const styles = createStyle({
  container: {
    flex: 1,
    flexDirection: 'row',
    overflow: 'hidden',
  },
  categories: {
    width: '26%',
    minWidth: 190,
    maxWidth: 330,
    flexGrow: 0,
    flexShrink: 0,
    borderRightWidth: 1,
    borderRightColor: '#E6ECE9',
    overflow: 'hidden',
  },
  songs: {
    flex: 1,
    minWidth: 0,
    overflow: 'hidden',
  },
})
""", encoding="utf-8")

    tag_index = root / "TagList/index.tsx"
    source = tag_index.read_text(encoding="utf-8")
    source = source.replace("const [visible, setVisible] = useState(false)", "const [visible, setVisible] = useState(true)", 1)
    source = source.replace("    global.app_event.hideSonglistTagList()\n    requestAnimationFrame(() => {", "    requestAnimationFrame(() => {", 1)
    if "global.app_event.hideSonglistTagList()" in source:
        source = source.replace("    global.app_event.hideSonglistTagList()\n", "", 1)
    tag_index.write_text(source, encoding="utf-8")

    tag_list = root / "TagList/List.tsx"
    source = tag_list.read_text(encoding="utf-8")
    source = source.replace(
        "<ScrollView style={{ flexShrink: 1, flexGrow: 0 }} keyboardShouldPersistTaps={'always'}>",
        "<ScrollView style={{ flex: 1, width: '100%' }} keyboardShouldPersistTaps={'always'}>",
        1,
    )
    tag_list.write_text(source, encoding="utf-8")

    tag_group = root / "TagList/TagGroup.tsx"
    source = tag_group.read_text(encoding="utf-8")
    source = source.replace(
        "  tagTypeList: {\n    flexDirection: 'row',\n    flexWrap: 'wrap',\n  },",
        "  tagTypeList: {\n    flexDirection: 'column',\n    width: '100%',\n  },",
        1,
    )
    source = source.replace(
        "    marginRight: 10,\n    marginBottom: 10,",
        "    width: '100%',\n    minHeight: 42,\n    justifyContent: 'center',\n    marginBottom: 4,\n    backgroundColor: 'transparent',",
        1,
    )
    source = source.replace(
        "    paddingTop: 8,\n    paddingBottom: 8,",
        "    paddingTop: 8,\n    paddingBottom: 8,",
        1,
    )
    source = source.replace(
        "    fontSize: 13,",
        "    fontSize: 18,",
        1,
    )
    tag_group.write_text(source, encoding="utf-8")

    content = root / "Content.tsx"
    source = content.read_text(encoding="utf-8")
    source = source.replace(
        "      listRef.current?.loadList(info.source, info.sortId, info.tagId)",
        "      listRef.current?.loadList(info.source, info.sortId, info.tagId)\n      global.app_event.showSonglistTagList(info.source, info.tagId)",
        1,
    )
    content.write_text(source, encoding="utf-8")

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
          <Main />
        </View>
      </View>
    </View>
  </>
)
"""
    source = replace_once(source, old_layout, new_layout, "home horizontal layout")
    home.write_text(source, encoding="utf-8")

    # Open the home screen on Song Lists by default.
    common_state = ROOT / "src/store/common/state.ts"
    state_source = common_state.read_text(encoding="utf-8")
    state_source = replace_once(
        state_source,
        "  navActiveId: 'nav_search',\n  lastNavActiveId: 'nav_search',",
        "  navActiveId: 'nav_songlist',\n  lastNavActiveId: 'nav_songlist',",
        "TV home default leaderboard",
    )
    common_state.write_text(state_source, encoding="utf-8")

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
patch_songlist_three_pane()
patch_songlist_reference_style()
patch_button()
patch_player_controls()
patch_player_bar()
patch_my_lists()
print("Applied TV layout relocation and remote focus adaptations.")
