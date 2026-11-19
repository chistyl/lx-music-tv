package com.lxmusic.tv.data.source

/**
 * 通用 JavaScript 音源協議初步識別。
 *
 * 此識別只提供相容層選擇線索，不作為匯入門檻，也不代表未知協議已可執行。
 * 新協議應新增 adapter，而不是把協議條件塞回匯入解析器。
 */
enum class SourceProtocol {
    LX_EVENT,
    COMMON_JS,
    ES_MODULE,
    GENERIC_JAVASCRIPT
}

object SourceProtocolDetector {
    fun detect(script: String): SourceProtocol {
        val normalized = script
            .replace(Regex("/\\*[\\s\\S]*?\\*/"), " ")
            .replace(Regex("(?m)//.*$"), " ")

        val hasLxHost = Regex(
            """(?:globalThis|window|global)\s*(?:\.\s*lx|\[\s*['"]lx['"]\s*])"""
        ).containsMatchIn(normalized) ||
            normalized.contains("__lx_setup__")

        if (hasLxHost) return SourceProtocol.LX_EVENT

        if (Regex("""(?m)^\s*(?:export\s+(?:default|const|function|async)|import\s+)""")
                .containsMatchIn(normalized)) {
            return SourceProtocol.ES_MODULE
        }

        if (normalized.contains("module.exports") ||
            Regex("""(?m)exports\.[A-Za-z_$]""").containsMatchIn(normalized) ||
            normalized.contains("require(")) {
            return SourceProtocol.COMMON_JS
        }

        return SourceProtocol.GENERIC_JAVASCRIPT
    }
}
