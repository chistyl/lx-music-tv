package com.lxmusic.tv.presentation.lyrics

import com.github.houbb.opencc4j.util.ZhTwConverterUtil

/**
 * 將播放畫面中的簡體中文歌詞轉為台灣繁體中文。
 *
 * 只轉換歌詞文字，不接觸 LRC 時間標記、歌曲來源資料或 metadata。
 * 含日文假名的行保留原文，避免將日文漢字誤套用中文轉換規則。
 */
internal object TraditionalChineseConverter {
    private val japaneseKana = Regex("[\\u3040-\\u30FF\\u31F0-\\u31FF]")

    fun convert(text: String): String {
        if (text.isBlank() || japaneseKana.containsMatchIn(text)) return text
        return ZhTwConverterUtil.toTraditional(text)
    }
}
