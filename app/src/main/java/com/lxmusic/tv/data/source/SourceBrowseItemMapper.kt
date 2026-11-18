package com.lxmusic.tv.data.source

import com.lxmusic.tv.data.model.SourceBrowseFieldMap
import com.lxmusic.tv.data.model.SourceBrowseItem
import com.lxmusic.tv.data.model.SourceBrowsePayload
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive

/**
 * 依明確提供的 JSON path 對照表，將自訂音源資料映射為通用瀏覽項目。
 *
 * path 支援 object dot path 與 array index，例如 data.items、result.list[0]。
 * 欄位名稱不會依平台猜測；必要欄位 id/title 缺漏的項目會略過。
 */
class SourceBrowseItemMapper {

    fun map(
        payload: SourceBrowsePayload,
        fields: SourceBrowseFieldMap
    ): List<SourceBrowseItem> {
        val collection = if (fields.collectionPath.isBlank()) {
            payload.rawData
        } else {
            readPath(payload.rawData, fields.collectionPath)
                ?: return emptyList()
        }

        val elements = when (collection) {
            is JsonArray -> collection.toList()
            is JsonObject -> listOf(collection)
            else -> emptyList()
        }

        return elements.mapNotNull { item ->
            val id = readPath(item, fields.idPath)?.asText()?.takeIf { it.isNotBlank() }
                ?: return@mapNotNull null
            val title = readPath(item, fields.titlePath)?.asText()?.takeIf { it.isNotBlank() }
                ?: return@mapNotNull null

            SourceBrowseItem(
                id = id,
                title = title,
                platformKey = payload.platformKey,
                sourceId = payload.sourceId,
                action = payload.action,
                subtitle = fields.subtitlePath?.let { readPath(item, it)?.asText() },
                coverUrl = fields.coverPath?.let { readPath(item, it)?.asText() },
                count = fields.countPath?.let { readPath(item, it)?.asText()?.toIntOrNull() },
                description = fields.descriptionPath?.let { readPath(item, it)?.asText() },
                durationMs = fields.durationPath?.let { readPath(item, it)?.asText()?.toLongOrNull() },
                album = fields.albumPath?.let { readPath(item, it)?.asText() }
            )
        }
    }

    private fun readPath(root: JsonElement, path: String): JsonElement? {
        if (path.isBlank()) return root
        val tokens = Regex("""[^.\[\]]+|\[(\d+)\]""")
            .findAll(path)
            .map { match -> match.groups[1]?.value ?: match.value }
            .toList()
        if (tokens.isEmpty()) return null

        var current: JsonElement = root
        for (token in tokens) {
            current = when (current) {
                is JsonObject -> current[token] ?: return null
                is JsonArray -> {
                    val index = token.toIntOrNull() ?: return null
                    current.getOrNull(index) ?: return null
                }
                else -> return null
            }
        }
        return current.takeUnless { it is JsonNull }
    }

    private fun JsonElement.asText(): String? = when (this) {
        JsonNull -> null
        is JsonPrimitive -> content
        else -> toString()
    }
}
