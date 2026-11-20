from pathlib import Path

root = Path("upstream/lx-music-mobile-auto-source/src/screens/Home/Horizontal")
index = root / "index.tsx"
aside = root / "Aside.tsx"

source = index.read_text(encoding="utf-8")
old = """const styles = createStyle({
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
new = """const styles = createStyle({
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
    paddingHorizontal: 18,
    paddingTop: 8,
    paddingBottom: 14,
    gap: 16,
  },
  main: {
    flex: 1,
    minWidth: 0,
    overflow: 'hidden',
    borderRadius: 18,
  },
  player: {
    width: '27%',
    maxWidth: 390,
    minWidth: 280,
    flexGrow: 0,
    flexShrink: 0,
    overflow: 'hidden',
    borderRadius: 22,
    borderWidth: 1,
    borderColor: 'rgba(120, 165, 225, 0.16)',
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
if old not in source:
    raise SystemExit("Run154 layout patch stopped: Horizontal/index.tsx no longer matches the verified Run153 structure")
index.write_text(source.replace(old, new), encoding="utf-8")

source = aside.read_text(encoding="utf-8")
source = source.replace(">Music</Text>", ">LX Music TV</Text>")
source = source.replace("width: 138,", "width: 178,")
source = source.replace("height: 72,", "height: 78,")
aside.write_text(source, encoding="utf-8")

print("Run154: home navigation remains top-mounted; content now uses a wide main area with the existing player panel on the right. Existing navigation and player components are retained.")

# Layout changes are intentionally limited to the existing home and player components.
