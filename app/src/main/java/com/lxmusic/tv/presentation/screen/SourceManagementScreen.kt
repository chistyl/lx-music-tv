package com.lxmusic.tv.presentation.screen

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.type
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.lxmusic.tv.data.model.MusicSource
import com.lxmusic.tv.data.model.SourceActionOption
import com.lxmusic.tv.data.model.SourceBrowseFieldMap
import com.lxmusic.tv.data.model.SourceBrowseItem
import com.lxmusic.tv.data.source.ParseResult
import com.lxmusic.tv.data.source.ScriptParser
import com.lxmusic.tv.viewmodel.SourceImportPreview
import com.lxmusic.tv.presentation.component.lxBackButtonFocus
import com.lxmusic.tv.presentation.component.lxFocusBorder
import com.lxmusic.tv.presentation.component.lxSelectorFocus
import com.lxmusic.tv.presentation.component.requestInitialFocus
import com.lxmusic.tv.presentation.theme.LXAccentGradientBrush
import com.lxmusic.tv.presentation.theme.LXBorder
import com.lxmusic.tv.presentation.theme.LXCardDark
import com.lxmusic.tv.presentation.theme.LXOnCardDark
import com.lxmusic.tv.presentation.theme.LXOnCardDarkSecondary
import com.lxmusic.tv.presentation.theme.LXPrimary
import com.lxmusic.tv.presentation.theme.LXSuccess
import com.lxmusic.tv.presentation.theme.LXSurfaceDialog
import com.lxmusic.tv.presentation.theme.LXSurfaceMain
import com.lxmusic.tv.presentation.theme.LXSurfaceVariant
import com.lxmusic.tv.presentation.theme.LXTextPrimary
import com.lxmusic.tv.presentation.theme.LXTextSecondary

/**
 * 播放源管理界面
 * 管理导入的播放源文件，启动HTTP 伺服器
 */
