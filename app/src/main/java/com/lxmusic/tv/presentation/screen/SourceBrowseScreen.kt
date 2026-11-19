package com.lxmusic.tv.presentation.screen

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.lxmusic.tv.data.model.SourceBrowseItem
import com.lxmusic.tv.data.model.Song
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
    onFocusFloatingBall: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val backRequester = remember { FocusRequester() }
    var selectedItem by remember(items) { mutableStateOf<SourceBrowseItem?>(null) }
    BackHandler(onBack = onBack)

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
                                .clickable { selectedItem = item }
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
                    Column(Modifier.fillMaxSize().padding(22.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
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
