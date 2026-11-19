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
    val albumPath: String? = null,
    // 歌曲播放資料必須由使用者明確映射；不沿用清單 ID/title 猜測。
    val songIdPath: String? = null,
    val songNamePath: String? = null,
    val singerPath: String? = null,
    val songAlbumNamePath: String? = null,
    val songAlbumIdPath: String? = null,
    val songPicPath: String? = null,
    val songDurationPath: String? = null
)

sealed class SourceBrowseItemsResult {
    data class Success(val items: List<SourceBrowseItem>) : SourceBrowseItemsResult()
    data class Error(val message: String) : SourceBrowseItemsResult()
}

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
    val album: String? = null,
    val songId: String? = null,
    val songName: String? = null,
    val singer: String? = null,
    val songAlbumName: String? = null,
    val songAlbumId: String? = null,
    val songPicUrl: String? = null,
    val songDurationMs: Long? = null
) {
    /** 只有明確映射了歌曲 ID、歌名與歌手，才允許進入既有播放流程。 */
    fun toSongOrNull(): Song? {
        val mappedId = songId?.takeIf { it.isNotBlank() } ?: return null
        val mappedName = songName?.takeIf { it.isNotBlank() } ?: return null
        val mappedSinger = singer?.takeIf { it.isNotBlank() } ?: return null
        val mappedPlatform = MusicPlatform.entries.firstOrNull { it.key == platformKey } ?: MusicPlatform.LOCAL
        return Song(
            id = mappedId,
            name = mappedName,
            singer = mappedSinger,
            albumName = songAlbumName ?: album,
            albumId = songAlbumId,
            picUrl = songPicUrl ?: coverUrl,
            duration = songDurationMs ?: durationMs,
            platform = mappedPlatform,
            platformKey = platformKey
        )
    }
}