@Composable
fun SourceManagementScreen(
    sources: List<MusicSource>,
    declaredActions: List<SourceActionOption> = emptyList(),
    sourceActionTestResult: String? = null,
    sourceActionTestLoading: Boolean = false,
    onExecuteDeclaredAction: (SourceActionOption, String) -> Unit = { _, _ -> },
    onClearActionTestResult: () -> Unit = {},
    sourceBrowseItems: List<SourceBrowseItem> = emptyList(),
    sourceBrowseError: String? = null,
    sourceBrowseLoading: Boolean = false,
    onLoadSourceBrowseItems: (SourceActionOption, String, SourceBrowseFieldMap) -> Unit = { _, _, _ -> },
    onClearSourceBrowseItems: () -> Unit = {},
    serverRunning: Boolean,
    serverUrl: String?,
    onToggleServer: () -> Unit,
    onToggleSource: (String, Boolean) -> Unit,
    onDeleteSource: (String) -> Unit,
    onPreviewSourceFromUrl: (String) -> Unit = {},
    sourceImportPreview: SourceImportPreview? = null,
    onConfirmImportSource: () -> Unit = {},
    onCancelImportPreview: () -> Unit = {},
    onBack: () -> Unit,
    // 2.8 返回按钮按「右键」→ 聚焦右上角悬浮播放球（悬浮层空间焦点导航不可达，需显式桥接）
    onFocusFloatingBall: () -> Unit = {},
    // 2.9 播放失败尝试切换平台开关（默认启用；开启后 JS 源解析失败时自动用同一源尝试其他平台版本）
    platformSwitchEnabled: Boolean = true,
    onTogglePlatformSwitch: (Boolean) -> Unit = {},
    modifier: Modifier = Modifier
) {
    var showDeleteDialog by remember { mutableStateOf<MusicSource?>(null) }
    var showImportDialog by remember { mutableStateOf(false) }
    // 播放源排序：启用的源按「启用顺序」排前面（优先级从高到低，先启用优先），未启用的按导入顺序排后面
    val orderedSources = remember(sources) {
        val enabled = sources.filter { it.isEnabled }
            .sortedWith(compareBy { it.enabledAt ?: it.updatedAt })
        enabled + sources.filter { !it.isEnabled }
    }
    // 进入页面时把焦点落到返回按钮，避免初始无焦点导致方向键失灵
    val backFocusRequester = remember { FocusRequester() }
    val addSourceFocusRequester = remember { FocusRequester() }
    var initialFocusRequested by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        requestInitialFocus(
            focusRequester = backFocusRequester,
            attempted = { initialFocusRequested },
            markAttempted = { initialFocusRequested = true }
        )
    }

    // 全站主题由 MainActivity 根部的 LXMusicTheme 统一提供，此处不再嵌套 LXMusicTheme
    // 整页：浅色基底 #F5F5F7 + 顶部品牌红氛围渐变（与主/侧栏一致，2.5 浅色主题）
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(LXSurfaceMain)
    ) {
            // 顶部氛围渐变叠加层（固定不随列表滚动，仿主页主区）
            Box(
                modifier = Modifier
                    .matchParentSize()
                    .background(LXAccentGradientBrush)
            )
            // 整页 LazyColumn：手机上内容多时可整体滚动，避免控件挤在一起
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Transparent)
                    .padding(horizontal = 24.dp, vertical = 24.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
            // 顶部导航栏
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(
                        onClick = onBack,
                        modifier = Modifier
                            .size(48.dp)
                            // focusRequester 必须在 focusable(IconButton) 之前
                            .focusRequester(backFocusRequester)
                            .lxBackButtonFocus()
                            // 2.8 右键 → 聚焦右上角悬浮播放球
                            .onPreviewKeyEvent { keyEvent ->
                                if (keyEvent.type == KeyEventType.KeyDown && keyEvent.key == Key.DirectionRight) {
                                    addSourceFocusRequester.requestFocus()
                                    true
                                } else false
                            }
                    ) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "返回",
                        // 2.5 浅色主题：浅底上的深色返回箭头（lxBackButtonFocus 提供焦点边框）
                        tint = LXTextPrimary,
                        modifier = Modifier.size(32.dp)
                    )
                    }

                    Spacer(modifier = Modifier.width(16.dp))

                    Text(
                        text = "音源管理",
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = LXTextPrimary
                    )
                    Spacer(modifier = Modifier.weight(1f))
                    Button(
                        onClick = { showImportDialog = true },
                        modifier = Modifier
                            .focusRequester(addSourceFocusRequester)
                            .height(48.dp)
                            .lxSelectorFocus(shape = RoundedCornerShape(12.dp), glow = false, animated = false)
                            .onPreviewKeyEvent { keyEvent ->
                                if (keyEvent.type == KeyEventType.KeyDown && keyEvent.key == Key.DirectionRight) {
                                    onFocusFloatingBall()
                                    true
                                } else false
                            },
                        colors = ButtonDefaults.buttonColors(containerColor = LXPrimary)
                    ) {
                        Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("新增音源", fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }

            // HTTP 伺服器状态
            item {
                ServerStatusCard(
                    isRunning = serverRunning,
                    serverUrl = serverUrl,
                    onToggle = onToggleServer,
                    modifier = Modifier.fillMaxWidth()
                )
            }

            // 已啟用音源明確宣告的 Action 能力清單；不預設任何平台或 Action 名稱。
            item {
                DeclaredSourceActionsCard(
                    actions = declaredActions,
                    testResult = sourceActionTestResult,
                    testLoading = sourceActionTestLoading,
                    onExecute = onExecuteDeclaredAction,
                    onClearResult = onClearActionTestResult,
                    browseItems = sourceBrowseItems,
                    browseError = sourceBrowseError,
                    browseLoading = sourceBrowseLoading,
                    onLoadBrowseItems = onLoadSourceBrowseItems,
                    onClearBrowseItems = onClearSourceBrowseItems,
                    modifier = Modifier.fillMaxWidth()
                )
            }

            // 2.9 播放失败尝试切换平台开关（开启后 JS 源解析失败时自动用同一源尝试其他平台版本）
            item {
                PlatformSwitchCard(
                    enabled = platformSwitchEnabled,
                    onToggle = onTogglePlatformSwitch,
                    modifier = Modifier.fillMaxWidth()
                )
            }

            // 播放源列表（启用的源按启用顺序排最前 = 优先级从高到低，未启用的排后）
            if (sources.isEmpty()) {
                item { EmptyState(modifier = Modifier.fillMaxWidth().height(320.dp)) }
            } else {
                // 说明：优先级 = 启用顺序
                item {
                    Text(
                        text = "已啟用的音源依「啟用順序」排列播放優先級（越前面優先級越高），播放失敗時會自動切換至下一個音源",
                        fontSize = 13.sp,
                        color = LXTextSecondary,
                        modifier = Modifier.fillMaxWidth().padding(top = 4.dp, bottom = 2.dp)
                    )
                }
                itemsIndexed(orderedSources) { index, source ->
                    SourceItem(
                        source = source,
                        // 启用源显示优先级序号（1 = 最高）
                        priority = if (source.isEnabled) index + 1 else null,
                        onToggleEnabled = { enabled -> onToggleSource(source.id, enabled) },
                        onDelete = { showDeleteDialog = source },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }

        if (showImportDialog) {
            ImportSourceDialog(
                onImport = { url ->
                    onPreviewSourceFromUrl(url)
                    showImportDialog = false
                },
                onDismiss = { showImportDialog = false }
            )
        }

        sourceImportPreview?.let { preview ->
            SourceImportPreviewDialog(
                preview = preview,
                onConfirm = onConfirmImportSource,
                onDismiss = onCancelImportPreview
            )
        }

        // 刪除確認對話框
        showDeleteDialog?.let { source ->
            DeleteConfirmDialog(
                sourceName = source.name,
                onConfirm = {
                    onDeleteSource(source.id)
                    showDeleteDialog = null
                },
                onDismiss = { showDeleteDialog = null }
            )
        }

        }
}

@Composable
private fun SourceMappingField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    required: Boolean = false
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = Modifier.fillMaxWidth()
            .lxSelectorFocus(shape = RoundedCornerShape(8.dp), glow = false, animated = false),
        label = { Text(if (required) "$label（必填）" else "$label（選填）") },
        singleLine = true,
        textStyle = androidx.compose.ui.text.TextStyle(fontSize = 14.sp),
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = LXTextPrimary,
            unfocusedTextColor = LXTextPrimary,
            focusedBorderColor = LXPrimary,
            unfocusedBorderColor = LXBorder,
            focusedLabelColor = LXPrimary,
            unfocusedLabelColor = LXTextSecondary
        )
    )
}

