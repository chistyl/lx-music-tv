from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")
home = ROOT / "src/screens/Home/Horizontal/index.tsx"
aside = ROOT / "src/screens/Home/Horizontal/Aside.tsx"
player = ROOT / "src/components/player/PlayerBar/index.tsx"

# patch-tv-controls.py runs first and supplies the TV-specific top navigation,
# player focus states, vertical player composition, and the initial layout.
source = home.read_text(encoding="utf-8")
old_layout = """const styles = createStyle({
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
new_layout = """const styles = createStyle({
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
if old_layout not in source:
    if new_layout not in source:
        raise SystemExit("Run154 stopped: expected TV-layout output from patch-tv-controls.py was not found")
else:
    source = source.replace(old_layout, new_layout, 1)
    home.write_text(source, encoding="utf-8")

# Refine the already-horizontal, focusable navigation without replacing its logic.
source = aside.read_text(encoding="utf-8")
for old, new, label in (
    ('<Text size={18} color={theme[\'c-primary-font-active\']} style={styles.logoText}>Music</Text>',
     '<Text size={18} color={theme[\'c-primary-font-active\']} style={styles.logoText}>LX Music TV</Text>', "brand label"),
    ("height: 72,", "height: 78,", "navigation height"),
    ("width: 138,", "width: 178,", "brand width"),
):
    if old in source:
        source = source.replace(old, new, 1)
    elif new not in source:
        raise SystemExit(f"Run154 stopped: expected navigation {label} anchor not found")
aside.write_text(source, encoding="utf-8")

# patch-tv-controls.py already makes the home player vertical and focusable.
# Enlarge only the home cover; keep the detail-page cover unchanged.
source = player.read_text(encoding="utf-8")
old = "<Pic isHome={isHome} size={isHome ? 120 : 46} />"
new = "<Pic isHome={isHome} size={isHome ? 210 : 46} />"
if old in source:
    source = source.replace(old, new, 1)
elif new not in source:
    raise SystemExit("Run154 stopped: expected TV player cover-size prop not found")
player.write_text(source, encoding="utf-8")

print("Run154 reference layout applied: top navigation, left content, right vertical player; existing routes and remote controls retained.")
