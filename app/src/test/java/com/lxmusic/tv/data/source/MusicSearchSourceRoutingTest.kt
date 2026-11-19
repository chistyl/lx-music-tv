package com.lxmusic.tv.data.source

import com.lxmusic.tv.data.model.AudioQuality
import com.lxmusic.tv.data.model.MusicPlatform
import com.lxmusic.tv.data.model.MusicSource
import com.lxmusic.tv.data.model.MusicItem
import org.junit.Assert.assertEquals
import org.junit.Test

class MusicSearchSourceRoutingTest {

    private fun source(id: String, name: String) = MusicSource(
        id = id,
        name = name,
        description = null,
        version = null,
        author = null,
        homepage = null,
        scriptContent = "",
        isEnabled = true
    )

    @Test
    fun `preferred source is attempted before other platform sources`() {
        val first = source("source-a", "A")
        val preferred = source("source-b", "B")
        val third = source("source-c", "C")

        assertEquals(
            listOf(preferred, first, third),
            prioritizeMusicSources(listOf(first, preferred, third), "source-b")
        )
    }

    @Test
    fun `missing preferred source preserves enabled order`() {
        val first = source("source-a", "A")
        val second = source("source-b", "B")

        assertEquals(
            listOf(first, second),
            prioritizeMusicSources(listOf(first, second), "removed-source")
        )
    }

    @Test
    fun `music item conversion preserves custom platform and source identity`() {
        val item = MusicItem(
            id = "catalog_song_2026_part_a",
            name = "測試歌曲",
            artist = "測試歌手",
            album = "測試專輯",
            duration = 180000L,
            platform = "indie-radio",
            sourceId = "source-custom",
            url = null,
            picUrl = null,
            lyricUrl = null
        )

        val song = item.toSong()

        assertEquals("catalog_song_2026_part_a", song.id)
        assertEquals("indie-radio", song.platformKey)
        assertEquals(MusicPlatform.LOCAL, song.platform)
        assertEquals("source-custom", song.sourceId)
        assertEquals(listOf(AudioQuality.QUALITY_128K, AudioQuality.QUALITY_320K, AudioQuality.FLAC), song.quality)
    }
}