/**
 * 顯示目前已啟用音源明確宣告的 Action。
 * 此處只呈現能力，不推測請求參數或直接執行未知 Action。
 */
@Composable
private fun DeclaredSourceActionsCard(
    actions: List<SourceActionOption>,
    testResult: String?,
    testLoading: Boolean,
    onExecute: (SourceActionOption, String) -> Unit,
    onClearResult: () -> Unit,
    browseItems: List<SourceBrowseItem>,
    browseError: String?,
    browseLoading: Boolean,
    onLoadBrowseItems: (SourceActionOption, String, SourceBrowseFieldMap) -> Unit,
    onClearBrowseItems: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedAction by remember(actions) { mutableStateOf(actions.firstOrNull()) }
    var requestJson by remember(selectedAction) { mutableStateOf("{}") }
    var collectionPath by remember(selectedAction) { mutableStateOf("") }
    var idPath by remember(selectedAction) { mutableStateOf("") }
    var titlePath by remember(selectedAction) { mutableStateOf("") }
    var subtitlePath by remember(selectedAction) { mutableStateOf("") }
    var coverPath by remember(selectedAction) { mutableStateOf("") }
    var countPath by remember(selectedAction) { mutableStateOf("") }
    var descriptionPath by remember(selectedAction) { mutableStateOf("") }
    var durationPath by remember(selectedAction) { mutableStateOf("") }
    var albumPath by remember(selectedAction) { mutableStateOf("") }
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = LXCardDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text(
                text = "音源擴充能力",
                fontSize = 19.sp,
                fontWeight = FontWeight.Bold,
                color = LXOnCardDark
            )
            Text(
                text = "以下只列出音源腳本實際宣告的 Action；不同音源可支援不同功能。",
                fontSize = 13.sp,
                color = LXOnCardDarkSecondary
            )
            if (actions.isEmpty()) {
                Text(
                    text = "目前沒有已啟用音源宣告可用的 Action",
                    fontSize = 14.sp,
                    color = LXOnCardDarkSecondary
                )
            } else {
                actions.groupBy { Triple(it.sourceId, it.sourceName, it.platformKey to it.platformName) }
                    .forEach { (group, entries) ->
                        Column(
                            modifier = Modifier.fillMaxWidth()
                                .background(LXSurfaceVariant, RoundedCornerShape(8.dp))
                                .padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Text(
                                text = "${group.second} · ${group.third.second} (${group.third.first})",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = LXTextPrimary
                            )
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                entries.forEach { entry ->
                                    val selected = selectedAction == entry
                                    Button(
                                        onClick = {
                                            selectedAction = entry
                                            onClearResult()
                                            onClearBrowseItems()
                                        },
                                        modifier = Modifier.lxSelectorFocus(
                                            shape = RoundedCornerShape(8.dp),
                                            glow = false,
                                            animated = false
                                        ),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (selected) LXPrimary else LXSurfaceVariant,
                                            contentColor = if (selected) Color.White else LXTextPrimary
                                        ),
                                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                                    ) {
                                        Text(entry.action, fontSize = 12.sp)
                                    }
                                }
                            }
                        }
                    }

                selectedAction?.let { selected ->
                    Text(
                        text = "測試 Action：${selected.action}",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = LXOnCardDark
                    )
                    Text(
                        text = "請依該音源的腳本規格輸入 info JSON；系統不會自動猜測參數。",
                        fontSize = 12.sp,
                        color = LXOnCardDarkSecondary
                    )
                    OutlinedTextField(
                        value = requestJson,
                        onValueChange = { requestJson = it },
                        modifier = Modifier.fillMaxWidth()
                            .lxSelectorFocus(shape = RoundedCornerShape(8.dp), glow = false, animated = false),
                        label = { Text("info JSON") },
                        minLines = 3,
                        maxLines = 6,
                        textStyle = androidx.compose.ui.text.TextStyle(fontSize = 14.sp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = LXTextPrimary,
                            unfocusedTextColor = LXTextPrimary,
                            focusedBorderColor = LXPrimary,
                            unfocusedBorderColor = LXBorder,
                            focusedLabelColor = LXPrimary,
                            unfocusedLabelColor = LXTextSecondary
                        )
                    )
                    Button(
                        onClick = { onExecute(selected, requestJson) },
                        enabled = !testLoading,
                        modifier = Modifier.lxSelectorFocus(
                            shape = RoundedCornerShape(8.dp),
                            glow = false,
                            animated = false
                        ),
                        colors = ButtonDefaults.buttonColors(containerColor = LXPrimary)
                    ) {
                        Text(if (testLoading) "執行中…" else "執行測試")
                    }
                    testResult?.let { result ->
                        Column(
                            modifier = Modifier.fillMaxWidth()
                                .background(LXSurfaceVariant, RoundedCornerShape(8.dp))
                                .padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Text("回傳結果", fontWeight = FontWeight.SemiBold, color = LXTextPrimary)
                            Text(text = result, color = LXTextPrimary, fontSize = 12.sp)
                        }
                    }

                    Divider(color = LXOnCardDarkSecondary.copy(alpha = 0.35f))
                    Text("瀏覽資料欄位映射", fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = LXOnCardDark)
                    Text(
                        "依照上方 Action 回傳的 JSON 結構填寫路徑。支援 data.items、result.list[0] 等路徑；不填的選填欄位會略過。",
                        fontSize = 12.sp,
                        color = LXOnCardDarkSecondary
                    )
                    SourceMappingField("清單路徑 collectionPath", collectionPath, { collectionPath = it })
                    mappingField("項目 ID idPath", idPath, { idPath = it }, required = true)
                    mappingField("標題 titlePath", titlePath, { titlePath = it }, required = true)
                    mappingField("副標題 subtitlePath", subtitlePath, { subtitlePath = it })
                    mappingField("封面 coverPath", coverPath, { coverPath = it })
                    mappingField("數量 countPath", countPath, { countPath = it })
                    mappingField("描述 descriptionPath", descriptionPath, { descriptionPath = it })
                    mappingField("時長 durationPath", durationPath, { durationPath = it })
                    mappingField("專輯 albumPath", albumPath, { albumPath = it })

                    Button(
                        onClick = {
                            selectedAction?.let { action ->
                                onLoadBrowseItems(
                                    action,
                                    requestJson,
                                    SourceBrowseFieldMap(
                                        collectionPath = collectionPath.trim(),
                                        idPath = idPath.trim(),
                                        titlePath = titlePath.trim(),
                                        subtitlePath = subtitlePath.trim().ifBlank { null },
                                        coverPath = coverPath.trim().ifBlank { null },
                                        countPath = countPath.trim().ifBlank { null },
                                        descriptionPath = descriptionPath.trim().ifBlank { null },
                                        durationPath = durationPath.trim().ifBlank { null },
                                        albumPath = albumPath.trim().ifBlank { null }
                                    )
                                )
                            }
                        },
                        enabled = !browseLoading && selectedAction != null && idPath.isNotBlank() && titlePath.isNotBlank(),
                        modifier = Modifier.lxSelectorFocus(shape = RoundedCornerShape(8.dp), glow = false, animated = false),
                        colors = ButtonDefaults.buttonColors(containerColor = LXPrimary)
                    ) {
                        Text(if (browseLoading) "轉換中…" else "執行欄位映射")
                    }
                    browseError?.let { error ->
                        Text("映射失敗：$error", color = Color.Red, fontSize = 13.sp)
                    }
                    if (browseItems.isNotEmpty()) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("映射結果（${browseItems.size} 筆）", color = LXOnCardDark, fontWeight = FontWeight.SemiBold)
                            Spacer(modifier = Modifier.weight(1f))
                            TextButton(onClick = onClearBrowseItems) { Text("清除") }
                        }
                        browseItems.take(20).forEach { item ->
                            Column(
                                modifier = Modifier.fillMaxWidth()
                                    .background(LXSurfaceVariant, RoundedCornerShape(8.dp))
                                    .padding(10.dp),
                                verticalArrangement = Arrangement.spacedBy(3.dp)
                            ) {
                                Text(item.title, color = LXTextPrimary, fontWeight = FontWeight.SemiBold)
                                Text("ID：${item.id} · 平台：${item.platformKey}", color = LXTextSecondary, fontSize = 11.sp)
                                item.subtitle?.takeIf { it.isNotBlank() }?.let {
                                    Text(it, color = LXTextSecondary, fontSize = 12.sp)
                                }
                                item.coverUrl?.takeIf { it.isNotBlank() }?.let {
                                    Text("封面：$it", color = LXTextSecondary, fontSize = 11.sp, maxLines = 1)
                                }
                            }
                        }
                        if (browseItems.size > 20) {
                            Text("僅預覽前 20 筆，完整資料保留於瀏覽狀態。", color = LXOnCardDarkSecondary, fontSize = 11.sp)
                        }
                    }
                }
            }
        }
    }
}

