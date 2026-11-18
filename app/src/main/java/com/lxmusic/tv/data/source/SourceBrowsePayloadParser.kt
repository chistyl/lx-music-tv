package com.lxmusic.tv.data.source

import com.lxmusic.tv.data.model.SourceBrowseActionResult
import com.lxmusic.tv.data.model.SourceBrowsePayload
import kotlinx.serialization.json.Json

/**
 * 將腳本 Action 的 JSON 回傳值封裝為通用瀏覽資料。
 *
 * 此層刻意不推測排行榜、歌單或歌曲欄位名稱；不同音源的資料結構
 * 應由後續明確的 adapter/mapping profile 解讀。
 */
class SourceBrowsePayloadParser(
    private val json: Json = Json {
        isLenient = true
        ignoreUnknownKeys = true
    }
) {
    fun parse(
        sourceId: String,
        platformKey: String,
        action: String,
        rawJson: String
    ): SourceBrowseActionResult {
        if (sourceId.isBlank()) return SourceBrowseActionResult.Error("音源 ID 不可為空")
        if (platformKey.isBlank()) return SourceBrowseActionResult.Error("平台代碼不可為空")
        if (action.isBlank()) return SourceBrowseActionResult.Error("Action 不可為空")
        if (rawJson.isBlank()) return SourceBrowseActionResult.Error("音源未回傳資料")

        return try {
            val data = json.parseToJsonElement(rawJson)
            SourceBrowseActionResult.Success(
                SourceBrowsePayload(
                    sourceId = sourceId,
                    platformKey = platformKey,
                    action = action,
                    rawData = data
                )
            )
        } catch (e: Exception) {
            SourceBrowseActionResult.Error("音源回傳的 JSON 格式無效：${e.message ?: "未知錯誤"}")
        }
    }
}
