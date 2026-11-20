from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")

# Add a real Home destination while preserving the original Songlist and Ranking pages.
constant = ROOT / "src/config/constant.ts"
source = constant.read_text(encoding="utf-8")
anchor = "export const NAV_MENUS = [\n"
if anchor not in source:
    raise SystemExit("NAV_MENUS anchor not found")
if "{ id: 'nav_home', icon: 'home' }" not in source:
    source = source.replace(anchor, anchor + "  { id: 'nav_home', icon: 'home' },\n", 1)
constant.write_text(source, encoding="utf-8")

dashboard = ROOT / "src/screens/Home/Horizontal/TVHomeDashboard.tsx"
dashboard.write_text("""import { useEffect, useState } from 'react'
import { ScrollView, TouchableOpacity, View } from 'react-native'
import { useTheme } from '@/store/theme/hook'
import Text from '@/components/common/Text'
import Image from '@/components/common/Image'
import { createStyle } from '@/utils/tools'
import musicSdk from '@/utils/musicSdk'
import { getSongListSetting, saveSongListSetting, getLeaderboardSetting, saveLeaderboardSetting } from '@/utils/data'
import { setNavActiveId } from '@/core/common'

type SongListCard = { id: string, name: string, img?: string, source: LX.OnlineSource, author?: string }
type BoardCard = { id: string, name: string, bangid: string }
type SongCard = { id: string, name: string, singer?: string, pic?: string }

export default () => {
  const theme = useTheme()
  const [lists, setLists] = useState<SongListCard[]>([])
  const [boards, setBoards] = useState<BoardCard[]>([])
  const [songs, setSongs] = useState<SongCard[]>([])
  const [listSetting, setListSetting] = useState<{ source: LX.OnlineSource, sortId: string, tagId: string } | null>(null)
  const [boardSetting, setBoardSetting] = useState<{ source: LX.OnlineSource, boardId: string } | null>(null)

  useEffect(() => {
    let alive = true
    void (async() => {
      try {
        const [ls, bs] = await Promise.all([getSongListSetting(), getLeaderboardSetting()])
        if (!alive) return
        setListSetting(ls)
        setBoardSetting(bs)
        const source = musicSdk[ls.source]
        const listResult = await source?.songList.getList(ls.sortId, ls.tagId, 1)
        if (alive && listResult?.list) setLists(listResult.list.slice(0, 6).map(item => ({ ...item, source: ls.source })))
        const boardSource = musicSdk[bs.source]
        const boardResult = await boardSource?.leaderboard.getBoards()
        if (!alive || !boardResult?.list?.length) return
        setBoards(boardResult.list.slice(0, 5))
        const selected = boardResult.list.find(item => item.id === bs.boardId) ?? boardResult.list[0]
        const detail = await boardSource?.leaderboard.getList(selected.bangid, 1)
        if (alive && detail?.list) setSongs(detail.list.slice(0, 8).map(item => ({
          id: item.id,
          name: item.name,
          singer: item.singer,
          pic: item.pic,
        })))
      } catch (error) {
        console.warn('TV dashboard data load failed', error)
      }
    })()
    return () => { alive = false }
  }, [])

  const openSonglists = () => setNavActiveId('nav_songlist')
  const openRanking = async(board: BoardCard) => {
    if (boardSetting) await saveLeaderboardSetting({ source: boardSetting.source, boardId: board.id })
    setNavActiveId('nav_top')
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <View style={styles.sectionHeader}>
        <Text size={22} color={theme['c-font']} style={styles.heading}>熱門歌單</Text>
        <TouchableOpacity focusable onPress={openSonglists}><Text color={theme['c-primary-font-active']}>更多歌單　›</Text></TouchableOpacity>
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.cardRow}>
        {lists.map(item => (
          <TouchableOpacity key={item.id} focusable activeOpacity={0.8} onPress={async() => {
            if (listSetting) await saveSongListSetting({ source: item.source, sortId: listSetting.sortId, tagId: listSetting.tagId })
            openSonglists()
          }} style={styles.playlistCard}>
            <Image url={item.img ?? ''} style={styles.cover} />
            <Text color={theme['c-font']} numberOfLines={2}>{item.name}</Text>
            <Text color={theme['c-font-label']} size={11} numberOfLines={1}>{item.author ?? ''}</Text>
          </TouchableOpacity>
        ))}
        {lists.length === 0 ? <Text color={theme['c-font-label']}>正在載入歌單…</Text> : null}
      </ScrollView>

      <View style={styles.sectionHeader}>
        <Text size={22} color={theme['c-font']} style={styles.heading}>排行榜</Text>
        <TouchableOpacity focusable onPress={() => setNavActiveId('nav_top')}><Text color={theme['c-primary-font-active']}>完整排行榜　›</Text></TouchableOpacity>
      </View>
      <View style={styles.boardRow}>
        {boards.map((board, index) => (
          <TouchableOpacity key={board.id} focusable activeOpacity={0.8} onPress={() => { void openRanking(board) }} style={[styles.boardCard, { borderColor: theme['c-border-background'] }]}>
            <Text size={24} color={theme['c-primary-font-active']}>{String(index + 1).padStart(2, '0')}</Text>
            <Text color={theme['c-font']} numberOfLines={2}>{board.name}</Text>
          </TouchableOpacity>
        ))}
        {boards.length === 0 ? <Text color={theme['c-font-label']}>正在載入排行榜…</Text> : null}
      </View>

      <View style={styles.sectionHeader}>
        <Text size={22} color={theme['c-font']} style={styles.heading}>推薦歌曲</Text>
        <TouchableOpacity focusable onPress={() => setNavActiveId('nav_top')}><Text color={theme['c-primary-font-active']}>查看榜單　›</Text></TouchableOpacity>
      </View>
      <View style={styles.songList}>
        {songs.map((song, index) => (
          <TouchableOpacity key={song.id} focusable activeOpacity={0.8} onPress={() => setNavActiveId('nav_top')} style={[styles.songRow, { borderBottomColor: theme['c-border-background'] }]}>
            <Text color={theme['c-font-label']} style={styles.songIndex}>{String(index + 1).padStart(2, '0')}</Text>
            {song.pic ? <Image url={song.pic} style={styles.songCover} /> : <View style={styles.songCover} />}
            <View style={styles.songMeta}>
              <Text color={theme['c-font']} numberOfLines={1}>{song.name}</Text>
              <Text color={theme['c-font-label']} size={11} numberOfLines={1}>{song.singer ?? ''}</Text>
            </View>
          </TouchableOpacity>
        ))}
        {songs.length === 0 ? <Text color={theme['c-font-label']}>正在載入推薦歌曲…</Text> : null}
      </View>
    </ScrollView>
  )
}

const styles = createStyle({
  container: { flex: 1, minWidth: 0 },
  content: { paddingHorizontal: 24, paddingTop: 18, paddingBottom: 28, gap: 14 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 8 },
  heading: { fontWeight: '700' },
  cardRow: { flexDirection: 'row', gap: 14, paddingVertical: 6, paddingRight: 12 },
  playlistCard: { width: 150, gap: 6, padding: 6, borderRadius: 10 },
  cover: { width: 138, height: 104, borderRadius: 8 },
  boardRow: { flexDirection: 'row', gap: 12, paddingVertical: 6 },
  boardCard: { flex: 1, minWidth: 90, minHeight: 92, padding: 12, borderWidth: 1, borderRadius: 10, justifyContent: 'space-between' },
  songList: { gap: 2 },
  songRow: { minHeight: 58, flexDirection: 'row', alignItems: 'center', gap: 12, borderBottomWidth: 1, paddingVertical: 6 },
  songIndex: { width: 24, textAlign: 'center' },
  songCover: { width: 44, height: 44, borderRadius: 6 },
  songMeta: { flex: 1, gap: 3 },
})
""", encoding="utf-8")

main = ROOT / "src/screens/Home/Horizontal/Main.tsx"
source = main.read_text(encoding="utf-8")
if "import TVHomeDashboard from './TVHomeDashboard'" not in source:
    source = source.replace("import Setting from '../Views/Setting'\n", "import Setting from '../Views/Setting'\nimport TVHomeDashboard from './TVHomeDashboard'\n", 1)
source = source.replace("    switch (id) {\n", "    switch (id) {\n      case 'nav_home': return <TVHomeDashboard />\n", 1)
main.write_text(source, encoding="utf-8")

print("Installed a data-backed TV Home dashboard with separate playlist, ranking, and recommended-song sections.")