/**
 * 服务器状态卡片
 */
@Composable
fun ServerStatusCard(
    isRunning: Boolean,
    serverUrl: String?,
    onToggle: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        // 2.5 浅色主题：深色卡片（仿播放页播放列表），内部文字浅色
        colors = CardDefaults.cardColors(containerColor = LXCardDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .clip(RoundedCornerShape(6.dp))
                        .background(if (isRunning) LXSuccess else LXOnCardDarkSecondary)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = "HTTP 伺服器",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Medium,
                    // 2.5 浅色主题：深卡片上的浅色文字
                    color = LXOnCardDark,
                    modifier = Modifier.weight(1f)
                )
                Switch(
                    checked = isRunning,
                    onCheckedChange = { onToggle() },
                    modifier = Modifier
                        // 与下方音源启用开关保持一致：常态透明边框，仅聚焦时主题色边框
                        .lxSelectorFocus(shape = RoundedCornerShape(10.dp), glow = false, animated = false),
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = LXPrimary,
                        uncheckedThumbColor = Color.White,
                        uncheckedTrackColor = LXOnCardDarkSecondary
                    )
                )
            }

            if (isRunning && serverUrl != null) {
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                    .clip(RoundedCornerShape(8.dp))
                    // 2.5 浅色主题：深卡片上的次级面板（白色半透明叠加）
                    .background(Color(0x22FFFFFF))
                    .clickable { }
                        .padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Link,
                        contentDescription = null,
                        tint = LXPrimary,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = serverUrl,
                        fontSize = 14.sp,
                        // 2.8 不跟随主题色：与播放源卡片二级标题同色（深卡片上的次级文字）
                        color = LXOnCardDarkSecondary,
                        modifier = Modifier.weight(1f)
                    )
                    Icon(
                        imageVector = Icons.Default.ContentCopy,
                        contentDescription = "复制",
                        tint = LXOnCardDarkSecondary,
                        modifier = Modifier.size(16.dp)
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "在手機或電腦瀏覽器中開啟上述網址，即可上傳及管理音源",
                    fontSize = 12.sp,
                    // 2.5 浅色主题：深卡片上的次级文字（白70%）
                    color = LXOnCardDarkSecondary
                )
            }
        }
    }
}

