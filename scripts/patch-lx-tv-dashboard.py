from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")
target = ROOT / "src/screens/Home/Horizontal/Main.tsx"
source = target.read_text(encoding="utf-8")

# Do not disguise two complete feature pages as a dashboard. Keep their original
# navigation destinations intact until the dedicated data-backed TV dashboard is
# implemented and tested as independent components.
source = source.replace(
    "import { View } from 'react-native'\nimport { createStyle } from '@/utils/tools'\n",
    "",
)
start = source.find("const TVHomeDashboard = () => (")
if start >= 0:
    end = source.find("\nconst Main = () => {", start)
    if end < 0:
        raise SystemExit("Could not locate Main component after temporary dashboard")
    source = source[:start] + source[end + 1:]
source = source.replace(
    "case 'nav_songlist': return <TVHomeDashboard />",
    "case 'nav_songlist': return <SongList />",
)
target.write_text(source, encoding="utf-8")
print("Restored the original Songlist and Ranking destinations; removed the invalid page-in-page dashboard.")
