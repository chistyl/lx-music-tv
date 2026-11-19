package com.lxmusic.tv.data.source

import com.lxmusic.tv.data.model.SourceBrowseActionResult
import com.lxmusic.tv.data.model.SourceBrowseFieldMap
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SourceBrowseItemMapperTest {

    private val parser = SourceBrowsePayloadParser()
    private val mapper = SourceBrowseItemMapper()

    @Test
    fun `maps custom nested response using explicit paths`() {
        val parsed = parser.parse(
            sourceId = "source-a",
            platformKey = "indie-radio",
            action = "loadCollections",
            rawJson = """{"data":{"collections":[{"key":"c1","meta":{"title":"精選歌單","owner":"編輯部"},"image":"https://img.example/a.jpg","total":"18"}]}}"""
        ) as SourceBrowseActionResult.Success

        val items = mapper.map(
            parsed.payload,
            SourceBrowseFieldMap(
                collectionPath = "data.collections",
                idPath = "key",
                titlePath = "meta.title",
                subtitlePath = "meta.owner",
                coverPath = "image",
                countPath = "total"
            )
        )

        assertEquals(1, items.size)
        assertEquals("c1", items[0].id)
        assertEquals("精選歌單", items[0].title)
        assertEquals("編輯部", items[0].subtitle)
        assertEquals(18, items[0].count)
        assertEquals("indie-radio", items[0].platformKey)
        assertEquals("source-a", items[0].sourceId)
    }

    @Test
    fun `supports root arrays and indexed paths`() {
        val parsed = parser.parse(
            "source-b", "custom", "searchCatalog",
            """[{"id":"x","names":["首選","別名"],"length":215000},{"id":"y","names":["第二首"],"length":180000}]"""
        ) as SourceBrowseActionResult.Success

        val items = mapper.map(
            parsed.payload,
            SourceBrowseFieldMap(
                idPath = "id",
                titlePath = "names[0]",
                durationPath = "length"
            )
        )

        assertEquals(2, items.size)
        assertEquals("首選", items[0].title)
        assertEquals(215000L, items[0].durationMs)
    }

    @Test
    fun `skips entries missing required id or title`() {
        val parsed = parser.parse(
            "source-c", "custom", "list",
            """[{"id":"ok","title":"有效"},{"id":"missing-title"},{"title":"missing-id"}]"""
        ) as SourceBrowseActionResult.Success

        val items = mapper.map(
            parsed.payload,
            SourceBrowseFieldMap(idPath = "id", titlePath = "title")
        )

        assertEquals(1, items.size)
        assertEquals("ok", items[0].id)
    }

    @Test
    fun `returns empty list when configured collection path is absent`() {
        val parsed = parser.parse("source-d", "custom", "list", """{"other":[]}""")
            as SourceBrowseActionResult.Success
        val items = mapper.map(
            parsed.payload,
            SourceBrowseFieldMap(collectionPath = "data.items", idPath = "id", titlePath = "name")
        )
        assertTrue(items.isEmpty())
    }
    @Test
    fun `maps explicit song playback metadata without guessing list fields`() {
        val parsed = parser.parse(
            "source-song", "indie-radio", "playlistDetail",
            """[{"catalogId":"pl-1","display":"清單名稱","track":{"mid":"song-9","title":"夜空","artist":"歌手甲","album":"星光","cover":"https://img.example/song.jpg","duration":201000}}]"""
        ) as SourceBrowseActionResult.Success

        val items = mapper.map(
            parsed.payload,
            SourceBrowseFieldMap(
                idPath = "catalogId",
                titlePath = "display",
                songIdPath = "track.mid",
                songNamePath = "track.title",
                singerPath = "track.artist",
                songAlbumNamePath = "track.album",
                songPicPath = "track.cover",
                songDurationPath = "track.duration"
            )
        )

        assertEquals(1, items.size)
        val song = items[0].toSongOrNull()
        assertEquals("song-9", song?.id)
        assertEquals("indie-radio", song?.platformKey)
        assertEquals("夜空", song?.name)
        assertEquals("歌手甲", song?.singer)
        assertEquals("星光", song?.albumName)
        assertEquals(201000L, song?.duration)
    }

}