/**
 * 2.9 播放失败尝试切换平台开关卡片
 * 开启后：JS 源解析当前平台失败时，自动用同一源尝试解析该歌曲在其他平台的版本
 * （切换顺序 QQ音乐 → 网易云音乐 → 酷狗音乐 → 酷我音乐；咪咕不参与；只切换到该源已配置的平台）。
 * 与 HTTP 服务器卡片同风格（深色卡片 + Switch，焦点在 Switch 上）。
 */
@Composable
fun PlatformSwitchCard(
    enabled: Boolean,
    onToggle: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = LXCardDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "播放失敗時嘗試切換音樂平台",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = LXOnCardDark
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "JS 音源解析失敗時，自動使用同一音源嘗試其他平台版本",
                    fontSize = 12.sp,
                    color = LXOnCardDarkSecondary
                )
            }
            Spacer(modifier = Modifier.width(16.dp))
            Switch(
                checked = enabled,
                onCheckedChange = onToggle,
                modifier = Modifier
                    // 与 HTTP 服务器开关一致：常态透明边框，仅聚焦时主题色边框
                    .lxSelectorFocus(shape = RoundedCornerShape(10.dp), glow = false, animated = false),
                colors = SwitchDefaults.colors(
                    checkedThumbColor = Color.White,
                    checkedTrackColor = LXPrimary,
                    uncheckedThumbColor = Color.White,
                    uncheckedTrackColor = LXOnCardDarkSecondary
                )
            )
        }
    }
}

