from pathlib import Path

root = Path("upstream/lx-music-mobile-auto-source/src/screens/Home/Horizontal")
index = root / "index.tsx"
aside = root / "Aside.tsx"

index_source = index.read_text(encoding="utf-8")
expected_imports = """import { View } from 'react-native'
import Aside from './Aside'
import PlayerBar from '@/components/player/PlayerBar'
import StatusBar from '@/components/common/StatusBar'
import Header from './Header'
import Main from './Main'
import { createStyle } from '@/utils/tools'
"""
if expected_imports not in index_source:
    raise SystemExit("Run154 stopped: upstream Horizontal/index.tsx imports differ from pinned source")

new_index = """import { View } from 'react-native'
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
    backgroundColor: '#070B12',
  },
  content: {
    flex: 1,
    minHeight: 0,
    flexDirection: 'row',
    overflow: 'hidden',
    paddingHorizontal: 22,
    paddingTop: 14,
    paddingBottom: 18,
  },
  main: {
    flex: 1,
    minWidth: 0,
    overflow: 'hidden',
    marginRight: 18,
    borderRadius: 18,
  },
  player: {
    width: '28%',
    minWidth: 290,
    maxWidth: 390,
    flexGrow: 0,
    flexShrink: 0,
    overflow: 'hidden',
    borderRadius: 22,
    borderWidth: 1,
    borderColor: 'rgba(120, 165, 225, 0.18)',
    backgroundColor: '#0D1420',
  },
})

export default () => (
  <>
    <StatusBar />
    <View style={styles.container}>
      <Aside />
      <View style={styles.content}>
        <View style={styles.main}>
          <Header />
          <Main />
        </View>
        <View style={styles.player}>
          <PlayerBar isHome />
        </View>
      </View>
    </View>
  </>
)
"""
index.write_text(new_index, encoding="utf-8")

source = aside.read_text(encoding="utf-8")
source = source.replace("const NAV_WIDTH = 68\n\n", "", 1)
source = source.replace(
    "import { Icon } from '@/components/common/Icon'\n",
    "import { Icon } from '@/components/common/Icon'\nimport Text from '@/components/common/Text'\n",
    1,
)
old_menu = """  return activeId == id
    ? <View style={styles.menuItem}>
        <View style={styles.iconContent}>
          <Icon name={icon} size={20} color={theme['c-primary-font-active']} />
        </View>
        {/* <Text style={styles.text} size={14} color={theme['c-primary-font']}>{t(id)}</Text> */}
      </View>
    : <TouchableOpacity focusable style={styles.menuItem} onPress={() => { onPress(id) }}>
        <View style={styles.iconContent}>
          <Icon name={icon} size={20} color={theme['c-font-label']} />
        </View>
        {/* <Text style={styles.text} size={14}>{t(id)}</Text> */}
      </TouchableOpacity>
"""
new_menu = """  return (
    <TouchableOpacity
      focusable
      style={{
        ...styles.menuItem,
        backgroundColor: activeId == id ? theme['c-primary-background'] : 'transparent',
        borderRadius: 12,
      }}
      onPress={() => { onPress(id) }}
      activeOpacity={0.82}
    >
      <View style={styles.iconContent}>
        <Icon
          name={icon}
          size={20}
          color={activeId == id ? theme['c-primary-font-active'] : theme['c-font-label']}
        />
      </View>
      <Text
        style={styles.text}
        size={14}
        color={activeId == id ? theme['c-primary-font-active'] : theme['c-font-label']}
      >{global.i18n.t(id)}</Text>
    </TouchableOpacity>
  )
"""
if old_menu not in source:
    raise SystemExit("Run154 stopped: MenuItem source differs from pinned upstream")
source = source.replace(old_menu, new_menu, 1)
replacements = [
    ("borderRightWidth: BorderWidths.normal,", "borderBottomWidth: BorderWidths.normal,"),
    ("paddingBottom: 10,\n    width: NAV_WIDTH,", "paddingHorizontal: 18,\n    paddingBottom: 0,\n    width: '100%',\n    flexDirection: 'row',\n    alignItems: 'center',"),
    ("paddingTop: 15,\n    paddingBottom: 15,\n    flexDirection: 'row',\n    justifyContent: 'center',", "paddingTop: 10,\n    paddingBottom: 10,\n    paddingLeft: 8,\n    paddingRight: 24,\n    flexDirection: 'row',\n    justifyContent: 'flex-start',"),
    ("menus: {\n    flex: 1,\n  },", "menus: {\n    flex: 1,\n    minWidth: 0,\n  },"),
    ("paddingBottom: 15,\n  },\n  menuItem:", "paddingBottom: 0,\n    flexDirection: 'row',\n    alignItems: 'center',\n  },\n  menuItem:"),
    ("paddingTop: 15,\n    paddingBottom: 15,", "paddingTop: 13,\n    paddingBottom: 13,\n    paddingLeft: 18,\n    paddingRight: 18,"),
    ("<ScrollView style={styles.menus}>", "<ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.menus}>"),
]
for old, new in replacements:
    if old not in source:
        raise SystemExit(f"Run154 stopped: expected Aside.tsx fragment not found: {old!r}")
    source = source.replace(old, new, 1)

source = source.replace(
    "return (\n    <View style={{ ...styles.container, borderRightColor: theme['c-border-background'] }}>",
    "return (\n    <View style={{ ...styles.container, borderBottomColor: theme['c-border-background'] }}>",
    1,
)
aside.write_text(source, encoding="utf-8")

print("Run154 layout patch applied: top horizontal navigation, left content canvas, right player panel. Existing screen routing and player actions remain connected.")
