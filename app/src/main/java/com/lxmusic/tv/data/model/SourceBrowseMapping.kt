package com.lxmusic.tv.data.model

/**
 * 由使用者／音源整合設定提供的 JSON 欄位路徑。
 * 不設任何平台預設欄位名稱，避免把某一音源格式誤當成通用協議。
 */
data class SourceBrowseFieldMap(
    val collectionPath: String = "",
    val idPath: String,
    val titlePath: String,
    val subtitlePath: String? = null,
    val coverPath: String? = null,
    val countPath: String? = null,
    val descriptionPath: String? = null,
    val durationPath: String? = null,
    val albumPath: String? = null
)

/**
 * 已依明確欄位對照表轉換的自訂音源瀏覽項目。
 * 以 platformKey 保留非內建平台識別，不回退成 LOCAL。
 */
data class SourceBrowseItem(
    val id: String,
    val title: String,
    val platformKey: String,
    val sourceId: String,
    val action: String,
    val subtitle: String? = null,
    val coverUrl: String? = null,
    val count: Int? = null,
    val description: String? = null,
    val durationMs: Long? = null,
    val album: String? = null
)