/**
 * 播放源列表项
 * 两行紧凑布局：第一行 图标+信息+启用开关；第二行刪除按钮
 * 手机上不拥挤，均可点击
 */
@Composable
fun SourceItem(
    source: MusicSource,
    priority: Int? = null,
    onToggleEnabled: (Boolean) -> Unit,
    onDelete: () -> Unit,
    modifier: Modifier = Modifier
) {
    val declaredPlatforms = remember(source.scriptContent) {
        when (val parsed = ScriptParser().parse(source.scriptContent)) {
            is ParseResult.Success -> parsed.platforms.keys.map { it.displayName }
            is ParseResult.Error -> emptyList()
        }
    }
    Card(
        // 卡片自身不设焦点节点：若卡片 focusable 会拦截方向键，导致遥控器
        // 无法把焦点移入卡片内部的「启用/刪除」操作（需按两次确定）。
        // 焦点直接落在内部三个操作控件上，方向键即可在它们之间切换。
        modifier = modifier,
        // 2.5 浅色主题：深色卡片（仿播放页播放列表），内部文字浅色
        colors = CardDefaults.cardColors(containerColor = LXCardDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(14.dp)
        ) {
            // 第一行：图标 + 信息 + 启用开关
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(8.dp))
                    // 2.5 浅色主题：深卡片上的次级图标底（白色半透明叠加）
                    .background(Color(0x22FFFFFF)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.MusicNote,
                        contentDescription = null,
                        tint = LXPrimary,
                        modifier = Modifier.size(22.dp)
                    )
                }

                Spacer(modifier = Modifier.width(14.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = source.name,
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Medium,
                            // 2.5 浅色主题：深卡片上的浅色文字
                            color = LXOnCardDark,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            modifier = Modifier.weight(1f, fill = false)
                        )
                        // 优先级徽标（启用源按列表顺序 1=最高）
                        priority?.let { p ->
                            Spacer(modifier = Modifier.width(8.dp))
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(LXPrimary.copy(alpha = 0.25f))
                                    .padding(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = "優先級 $p",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = LXPrimary
                                )
                            }
                        }
                    }
                    source.description?.let { desc ->
                        Text(
                            text = desc,
                            fontSize = 13.sp,
                            // 2.5 浅色主题：深卡片上的次级文字（白70%）
                            color = LXOnCardDarkSecondary,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                    Row(
                        modifier = Modifier.padding(top = 2.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        source.version?.let { ver ->
                            Text(text = "v$ver", fontSize = 12.sp, color = LXSuccess)
                        }
                        source.author?.let { auth ->
                            Text(text = "作者：$auth", fontSize = 12.sp, color = LXOnCardDarkSecondary)
                        }
                    }
                    Text(
                        text = "支援平台：" + (declaredPlatforms.takeIf { it.isNotEmpty() }?.joinToString("、") ?: "未宣告"),
                        fontSize = 12.sp,
                        color = LXOnCardDarkSecondary,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.padding(top = 3.dp)
                    )
                }

                Spacer(modifier = Modifier.width(8.dp))

                // 启用开关（第一行右侧）
                Switch(
                    checked = source.isEnabled,
                    onCheckedChange = onToggleEnabled,
                    modifier = Modifier
                        // 常态透明边框，仅聚焦时亮红边框（避免常显一圈多余边框）
                        // 关闭发光与动画：小按钮密集排列时发光/动画会背景异常
                        .lxSelectorFocus(shape = RoundedCornerShape(10.dp), glow = false, animated = false),
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = LXPrimary,
                        uncheckedThumbColor = Color.White,
                        uncheckedTrackColor = LXOnCardDarkSecondary
                    )
                )
            }

            // 音源支援平台由 JS 脚本 platforms 自行宣告；此处仅保留刪除操作。
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            ) {
                CacheActionButton(
                    text = "刪除",
                    hint = "移除此音源",
                    onClick = onDelete,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}

/**
 * 空状态
 */
@Composable
fun EmptyState(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxWidth().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.CloudOff,
            contentDescription = "沒有音源",
            tint = LXTextSecondary,
            modifier = Modifier.size(64.dp)
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "暂沒有音源",
            fontSize = 20.sp,
            fontWeight = FontWeight.Medium,
            // 2.5 浅色主题：浅底深色文字
            color = LXTextPrimary
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "启动HTTP 伺服器后，在手机/电脑浏览器中打开页面地址即可上传JS播放源文件",
            fontSize = 14.sp,
            color = LXTextSecondary,
            textAlign = TextAlign.Center
        )
    }
}

