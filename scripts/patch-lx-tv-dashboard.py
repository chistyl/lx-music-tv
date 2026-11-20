from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")
target = ROOT / "src/screens/Home/Horizontal/Main.tsx"
source = target.read_text(encoding="utf-8")

if "const TVHomeDashboard = () =>" not in source:
    source = source.replace(
        "import { useEffect, useMemo, useState } from 'react'\n",
        "import { useEffect, useMemo, useState } from 'react'\nimport { View } from 'react-native'\nimport { createStyle } from '@/utils/tools'\n",
        1,
    )
    source = source.replace(
        "const Main = () => {",
        """const TVHomeDashboard = () => (
  <View style={styles.dashboard}>
    <View style={styles.primaryColumn}>
      <SongList />
    </View>
    <View style={styles.secondaryColumn}>
      <Leaderboard />
    </View>
  </View>
)

const styles = createStyle({
  dashboard: {
    flex: 1,
    minHeight: 0,
    flexDirection: 'row',
    paddingHorizontal: 18,
    paddingTop: 12,
    paddingBottom: 16,
    gap: 16,
    overflow: 'hidden',
  },
  primaryColumn: {
    flex: 1.55,
    minWidth: 0,
    overflow: 'hidden',
  },
  secondaryColumn: {
    flex: 1,
    minWidth: 0,
    overflow: 'hidden',
  },
})

const Main = () => {""",
        1,
    )
    source = source.replace(
        "case 'nav_songlist': return <SongList />",
        "case 'nav_songlist': return <TVHomeDashboard />",
        1,
    )
target.write_text(source, encoding="utf-8")
print("Applied TV home dashboard: playlist and ranking content in separate remote-navigable columns.")
