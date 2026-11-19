package com.lxmusic.tv.script

import android.util.Log
import com.lxmusic.tv.data.model.*
import com.lxmusic.tv.data.source.SourceProtocol
import com.lxmusic.tv.data.source.SourceProtocolDetector
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.json.JSONObject

/**
 * 播放源执行器
 *
 * 参考 lx-music-desktop 的 UserApi 模块实现:
 * 1. 脚本执行后，通过 send(EVENT_NAMES.inited, { sources }) 宣告支持的源
 * 2. 应用通过 on(EVENT_NAMES.request, handler) 注册的 handler 处理请求
 * 3. 请求格式: { source: 'kw', action: 'musicUrl', info: { type: '320k', musicInfo: {...} } }
 * 4. handler 必须返回 Promise，resolve 值为 URL 字符串
 *
 * 支持两种模式:
 * 1. 传统函数调用模式: 脚本定义 search/getMusicUrl/getLyric 等全局函数
 * 2. 事件驱动模式（洛雪音乐标准）: 脚本通过 on(EVENT_NAMES.request, handler) 注册处理器
 *    通过 send(EVENT_NAMES.inited, data) 宣告初始化完成
 */
class SourceExecutor(
    private val javaScriptEngine: JavaScriptEngine
) {

    companion object {
        private const val TAG = "LX-SourceExecutor"
    }

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    // 是否使用事件驱动模式
    private var useEventDrivenModel = false

    // 从 inited 事件中提取的源信息
    private var sourceInfoFromInit: MutableMap<String, Any> = mutableMapOf()

    /**
     * 初始化播放源脚本
     *
     * 流程（参考 lx-music-desktop）:
     * 1. 执行脚本 → 脚本调用 on(EVENT_NAMES.request, handler) 注册处理器
     * 2. 脚本调用 send(EVENT_NAMES.inited, { sources }) 宣告初始化完成
     * 3. 检查 initEventData 和 eventHandlers 判断模式
     */
    suspend fun initializeSource(scriptContent: String): SourceExecutionResult = withContext(Dispatchers.IO) {
        // 每次切換腳本都先清除上一支腳本的平台/action metadata，避免跨腳本誤用。
        useEventDrivenModel = false
        sourceInfoFromInit.clear()
        try {
            Log.i(TAG, "===== 初始化播放源 =====")
            Log.i(TAG, "脚本长度: ${scriptContent.length}")

            // 执行脚本
            Log.i(TAG, "执行脚本...")
            val result = javaScriptEngine.executeScript(scriptContent)

            when (result) {
                is JavaScriptResult.Success -> {
                    Log.i(TAG, "脚本执行成功")

                    // 等待异步操作完成
                    // 注意：由于我们使用 runBlocking 同步执行 HTTP 请求，
                    // send() 和 on() 应该在脚本执行期间就已经被调用
                    // 但为了安全，还是等待一下
                    kotlinx.coroutines.delay(100)

                    Log.i(TAG, "检查初始化状态...")
                    Log.i(TAG, "  initEventData: ${if (javaScriptEngine.getInitEventData() != null) "已收到" else "未收到"}")
                    Log.i(TAG, "  已注册事件处理器: ${getRegisteredEventNames()}")

                    // 检查是否是事件驱动模式
                    val initEventData = javaScriptEngine.getInitEventData()
                    if (initEventData is org.json.JSONObject) {
                        // 事件驱动模式：脚本已通过 send(EVENT_NAMES.inited, data) 初始化
                        useEventDrivenModel = true
                        parseInitEventData(initEventData)
                        Log.i(TAG, "★ 播放源使用事件驱动模式初始化成功")
                        Log.i(TAG, "  支持的源: ${sourceInfoFromInit.keys}")
                        return@withContext SourceExecutionResult.Success("播放源初始化成功（事件驱动模式）")
                    }

                    // 检查是否有 EVENT_NAMES.request 的处理器注册
                    val requestHandler = javaScriptEngine.getEventHandler("request")
                    if (requestHandler != null) {
                        useEventDrivenModel = true
                        Log.i(TAG, "★ 检测到 request 事件处理器，使用事件驱动模式")
                        return@withContext SourceExecutionResult.Success("播放源初始化成功（事件驱动模式）")
                    }

                    // 传统函数模式：检查 lx 变量
                    Log.d(TAG, "未检测到事件驱动模式，尝试传统函数模式")
                    val lxCheck = javaScriptEngine.getVariable("lx")
                    when (lxCheck) {
                        is JavaScriptResult.Success -> {
                            useEventDrivenModel = false
                            Log.i(TAG, "播放源使用函数调用模式初始化成功")
                            SourceExecutionResult.Success("播放源初始化成功（函数调用模式）")
                        }
                        is JavaScriptResult.Error -> {
                            // 通用 JS 明確採用全域函式契約：
                            // search(keyword, page, limit) -> MusicItem[] 或 { musicList: MusicItem[] }
                            // getMusicUrl(musicId, quality) -> URL 字串
                            // getLyric(musicId) -> LRC 字串（選用）
                            // 不猜測其他函式名稱；CommonJS / ESM 尚需模組載入器，不能當作已支援。
                            val protocol = SourceProtocolDetector.detect(scriptContent)
                            val hasSearch = javaScriptEngine.hasFunction("search")
                            val hasMusicUrl = javaScriptEngine.hasFunction("getMusicUrl")
                            if (protocol == SourceProtocol.GENERIC_JAVASCRIPT && hasSearch && hasMusicUrl) {
                                useEventDrivenModel = false
                                Log.i(TAG, "播放源使用通用全域函式協議")
                                SourceExecutionResult.Success("播放源初始化成功（通用函式協議）")
                            } else {
                                Log.e(TAG, "播放源初始化失败: ${lxCheck.message}")
                                SourceExecutionResult.Error(
                                    "播放源缺少可識別的音源協議：通用 JS 必須同時提供 search() 與 getMusicUrl()；CommonJS/ESM 尚未支援"
                                )
                            }
                        }
                    }
                }
                is JavaScriptResult.Error -> {
                    Log.e(TAG, "执行播放源脚本失败: ${result.message}")
                    SourceExecutionResult.Error("执行播放源脚本失败: ${result.message}")
                }
            }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            Log.e(TAG, "初始化播放源异常", e)
            SourceExecutionResult.Error("初始化播放源时出错: ${e.message}")
        }
    }

    /**
     * 获取已注册的事件名称列表（用于日志）
     */
    private fun getRegisteredEventNames(): String {
        return try {
            val names = mutableListOf<String>()
            if (javaScriptEngine.getEventHandler("request") != null) names.add("request")
            names.joinToString(", ").ifEmpty { "无" }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            "获取失败"
        }
    }

    /**
     * 解析 inited 事件数据，提取源信息
     *
     * 参考 lx-music-desktop preload.js handleInit:
     * info.sources[source] = {
     *   type: 'music',
     *   actions: ['musicUrl'],
     *   qualitys: ['128k', '320k', 'flac', 'flac24bit'],
     * }
     */
    private fun parseInitEventData(data: org.json.JSONObject) {
        sourceInfoFromInit.clear()
        try {
            // 提取 sources 字段
            val sources = data.optJSONObject("sources")
            if (sources != null) {
                val keys = sources.keys()
                for (key in keys) {
                    val sourceData = sources.opt(key)
                    sourceInfoFromInit[key] = sourceData
                    Log.d(TAG, "  源 '$key': $sourceData")
                }
                Log.i(TAG, "解析到 ${sourceInfoFromInit.size} 个源")
            } else {
                Log.w(TAG, "inited 数据中没有 sources 字段")
                Log.w(TAG, "  inited 数据: ${data.toString().take(200)}")
            }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            Log.e(TAG, "解析 inited 数据失败: ${e.message}", e)
        }
    }

    /**
     * 執行音源腳本明確宣告的平台 action。
     *
     * 只允許 inited.sources[platformKey].actions 中實際宣告的 action，
     * 不推測 action 名稱或 info schema；info 由呼叫端依已確認的協議提供。
     */
    suspend fun executeDeclaredAction(
        platformKey: String,
        action: String,
        info: JSONObject
    ): JavaScriptResult = withContext(Dispatchers.IO) {
        if (platformKey.isBlank()) {
            return@withContext JavaScriptResult.Error("平台代碼不可為空")
        }
        if (action.isBlank()) {
            return@withContext JavaScriptResult.Error("Action 不可為空")
        }
        if (!useEventDrivenModel) {
            return@withContext JavaScriptResult.Error("目前音源不是事件驅動模式")
        }
        val platformInfo = sourceInfoFromInit[platformKey] as? JSONObject
            ?: return@withContext JavaScriptResult.Error("音源未宣告平台：$platformKey")
        val actions = platformInfo.optJSONArray("actions")
            ?: return@withContext JavaScriptResult.Error("平台未宣告任何 action：$platformKey")
        val declared = (0 until actions.length()).any { actions.optString(it) == action }
        if (!declared) {
            return@withContext JavaScriptResult.Error("平台「$platformKey」未宣告 action「$action」")
        }

        val eventData = JSONObject().apply {
            put("source", platformKey)
            put("action", action)
            put("info", JSONObject(info.toString()))
        }
        dispatchEventRequest(eventData)
    }

    private suspend fun dispatchEventRequest(eventData: JSONObject): JavaScriptResult =
        javaScriptEngine.dispatchEvent("request", eventData)

    /**
     * 搜索音乐
     */
    suspend fun searchMusic(
        keyword: String,
        page: Int = 1,
        limit: Int = 30,
        platformKey: String? = null
    ): SourceExecutionResult = withContext(Dispatchers.IO) {
        try {
            val searchResult = if (useEventDrivenModel) {
                // LX 標準事件模式：只對腳本已宣告 search action 的平台派發搜尋請求。
                val sourceKey = sourceInfoFromInit.entries.firstOrNull { (key, value) ->
                    if (platformKey != null && key != platformKey) {
                        false
                    } else {
                        val item = value as? org.json.JSONObject
                        item?.optJSONArray("actions")?.let { actions ->
                            (0 until actions.length()).any { actions.optString(it) == "search" }
                        } == true
                    }
                }?.key
                if (sourceKey == null) {
                    return@withContext SourceExecutionResult.Error("此播放源未宣告 search action")
                }
                val eventData = JSONObject().apply {
                    put("source", sourceKey)
                    put("action", "search")
                    put("info", JSONObject().apply {
                        put("keyword", keyword)
                        put("page", page)
                        put("limit", limit)
                    })
                }
                javaScriptEngine.dispatchEvent("request", eventData)
            } else {
                javaScriptEngine.callFunction("search", arrayOf(keyword, page, limit))
            }

            when (searchResult) {
                is JavaScriptResult.Success -> {
                    val musicList = parseSearchResult(searchResult.resultString)
                    SourceExecutionResult.SearchSuccess(musicList)
                }
                is JavaScriptResult.Error -> {
                    SourceExecutionResult.Error("搜索失败: ${searchResult.message}")
                }
            }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            SourceExecutionResult.Error("搜索音乐时出错: ${e.message}")
        }
    }

    /**
     * 获取音乐播放URL
     *
     * 参考 lx-music-desktop preload.js handleRequest:
     * - action: 'musicUrl'
     * - source: 'kw'/'kg'/'tx'/'wy'/'mg'/'local'
     * - info: { type: '320k', musicInfo: { songmid: 'xxx', hash: 'xxx' } }
     * - handler 返回 Promise<string> (URL)
     */
    suspend fun getMusicUrl(
        musicId: String,
        quality: AudioQuality = AudioQuality.QUALITY_128K,
        source: String = "kw",
        // 2.8 歌曲信息：JS 源（尤其按歌名搜索的源）需要 name/singer，缺失报「没歌名搜不了」
        songName: String = "",
        singer: String = "",
        rawSongData: String? = null
    ): SourceExecutionResult = withContext(Dispatchers.IO) {
        try {
            Log.i(TAG, "获取播放URL: musicId=$musicId, quality=${quality.key}")

            if (useEventDrivenModel) {
                val platformInfo = sourceInfoFromInit[source] as? JSONObject
                    ?: return@withContext SourceExecutionResult.Error("音源未宣告平台：$source")
                val declaredActions = platformInfo.optJSONArray("actions")
                    ?: return@withContext SourceExecutionResult.Error("平台「$source」未宣告任何 action")
                val supportsMusicUrl = (0 until declaredActions.length())
                    .any { declaredActions.optString(it) == "musicUrl" }
                if (!supportsMusicUrl) {
                    return@withContext SourceExecutionResult.Error("平台「$source」未宣告 musicUrl，無法播放")
                }
                return@withContext dispatchMusicUrlRequest(musicId, quality, source, songName, singer)
            }

            // 传统函数模式
            val urlResult = javaScriptEngine.callFunction(
                "getMusicUrl",
                // 通用 JS 協議第三參數提供完整原始歌曲物件；舊函式仍可忽略第三參數。
                arrayOf(musicId, quality.key, rawSongData?.let { JSONObject(it) } ?: JSONObject().put("id", musicId))
            )

            when (urlResult) {
                is JavaScriptResult.Success -> {
                    val url = urlResult.resultString
                    if (url.isNotBlank() && url != "undefined" && url != "null") {
                        Log.i(TAG, "获取到播放URL: $url")
                        SourceExecutionResult.UrlSuccess(url)
                    } else {
                        SourceExecutionResult.Error("获取播放URL失败: 返回空URL")
                    }
                }
                is JavaScriptResult.Error -> {
                    SourceExecutionResult.Error("获取播放URL失败: ${urlResult.message}")
                }
            }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            Log.e(TAG, "获取播放URL异常", e)
            SourceExecutionResult.Error("获取播放URL时出错: ${e.message}")
        }
    }

    /**
     * 通过事件驱动模式获取播放URL
     *
     * 参考 lx-music-desktop preload.js handleRequest:
     * events.request.call(context, { source, action, info })
     *
     * @param musicId 格式通常为 "songmid" 或 "hash"（来自搜索结果的 id 字段）
     * @param quality 音质
     * @param source 音乐平台代码（kw/kg/tx/wy/mg），必须与歌曲实际平台匹配，
     *               否则 JS 源会用错误的平台 ID 请求播放地址
     */
    private suspend fun dispatchMusicUrlRequest(
        musicId: String,
        quality: AudioQuality,
        source: String = "kw",
        songName: String = "",
        singer: String = ""
    ): SourceExecutionResult = withContext(Dispatchers.IO) {
        try {
            Log.i(TAG, "[dispatchMusicUrlRequest] 开始派发 musicUrl 请求")
            Log.i(TAG, "  musicId: $musicId")
            Log.i(TAG, "  quality: ${quality.key}")
            Log.i(TAG, "  source: $source")
            Log.i(TAG, "  songName: $songName, singer: $singer")

            // 构造 musicInfo 对象
            // 参考 lx-music-desktop: info.musicInfo 包含 songmid, hash 等字段
            // 注意: musicId 可能是拼接格式（QQ: songMid_mediaMid, 酷狗: hash_albumId），
            // 而 JS 源只需要纯 ID（songmid/hash），必须拆分，否则请求拼接串会失败
            val pureId = normalizeMusicIdForPlatform(musicId, source)
            val eventData = JSONObject().apply {
                put("source", source)
                put("action", "musicUrl")
                put("info", JSONObject().apply {
                    put("type", quality.key)
                    put("musicInfo", JSONObject().apply {
                        put("songmid", pureId)
                        put("hash", pureId)
                        // 2.8 补歌曲信息：部分源（如听音音源）按歌名搜索，缺失报「没歌名搜不了」
                        if (songName.isNotEmpty()) put("name", songName)
                        if (singer.isNotEmpty()) put("singer", singer)
                        put("albumName", "")
                    })
                })
            }

            Log.d(TAG, "[dispatchMusicUrlRequest] 事件数据: $eventData")

            // 触发 request 事件
            val result = javaScriptEngine.dispatchEvent("request", eventData)

            when (result) {
                is JavaScriptResult.Success -> {
                    val url = result.resultString
                    Log.i(TAG, "[dispatchMusicUrlRequest] ★ 获取到播放URL: $url")
                    if (url.isNotBlank() && url != "undefined" && url != "null") {
                        SourceExecutionResult.UrlSuccess(url)
                    } else {
                        SourceExecutionResult.Error("获取播放URL失败: 返回空URL")
                    }
                }
                is JavaScriptResult.Error -> {
                    Log.e(TAG, "[dispatchMusicUrlRequest] 获取播放URL失败: ${result.message}")
                    SourceExecutionResult.Error("获取播放URL失败: ${result.message}")
                }
            }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            Log.e(TAG, "[dispatchMusicUrlRequest] 异常", e)
            SourceExecutionResult.Error("获取播放URL时出错: ${e.message}")
        }
    }

    /**
     * 获取歌词
     *
     * 参考 lx-music-desktop:
     * - 事件驱动模式下向源派发 { action: 'lyric', source, info: { musicInfo } } 请求，
     *   支持歌词的源返回 LRC 文本；不支持的源返回错误，由调用方 fallback 内置 API
     */
    suspend fun getLyric(
        musicId: String,
        // 2.8 补平台/歌名/歌手：歌词事件此前硬编码 source=kw 且缺 name，JS 源歌词全部失败
        source: String = "kw",
        songName: String = "",
        singer: String = ""
    ): SourceExecutionResult = withContext(Dispatchers.IO) {
        try {
            if (useEventDrivenModel) {
                // 构造 lyric 请求事件（参考 lx-music handleRequest）
                val eventData = JSONObject().apply {
                    put("source", source)
                    put("action", "lyric")
                    put("info", JSONObject().apply {
                        put("musicInfo", JSONObject().apply {
                            put("songmid", musicId)
                            put("hash", musicId)
                            if (songName.isNotEmpty()) put("name", songName)
                            if (singer.isNotEmpty()) put("singer", singer)
                            put("albumName", "")
                        })
                    })
                }
                val result = javaScriptEngine.dispatchEvent("request", eventData)
                return@withContext when (result) {
                    is JavaScriptResult.Success -> {
                        val lyric = result.resultString
                        if (lyric.isNotBlank() && lyric != "undefined" && lyric != "null") {
                            SourceExecutionResult.LyricSuccess(lyric)
                        } else {
                            SourceExecutionResult.Error("源返回空歌词")
                        }
                    }
                    is JavaScriptResult.Error -> {
                        SourceExecutionResult.Error("播放源不支持歌词: ${result.message}")
                    }
                }
            }

            val lyricResult = javaScriptEngine.callFunction(
                "getLyric",
                arrayOf(musicId)
            )

            when (lyricResult) {
                is JavaScriptResult.Success -> {
                    SourceExecutionResult.LyricSuccess(lyricResult.resultString)
                }
                is JavaScriptResult.Error -> {
                    SourceExecutionResult.Error("获取歌词失败: ${lyricResult.message}")
                }
            }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            SourceExecutionResult.Error("获取歌词时出错: ${e.message}")
        }
    }

    /**
     * 获取专辑封面
     */
    suspend fun getPicUrl(musicId: String): SourceExecutionResult = withContext(Dispatchers.IO) {
        try {
            if (useEventDrivenModel) {
                return@withContext SourceExecutionResult.Error("当前播放源不支持获取封面")
            }

            val picResult = javaScriptEngine.callFunction(
                "getPicUrl",
                arrayOf(musicId)
            )

            when (picResult) {
                is JavaScriptResult.Success -> {
                    SourceExecutionResult.PicSuccess(picResult.resultString)
                }
                is JavaScriptResult.Error -> {
                    SourceExecutionResult.Error("获取专辑封面失败: ${picResult.message}")
                }
            }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            SourceExecutionResult.Error("获取专辑封面时出错: ${e.message}")
        }
    }

    /**
     * 解析搜索结果JSON
     */
    private fun parseSearchResult(jsonStr: String): List<MusicItem> {
        return try {
            // 先保留既有 MusicItem 格式的原生解碼路徑，避免影響既有音源。
            try {
                val root = json.parseToJsonElement(jsonStr)
                val listElement = (root as? JsonObject)?.get("musicList")
                if (listElement != null) {
                    return json.decodeFromString(listElement.toString())
                }
                if (root is kotlinx.serialization.json.JsonArray) {
                    return json.decodeFromString(root.toString())
                }
            } catch (_: Exception) {
                // 欄位格式不同時，交由下方別名映射處理。
            }

            val parsedRoot = org.json.JSONTokener(jsonStr).nextValue()
            val root = parsedRoot as? JSONObject
            val rows = when (parsedRoot) {
                is org.json.JSONArray -> parsedRoot
                is JSONObject -> sequenceOf("musicList", "songs", "list", "results", "data")
                    .mapNotNull { key -> parsedRoot.opt(key) }
                    .firstOrNull { it is org.json.JSONArray } as? org.json.JSONArray
                    ?: if (parsedRoot.has("id") || parsedRoot.has("songmid") || parsedRoot.has("musicId")) {
                        org.json.JSONArray().put(parsedRoot)
                    } else null
                else -> null
            } ?: return emptyList()

            fun firstText(item: JSONObject, vararg keys: String): String {
                for (key in keys) {
                    val value = item.opt(key)
                    if (value != null && value != JSONObject.NULL) {
                        val text = when (value) {
                            is JSONObject -> value.optString("name", "")
                            is org.json.JSONArray -> (0 until value.length()).mapNotNull { index ->
                                val entry = value.opt(index)
                                when (entry) {
                                    is JSONObject -> entry.optString("name").takeIf { it.isNotBlank() }
                                    null, JSONObject.NULL -> null
                                    else -> entry.toString().takeIf { it.isNotBlank() }
                                }
                            }.joinToString("/")
                            else -> value.toString()
                        }
                        if (text.isNotBlank() && text != "null") return text
                    }
                }
                return ""
            }

            fun firstLong(item: JSONObject, vararg keys: String): Long {
                for (key in keys) {
                    val value = item.opt(key)
                    val parsed = when (value) {
                        is Number -> value.toLong()
                        else -> value?.toString()?.toLongOrNull()
                    }
                    if (parsed != null && parsed >= 0) return parsed
                }
                return 0L
            }

            buildList {
                for (index in 0 until rows.length()) {
                    val item = rows.optJSONObject(index) ?: continue
                    val id = firstText(item, "id", "songmid", "musicId", "mid", "hash", "rid", "songId")
                    val name = firstText(item, "name", "title", "songName", "musicName")
                    val artist = firstText(item, "artist", "singer", "artists", "author", "subtitle")
                    if (id.isBlank() || name.isBlank()) continue
                    val album = firstText(item, "album", "albumName", "albumname")
                        .ifBlank { null }
                    val duration = firstLong(item, "duration", "dt", "interval", "length")
                    val platform = firstText(item, "platform", "source", "sourceKey").ifBlank { "custom" }
                    val url = firstText(item, "url", "playUrl", "musicUrl").ifBlank { null }
                    val pic = firstText(item, "picUrl", "pic", "cover", "coverUrl", "artwork").ifBlank { null }
                    val lyric = firstText(item, "lyricUrl", "lyric").ifBlank { null }
                    val sourceId = firstText(item, "sourceId", "providerId").ifBlank { platform }
                    add(
                        MusicItem(
                            id = id,
                            name = name,
                            artist = artist,
                            album = album,
                            duration = duration,
                            platform = platform,
                            sourceId = sourceId,
                            url = url,
                            picUrl = pic,
                            lyricUrl = lyric,
                            rawData = item.toString()
                        )
                    )
                }
            }
        } catch (e: kotlin.coroutines.cancellation.CancellationException) { throw e } catch (e: Exception) {
            Log.e(TAG, "解析搜索結果失敗: ${e.message}", e)
            emptyList()
        }
    }

    /**
     * 释放资源
     */
    fun release() {
        useEventDrivenModel = false
        sourceInfoFromInit.clear()
        javaScriptEngine.release()
    }
}

/**
 * 源执行结果
 */
sealed class SourceExecutionResult {
    data class Success(val message: String) : SourceExecutionResult()
    data class Error(val message: String) : SourceExecutionResult()
    data class SearchSuccess(val musicList: List<MusicItem>) : SourceExecutionResult()
    data class UrlSuccess(val url: String) : SourceExecutionResult()
    data class LyricSuccess(val lyric: String) : SourceExecutionResult()
    data class PicSuccess(val picUrl: String) : SourceExecutionResult()
    data class ActionSuccess(val result: String) : SourceExecutionResult()
}

/**
 * TX 與 KG 的既有內建 ID 可能是「歌曲 ID_媒體／專輯 ID」組合格式；
 * 自訂平台 ID 不套用內建拆分規則，必須完整保留底線及原始字串。
 */
internal fun normalizeMusicIdForPlatform(musicId: String, platformKey: String): String =
    if (platformKey == "tx" || platformKey == "kg") musicId.substringBefore("_") else musicId