/**
 * 刪除确认对话框
 */
@Composable
fun DeleteConfirmDialog(
    sourceName: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = "确认刪除", fontWeight = FontWeight.Bold) },
        text = { Text("确定要刪除播放源 \"$sourceName\" 吗？") },
        confirmButton = {
            // 2.8 与主页「退出应用」弹窗按钮样式统一：无背景文本按钮，红字醒目
            TextButton(onClick = onConfirm) {
                Text("刪除", color = LXPrimary)
            }
        },
        dismissButton = {
            // 取消：与「后台播放」一致的无背景文本按钮
            TextButton(onClick = onDismiss) {
                Text("取消", color = LXTextPrimary)
            }
        },
        // 2.5 浅色主题：灰白底对话框（LXSurfaceDialog #F0F0F2）+ 深色文字
        containerColor = LXSurfaceDialog,
        titleContentColor = LXTextPrimary,
        textContentColor = LXTextPrimary
    )
}

/**
 * 洛雪音源匯入對話框：以遙控器可操作的單一網址欄位完成匯入。
 * 文字欄位優先取得焦點，確認/取消均可使用方向鍵切換。
 */
@Composable
fun ImportSourceDialog(
    onImport: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var sourceUrl by remember { mutableStateOf("") }
    val urlFocusRequester = remember { FocusRequester() }

    LaunchedEffect(Unit) {
        urlFocusRequester.requestFocus()
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = "匯入洛雪音源",
                fontWeight = FontWeight.Bold,
                color = LXTextPrimary
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = "輸入音源 JS 腳本的直接連結網址。匯入後會自動解析音源名稱、版本、作者及支援平台。",
                    color = LXTextSecondary,
                    fontSize = 14.sp
                )
                OutlinedTextField(
                    value = sourceUrl,
                    onValueChange = { sourceUrl = it },
                    modifier = Modifier
                        .fillMaxWidth()
                        .focusRequester(urlFocusRequester),
                    singleLine = true,
                    label = { Text("音源網址") },
                    placeholder = { Text("https://.../source.js") },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = LXPrimary,
                        cursorColor = LXPrimary
                    )
                )
                Text(
                    text = "也可以啟動下方 HTTP 伺服器，再透過手機或電腦上傳 JS 音源檔。",
                    color = LXTextSecondary,
                    fontSize = 12.sp
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { onImport(sourceUrl.trim()) },
                enabled = sourceUrl.trim().startsWith("https://", true) ||
                    sourceUrl.trim().startsWith("http://", true),
                modifier = Modifier.lxSelectorFocus(
                    shape = RoundedCornerShape(10.dp),
                    glow = false,
                    animated = false
                ),
                colors = ButtonDefaults.buttonColors(containerColor = LXPrimary)
            ) {
                Text("匯入音源")
            }
        },
        dismissButton = {
            OutlinedButton(
                onClick = onDismiss,
                modifier = Modifier.lxSelectorFocus(
                    shape = RoundedCornerShape(10.dp),
                    glow = false,
                    animated = false
                )
            ) {
                Text("取消", color = LXTextPrimary)
            }
        },
        containerColor = LXSurfaceDialog,
        titleContentColor = LXTextPrimary,
        textContentColor = LXTextPrimary
    )
}

