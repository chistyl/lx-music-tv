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
 * 管理导入的播放源文件，启动HTTP服务器
 */
@Composable
fun SourceManagementScreen(
    sources: List<MusicSource>,
    serverRunning: Boolean,
    serverUrl: String?,
    onToggleServer: () -> Unit,
    onToggleSource: (String, Boolean) -> Unit,
    onDeleteSource: (String) -> Unit,
    onBack: () -> Unit,
    // 2.8 返回按钮按「右键」→ 聚焦右上角悬浮播放球（悬浮层空间焦点导航不可达，需显式桥接）
    onFocusFloatingBall: () -> Unit = {},
    // 2.9 播放失败尝试切换平台开关（默认启用；开启后 JS 源解析失败时自动用同一源尝试其他平台版本）
    platformSwitchEnabled: Boolean = true,
    onTogglePlatformSwitch: (Boolean) -> Unit = {},
    modifier: Modifier = Modifier
) {
    var showDeleteDialog by remember { mutableStateOf<MusicSource?>(null) }
    // 播放源排序：启用的源按「启用顺序」排前面（优先级从高到低，先启用优先），未启用的按导入顺序排后面
    val orderedSources = remember(sources) {
        val enabled = sources.filter { it.isEnabled }
            .sortedWith(compareBy { it.enabledAt ?: it.updatedAt })
        enabled + sources.filter { !it.isEnabled }
    }
    // 进入页面时把焦点落到返回按钮，避免初始无焦点导致方向键失灵
    val backFocusRequester = remember { FocusRequester() }
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
                                    onFocusFloatingBall()
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
                        text = "播放源管理",
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        // 2.5 浅色主题：浅底深色标题
                        color = LXTextPrimary
                    )
                }
            }

            // HTTP服务器状态
            item {
                ServerStatusCard(
                    isRunning = serverRunning,
                    serverUrl = serverUrl,
                    onToggle = onToggleServer,
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
                        text = "启用的音源按「启用顺序」作为播放优先级（越靠前优先级越高），播放失败会自动切换到下一个音源",
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

        // 删除确认对话框
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
                    text = "HTTP服务器",
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
                    text = "在手机或电脑浏览器中打开上述地址，即可上传和管理播放源",
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
                    text = "播放失败尝试切换音乐平台",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = LXOnCardDark
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "JS 源解析失败时，自动用同一源尝试其他平台版本",
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
 * 两行紧凑布局：第一行 图标+信息+启用开关；第二行删除按钮
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
    Card(
        // 卡片自身不设焦点节点：若卡片 focusable 会拦截方向键，导致遥控器
        // 无法把焦点移入卡片内部的「启用/删除」操作（需按两次确定）。
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
                                    text = "优先级 $p",
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
                            Text(text = "by $auth", fontSize = 12.sp, color = LXOnCardDarkSecondary)
                        }
                    }
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

            // 音源支援平台由 JS 脚本 platforms 自行宣告；此处仅保留删除操作。
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            ) {
                CacheActionButton(
                    text = "删除",
                    hint = "移除该播放源",
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
            contentDescription = "无播放源",
            tint = LXTextSecondary,
            modifier = Modifier.size(64.dp)
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "暂无播放源",
            fontSize = 20.sp,
            fontWeight = FontWeight.Medium,
            // 2.5 浅色主题：浅底深色文字
            color = LXTextPrimary
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "启动HTTP服务器后，在手机/电脑浏览器中打开页面地址即可上传JS播放源文件",
            fontSize = 14.sp,
            color = LXTextSecondary,
            textAlign = TextAlign.Center
        )
    }
}

/**
 * 删除确认对话框
 */
@Composable
fun DeleteConfirmDialog(
    sourceName: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = "确认删除", fontWeight = FontWeight.Bold) },
        text = { Text("确定要删除播放源 \"$sourceName\" 吗？") },
        confirmButton = {
            // 2.8 与主页「退出应用」弹窗按钮样式统一：无背景文本按钮，红字醒目
            TextButton(onClick = onConfirm) {
                Text("删除", color = LXPrimary)
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
