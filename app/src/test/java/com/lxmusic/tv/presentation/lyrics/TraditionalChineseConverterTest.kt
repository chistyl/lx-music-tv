package com.lxmusic.tv.presentation.lyrics

import com.lxmusic.tv.presentation.screen.parseLrcWithTranslation
import org.junit.Assert.assertEquals
import org.junit.Test

class TraditionalChineseConverterTest {

    @Test
    fun convertsSimplifiedChineseToTaiwanTraditional() {
        assertEquals("這是一首關於軟體與音樂的歌", TraditionalChineseConverter.convert("这是一首关于软件与音乐的歌"))
    }

    @Test
    fun keepsExistingTraditionalChinese() {
        val text = "這是一首繁體中文歌曲"
        assertEquals(text, TraditionalChineseConverter.convert(text))
    }

    @Test
    fun keepsEnglishUnchanged() {
        val text = "Never gonna give you up"
        assertEquals(text, TraditionalChineseConverter.convert(text))
    }

    @Test
    fun keepsJapaneseKanaAndKanjiUnchanged() {
        val text = "君の心に"
        assertEquals(text, TraditionalChineseConverter.convert(text))
    }

    @Test
    fun convertsLyricsInTheActualPlayerParsingPipeline() {
        val lines = parseLrcWithTranslation(
            "[00:01.20]这是一首关于软件的歌",
            "[00:01.20]继续前进"
        )

        assertEquals(1, lines.size)
        assertEquals(1200L, lines[0].timeMs)
        assertEquals("這是一首關於軟體的歌", lines[0].text)
        assertEquals("繼續前進", lines[0].translation)
    }

    @Test
    fun convertsMainAndTranslationWithoutChangingLrcTimes() {
        val parser = LyricsParser()
        val lyrics = parser.parseWithTranslation(
            "[00:01.20]这是一首关于软件的歌\n[00:02.40]继续前进",
            "[00:01.20]這是一首關於軟體的歌\n[00:02.40]继续前进"
        )

        assertEquals(listOf(1200L, 2400L), lyrics.lines.map { it.timeMs })
        assertEquals("這是一首關於軟體的歌", lyrics.lines[0].content)
        assertEquals("這是一首關於軟體的歌", lyrics.lines[0].translation)
        assertEquals("繼續前進", lyrics.lines[1].content)
        assertEquals("繼續前進", lyrics.lines[1].translation)
    }
}