@Composable
fun SourceImportPreviewDialog(
    preview: SourceImportPreview,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    val confirmFocusRequester = remember { FocusRequester() }
    LaunchedEffect(Unit) {
        confirmFocusRequester.requestFocus()
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text("確認匯入音源", fontWeight = FontWeight.Bold, color = LXTextPrimary)
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(9.dp)) {
                Text(
                    text = preview.name,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = LXTextPrimary
                )
                preview.description?.takeIf { it.isNotBlank() }?.let {
                    Text(it, fontSize = 13.sp, color = LXTextSecondary, maxLines = 3, overflow = TextOverflow.Ellipsis)
                }
                ImportMetadataRow("版本", preview.version ?: "未提供")
                ImportMetadataRow("作者", preview.author ?: "未提供")
                ImportMetadataRow("平台", preview.supportedPlatforms.takeIf { it.isNotEmpty() }?.joinToString("、") ?: "未辨識")
                preview.homepage?.takeIf { it.isNotBlank() }?.let {
                    ImportMetadataRow("首頁", it)
                }
                Text(
                    "確認後才會將這個 JS 音源加入清單；平台支援依腳本宣告自動辨識。",
                    fontSize = 12.sp,
                    color = LXTextSecondary
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirm,
                modifier = Modifier
                    .focusRequester(confirmFocusRequester)
                    .lxSelectorFocus(shape = RoundedCornerShape(10.dp), glow = false, animated = false),
                colors = ButtonDefaults.buttonColors(containerColor = LXPrimary)
            ) {
                Text("確認匯入")
            }
        },
        dismissButton = {
            OutlinedButton(
                onClick = onDismiss,
                modifier = Modifier.lxSelectorFocus(shape = RoundedCornerShape(10.dp), glow = false, animated = false)
            ) {
                Text("取消", color = LXTextPrimary)
            }
        },
        containerColor = LXSurfaceDialog,
        titleContentColor = LXTextPrimary,
        textContentColor = LXTextPrimary
    )
}

@Composable
private fun ImportMetadataRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top
    ) {
        Text(label, color = LXTextSecondary, fontSize = 13.sp, modifier = Modifier.width(52.dp))
        Text(value, color = LXTextPrimary, fontSize = 13.sp, modifier = Modifier.weight(1f))
    }
}
