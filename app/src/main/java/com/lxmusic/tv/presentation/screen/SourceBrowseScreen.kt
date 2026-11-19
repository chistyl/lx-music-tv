package com.lxmusic.tv.presentation.screen

import android.content.Context
import org.json.JSONObject
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.lxmusic.tv.data.model.SourceBrowseItem
import com.lxmusic.tv.data.model.Song
import com.lxmusic.tv.data.model.SourceActionOption
import com.lxmusic.tv.data.model.SourceBrowseFieldMap
import com.lxmusic.tv.presentation.component.lxBackButtonFocus
import com.lxmusic.tv.presentation.component.lxSelectorFocus
import com.lxmusic.tv.presentation.theme.LXPrimary
import com.lxmusic.tv.presentation.theme.LXSurfaceMain
import com.lxmusic.tv.presentation.theme.LXTextPrimary
import com.lxmusic.tv.presentation.theme.LXTextSecondary

/** 自訂音源瀏覽結果頁。此頁只顯示已明確映射的通用項目，不推測歌曲播放資料。 */
@Composable
fun SourceBrowseScreen(
    items: List<SourceBrowseItem>,
    loading: Boolean,
    error: String?,
    onBack: () -> Unit,
    onPlaySong: (Song) -> Unit = {},
    declaredActions: List<SourceActionOption> = emptyList(),
    canGoBack: Boolean = false,
    onBackLevel: () -> Unit = {},
    onLoadBrowseAction: (SourceActionOption, String, SourceBrowseFieldMap, Boolean, Boolean) -> Unit = { _, _, _, _, _ -> },
    onFocusFloatingBall: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val backRequester = remember { FocusRequester() }
    val context = LocalContext.current
    var selectedItem by remember { mutableStateOf<SourceBrowseItem?>(null) }
    var requestContextItem by remember { mutableStateOf<SourceBrowseItem?>(null) }
    var activeBrowseAction by remember { mutableStateOf<SourceActionOption?>(null) }
    var activePage by remember { mutableIntStateOf(1) }
    BackHandler(onBack = onBack)
    LaunchedEffect(items, activeBrowseAction) {
        if (activeBrowseAction != null && items.isNotEmpty()) selectedItem = items.first()
    }

    Column(
        modifier = modifier.fillMaxSize().background(LXSurfaceMain).padding(28.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
            IconButton(
                onClick = onBack,
                modifier = Modifier.focusRequester(backRequester).lxBackButtonFocus()
                    .size(52.dp)
                    .then(Modifier)
            ) {
                Icon(Icons.Default.ArrowBack, contentDescription = "返回", tint = LXTextPrimary)
            }
            Spacer(Modifier.width(16.dp))
            Column(Modifier.weight(1f)) {
                Text("自訂音源瀏覽", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = LXTextPrimary)
                Text("依照已保存的欄位映射呈現資料", fontSize = 14.sp, color = LXTextSecondary)
            }
            if (canGoBack) {
                OutlinedButton(
                    onClick = {
                        onBackLevel()
                        selectedItem = null
                        requestContextItem = null
                        activeBrowseAction = null
                        activePage = 1
                    },
                    modifier = Modifier.height(44.dp).lxSelectorFocus(shape = RoundedCornerShape(8.dp), glow = false, animated = false)
                ) { Text("上一層") }
            }
            Text("${items.size} 筆", fontSize = 16.sp, color = LXTextSecondary)
        }

        when {
            loading -> Box(Modifier.fillMaxWidth().weight(1f), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = LXPrimary)
            }
            error != null -> Text(error, color = MaterialTheme.colorScheme.error, fontSize = 16.sp)
            items.isEmpty() -> Text("目前沒有可顯示的瀏覽項目，請返回音源管理頁執行欄位映射。", color = LXTextSecondary)
            else -> Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                LazyColumn(
                    modifier = Modifier.weight(1.25f),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                    contentPadding = PaddingValues(bottom = 24.dp)
                ) {
                    items(items, key = { "${it.sourceId}:${it.platformKey}:${it.action}:${it.id}" }) { item ->
                        val selected = selectedItem?.id == item.id &&
                            selectedItem?.sourceId == item.sourceId &&
                            selectedItem?.platformKey == item.platformKey
                        Row(
                            modifier = Modifier.fillMaxWidth()
                                .background(if (selected) LXPrimary.copy(alpha = 0.14f) else Color.White, RoundedCornerShape(12.dp))
                                .lxSelectorFocus(shape = RoundedCornerShape(12.dp), glow = false, animated = false)
                                .clickable { selectedItem = item; requestContextItem = item; activeBrowseAction = null; activePage = 1 }
                                .focusable()
                                .padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(Icons.Default.MusicNote, contentDescription = null, tint = LXPrimary, modifier = Modifier.size(30.dp))
                            Spacer(Modifier.width(14.dp))
                            Column(Modifier.weight(1f)) {
                                Text(item.title, color = LXTextPrimary, fontSize = 18.sp, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                item.subtitle?.takeIf { it.isNotBlank() }?.let {
                                    Text(it, color = LXTextSecondary, fontSize = 13.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                }
                            }
                            item.count?.let { Text("$it", color = LXTextSecondary, fontSize = 13.sp) }
                        }
                    }
                }

                Card(
                    modifier = Modifier.weight(0.85f).fillMaxHeight(),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(22.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text("項目資訊", color = LXTextPrimary, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                        val item = selectedItem
                        if (item == null) {
                            Text("使用遙控器選取左側項目以查看詳細資訊。", color = LXTextSecondary, fontSize = 15.sp)
                        } else {
                            Text(item.title, color = LXTextPrimary, fontSize = 22.sp, fontWeight = FontWeight.Bold)
                            item.subtitle?.let { Text(it, color = LXTextSecondary, fontSize = 15.sp) }
                            item.description?.takeIf { it.isNotBlank() }?.let {
                                Text(it, color = LXTextPrimary, fontSize = 14.sp, maxLines = 8, overflow = TextOverflow.Ellipsis)
                            }
                            item.album?.let { Text("專輯：$it", color = LXTextSecondary, fontSize = 14.sp) }
                            item.count?.let { Text("數量：$it", color = LXTextSecondary, fontSize = 14.sp) }
                            Divider()
                            Text("平台：${item.platformKey}", color = LXTextSecondary, fontSize = 12.sp)
                            Text("音源：${item.sourceId}", color = LXTextSecondary, fontSize = 12.sp)
                            Text("Action：${item.action}", color = LXTextSecondary, fontSize = 12.sp)
                            val compatibleActions = declaredActions.filter {
                                it.sourceId == item.sourceId && it.platformKey == item.platformKey && it.action != item.action
                            }
                            if (compatibleActions.isNotEmpty()) {
                                Divider()
                                Text("可用的下一層 Action", color = LXTextPrimary, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                                Text("請先在音源管理頁為該 Action 保存請求 JSON 與欄位映射。", color = LXTextSecondary, fontSize = 12.sp)
                                compatibleActions.forEach { option ->
                                    val config = readSavedMapping(context, option)
                                    val fields = config?.let { parseSavedFields(it) }
                                    if (config != null && fields != null) {
                                        Button(
                                            onClick = {
                                                val request = buildItemRequest(config.optString("requestJson", "{}"), item, 1)
                                                activeBrowseAction = option
                                                requestContextItem = item
                                                activePage = 1
                                                onLoadBrowseAction(option, request, fields, false, true)
                                            },
                                            modifier = Modifier.fillMaxWidth().height(46.dp)
                                                .lxSelectorFocus(shape = RoundedCornerShape(8.dp), glow = false, animated = false),
                                            colors = ButtonDefaults.buttonColors(containerColor = LXPrimary)
                                        ) { Text("載入：${option.action}") }
                                    }
                                }
                            }
                            activeBrowseAction?.let { option ->
                                if (option.sourceId == item.sourceId && option.platformKey == item.platformKey) {
                                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                        Text("目前：${option.action} · 第 ${activePage} 頁", color = LXTextSecondary, fontSize = 12.sp)
                                        Button(
                                            onClick = {
                                                val config = readSavedMapping(context, option)
                                                val fields = config?.let { parseSavedFields(it) }
                                                if (config != null && fields != null) {
                                                    val nextPage = activePage + 1
                                                    onLoadBrowseAction(option, buildItemRequest(config.optString("requestJson", "{}"), requestContextItem ?: item, nextPage), fields, true, false)
                                                    activePage = nextPage
                                                }
                                            },
                                            modifier = Modifier.height(42.dp).lxSelectorFocus(shape = RoundedCornerShape(8.dp), glow = false, animated = false),
                                            colors = ButtonDefaults.buttonColors(containerColor = LXPrimary)
                                        ) { Text("下一頁") }
                                    }
                                }
                            }
                            val playableSong = item.toSongOrNull()
                            if (playableSong != null) {
                                Button(
                                    onClick = { onPlaySong(playableSong) },
                                    modifier = Modifier.fillMaxWidth().height(50.dp)
                                        .lxSelectorFocus(shape = RoundedCornerShape(10.dp), glow = false, animated = false),
                                    colors = ButtonDefaults.buttonColors(containerColor = LXPrimary)
                                ) {
                                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                                    Spacer(Modifier.width(8.dp))
                                    Text("播放這首歌曲")
                                }
                                Text("歌曲 ID、名稱及歌手均已明確映射，可交由既有音源播放流程解析。", color = LXTextSecondary, fontSize = 13.sp)
                            } else {
                                Text("目前為瀏覽資料項目；若要播放，請在音源管理頁明確設定歌曲 ID、名稱及歌手欄位。", color = LXTextSecondary, fontSize = 13.sp)
                            }
                        }
                    }
                }
            }
        }
    }
}

private fun readSavedMapping(context: Context, option: SourceActionOption): JSONObject? {
    val key = "mapping_${option.sourceId}_${option.platformKey}_${option.action}"
    return try {
        context.getSharedPreferences("lx_source_browse_mappings", Context.MODE_PRIVATE)
            .getString(key, null)?.let(::JSONObject)
    } catch (_: Exception) { null }
}

private fun parseSavedFields(config: JSONObject): SourceBrowseFieldMap? {
    val id = config.optString("idPath").takeIf { it.isNotBlank() } ?: return null
    val title = config.optString("titlePath").takeIf { it.isNotBlank() } ?: return null
    fun optional(key: String) = config.optString(key).takeIf { it.isNotBlank() }
    return SourceBrowseFieldMap(
        collectionPath = config.optString("collectionPath"),
        idPath = id,
        titlePath = title,
        subtitlePath = optional("subtitlePath"),
        coverPath = optional("coverPath"),
        countPath = optional("countPath"),
        descriptionPath = optional("descriptionPath"),
        durationPath = optional("durationPath"),
        albumPath = optional("albumPath"),
        songIdPath = optional("songIdPath"),
        songNamePath = optional("songNamePath"),
        singerPath = optional("singerPath"),
        songAlbumNamePath = optional("songAlbumNamePath"),
        songAlbumIdPath = optional("songAlbumIdPath"),
        songPicPath = optional("songPicPath"),
        songDurationPath = optional("songDurationPath")
    )
}

private fun buildItemRequest(template: String, item: SourceBrowseItem, page: Int): String {
    return template
        .replace("{{item.id}}", JSONObject.quote(item.id))
        .replace("{{item.title}}", JSONObject.quote(item.title))
        .replace("{{item.subtitle}}", JSONObject.quote(item.subtitle.orEmpty()))
        .replace("{{page}}", page.toString())
}
