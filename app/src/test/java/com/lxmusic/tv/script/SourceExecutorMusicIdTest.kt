package com.lxmusic.tv.script

import org.junit.Assert.assertEquals
import org.junit.Test

class SourceExecutorMusicIdTest {

    @Test
    fun `custom platform ids preserve underscores and full value`() {
        assertEquals(
            "catalog_song_2026_part_a",
            normalizeMusicIdForPlatform("catalog_song_2026_part_a", "indie-radio")
        )
    }

    @Test
    fun `custom platform ids without underscores remain unchanged`() {
        assertEquals("song-123", normalizeMusicIdForPlatform("song-123", "custom"))
    }

    @Test
    fun `QQ combined ids retain existing normalization`() {
        assertEquals("songmid123", normalizeMusicIdForPlatform("songmid123_medi amid".replace(" ", ""), "tx"))
    }

    @Test
    fun `Kugou combined ids retain existing normalization`() {
        assertEquals("hash123", normalizeMusicIdForPlatform("hash123_album456", "kg"))
    }
}
