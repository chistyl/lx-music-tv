package com.lxmusic.tv.presentation.theme

import android.content.Context
import android.util.Log
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

/**
 * LX Music TV 主題系統：保留淺色／深色切換與三組強調色，TV 深色介面採中性黑色層次。
 * - 深色主背景、側欄、播放器與內容卡片使用一致的黑／炭灰表面階層
 * - 文字使用高對比淺色，次要資訊使用柔和灰階
 * - 赤焰紅／暮色紫／靛青仍作為可切換的品牌強調色，不覆寫使用者選擇
 * - 淺色主題維持原有設定，不因 TV 深色介面調整而改變
 */

// =================== 品牌色（主 / 次强调色实际取自所选主题色，定义见下方 LXPrimary / LXSecondary getter） ===================

// =================== 主题模式 / 主题色（界面设置持久化，实际生效） ===================
/** 主题模式：浅色 / 深色（深色模式参考 EchoMusic 暗色表面系统） */
enum class LXThemeMode { LIGHT, DARK }

/**
 * 主题色配置（实际生效）。赤焰红沿用 2.5 既有品牌红配置；暮色紫 / 靛青参考 EchoMusic 主题色预设。
 * 每个配置提供主强调色 primary、次要色 secondary，以及浅色 / 深色模式各自的
 * primaryContainer / onPrimaryContainer（Material3 容器色，由强调色推导）。
 */
data class LXThemeColorConfig(
    val primary: Color,
    val secondary: Color,
    val primaryContainerLight: Color,
    val onPrimaryContainerLight: Color,
    val primaryContainerDark: Color,
    val onPrimaryContainerDark: Color,
) {
    companion object {
        /** 赤焰红：2.5 既有品牌红（#E94560）+ 浅蓝次要色，作为默认主题色 */
        val CRIMSON = LXThemeColorConfig(
            primary = Color(0xFFE94560),
            secondary = Color(0xFF5AC8FA),
            primaryContainerLight = Color(0xFFFFD9DD),
            onPrimaryContainerLight = Color(0xFF3B0009),
            primaryContainerDark = Color(0xFF8B1A30),
            onPrimaryContainerDark = Color(0xFFFFD9DD),
        )
        /** 暮色紫：参考 EchoMusic 紫色主题（#8B5CF6，Material3 紫罗兰），次要色取浅紫 */
        val PURPLE = LXThemeColorConfig(
            primary = Color(0xFF8B5CF6),
            secondary = Color(0xFFB39DDB),
            primaryContainerLight = Color(0xFFE9DDFF),
            onPrimaryContainerLight = Color(0xFF2D006B),
            primaryContainerDark = Color(0xFF4A1D82),
            onPrimaryContainerDark = Color(0xFFE9DDFF),
        )
        /** 靛青：参考 EchoMusic 蓝色主题（#3B5BDB，Material3 靛蓝），次要色取青蓝 */
        val INDIGO = LXThemeColorConfig(
            primary = Color(0xFF3B5BDB),
            secondary = Color(0xFF7FA8FF),
            primaryContainerLight = Color(0xFFDBE0FF),
            onPrimaryContainerLight = Color(0xFF00164F),
            primaryContainerDark = Color(0xFF27368A),
            onPrimaryContainerDark = Color(0xFFDBE0FF),
        )
    }
}

/** 主题色：赤焰红 / 暮色紫 / 靛青（实际生效，切换后全站强调色随之改变） */
enum class LXThemeColor { CRIMSON, PURPLE, INDIGO }

/** 主题色对应配置（主 / 次强调色等） */
val LXThemeColor.config: LXThemeColorConfig
    get() = when (this) {
        LXThemeColor.CRIMSON -> LXThemeColorConfig.CRIMSON
        LXThemeColor.PURPLE -> LXThemeColorConfig.PURPLE
        LXThemeColor.INDIGO -> LXThemeColorConfig.INDIGO
    }

/** 主题色展示色板（界面设置页预览用，即该主题的主强调色） */
val LXThemeColor.swatch: Color get() = this.config.primary

/** 主题色中文名 */
val LXThemeColor.label: String
    get() = when (this) {
        LXThemeColor.CRIMSON -> "赤焰红"
        LXThemeColor.PURPLE -> "暮色紫"
        LXThemeColor.INDIGO -> "靛青"
    }

// =================== 主题令牌集合（浅色 / 深色各一套；表面/文字与主题色无关，主强调色来自所选主题色） ===================
data class LXThemeColors(
    // 主强调色（随主题色切换）
    val primary: Color,
    val secondary: Color,
    val primaryContainer: Color,
    val onPrimaryContainer: Color,
    // 表面系统
    val surfaceSidebar: Color,
    val surfaceMain: Color,
    val surfaceCard: Color,
    val surfaceDialog: Color,
    val surfaceVariant: Color,
    val background: Color,
    val surface: Color,
    val onPrimary: Color,
    val onBackground: Color,
    val onSurface: Color,
    val onSurfaceVariant: Color,
    val textPrimary: Color,
    val textSecondary: Color,
    val textDisabled: Color,
    val border: Color,
    val divider: Color,
    val cardDark: Color,
    val onCardDark: Color,
    val onCardDarkSecondary: Color,
    val accentGradient: Brush,
    val sidebarGradient: Brush,
    val shadowCard: Color,
    val focusBorder: Color,
    val focusFill: Color,
) {
    companion object {
        /** 浅色令牌（2.5 默认；仿 EchoMusic 浅色表面系统）；主强调色取自所选主题色的 primary */
        fun light(cfg: LXThemeColorConfig) = LXThemeColors(
            primary = cfg.primary,
            secondary = cfg.secondary,
            primaryContainer = cfg.primaryContainerLight,
            onPrimaryContainer = cfg.onPrimaryContainerLight,
            surfaceSidebar = Color(0xFFFFFFFF),
            surfaceMain = Color(0xFFF5F5F7),
            surfaceCard = Color(0xFFFFFFFF),
            surfaceDialog = Color(0xFFF0F0F2),
            surfaceVariant = Color(0xFFF0F0F2),
            background = Color(0xFFF5F5F7),
            surface = Color(0xFFFFFFFF),
            onPrimary = Color.White,
            onBackground = Color(0xFF1D1D1F),
            onSurface = Color(0xFF1D1D1F),
            onSurfaceVariant = Color(0xFF4B5563),
            textPrimary = Color(0xFF1D1D1F),
            textSecondary = Color(0xFF4B5563),
            textDisabled = Color(0xFF999999),
            border = Color(0xFFE5E5EA),
            divider = Color(0xFFEAEAEA),
            cardDark = Color(0x201A1A1A),          // 黑色半透明（用户手动调整），浅色模式下作深色卡片
            onCardDark = Color(0xFF1D1D1F),
            onCardDarkSecondary = Color(0xFF4B5563),
            accentGradient = Brush.verticalGradient(
                0.0f to cfg.primary.copy(alpha = 0.2f),
                0.6f to cfg.primary.copy(alpha = 0.07f),
                1.0f to Color.Transparent
            ),
            sidebarGradient = Brush.verticalGradient(
                0.0f to cfg.primary.copy(alpha = 0.18f),
                0.55f to cfg.primary.copy(alpha = 0.06f),
                1.0f to Color.Transparent
            ),
            shadowCard = Color(0x14000000),
            focusBorder = Color(0x801A1A1A),
            focusFill = Color(0xFF1D1D1F).copy(alpha = 0.05f),
        )

        /** 深色令牌（参考 EchoMusic 暗色表面系统：深底 + 浅字 + 强调色）；主强调色取自所选主题色 */
        fun dark(cfg: LXThemeColorConfig) = LXThemeColors(
            primary = cfg.primary,
            secondary = cfg.secondary,
            primaryContainer = cfg.primaryContainerDark,
            onPrimaryContainer = cfg.onPrimaryContainerDark,
            surfaceSidebar = Color(0xFF0D1013),
            surfaceMain = Color(0xFF090B0D),
            surfaceCard = Color(0xFF171D21),
            surfaceDialog = Color(0xFF1A2024),
            surfaceVariant = Color(0xFF242A2E),
            background = Color(0xFF090B0D),
            surface = Color(0xFF111519),
            onPrimary = Color.White,
            onBackground = Color(0xFFF3F5F6),
            onSurface = Color(0xFFF3F5F6),
            onSurfaceVariant = Color(0xFFAAB3B8),
            textPrimary = Color(0xFFF3F5F6),
            textSecondary = Color(0xFFAAB3B8),
            textDisabled = Color(0xFF69747B),
            border = Color(0xFF2B343A),
            divider = Color(0xFF20282D),
            cardDark = Color(0xFF171D21),
            onCardDark = Color(0xFFF3F5F6),
            onCardDarkSecondary = Color(0xFFAAB3B8),
            accentGradient = Brush.verticalGradient(
                0.0f to cfg.primary.copy(alpha = 0.28f),
                0.6f to cfg.primary.copy(alpha = 0.1f),
                1.0f to Color.Transparent
            ),
            sidebarGradient = Brush.verticalGradient(
                0.0f to cfg.primary.copy(alpha = 0.24f),
                0.55f to cfg.primary.copy(alpha = 0.09f),
                1.0f to Color.Transparent
            ),
            shadowCard = Color(0x40000000),
            // TV 焦點與選取狀態沿用使用者選擇的主題強調色，避免固定白框或固定綠色。
            focusBorder = cfg.primary,
            focusFill = cfg.primary.copy(alpha = 0.16f),
        )
    }
}

/**
 * 按（主题模式, 主题色）解析最终主题令牌（单一解析入口）。
 * initThemeState / setThemeMode / setThemeColor / LXMusicTheme 全部经此构建 currentLXTheme，
 * 主题色切换时会重建梯度与 Material 主色，使全站强调色即时变化。
 */
fun resolvedLXTheme(mode: LXThemeMode, color: LXThemeColor): LXThemeColors {
    val cfg = color.config
    return if (mode == LXThemeMode.DARK) LXThemeColors.dark(cfg) else LXThemeColors.light(cfg)
}

/**
 * 当前主题令牌（由 LXMusicTheme 在重组时写入；默认浅色）。
 *
 * 用 [mutableStateOf] 支撑的 `var` 而非普通 `var`：普通 var 的读取不会向 Compose 快照系统
 * 注册观察，导致导航切换页面（LXMusicTheme 本身未重组）时，新组合的页面读到的仍是旧值、
 * 主题在返回/重进后"复位"成浅色。改为 State 支撑后，所有读取 `LXSurfaceMain` 等令牌的
 * 组合在主题切换时都会失效重组，保证浅色/深色在全站（含跨页面导航）一致生效。
 *
 * 仍保留全局 var 形式，以便非组合上下文（drawWithContent 等绘制回调）也能读到当前主题色。
 */
var currentLXTheme: LXThemeColors by mutableStateOf(resolvedLXTheme(LXThemeMode.DARK, LXThemeColor.CRIMSON))

// =================== 主题模式/主题色全局状态（单一数据源） ===================
// 主题模式不能只放在 ViewModel：NavHost 目的地内的 viewModel() 解析到的是「返回栈条目作用域」
// 的独立实例（LocalViewModelStoreOwner = NavBackStackEntry），界面设置页 setThemeMode 改的是
// 自己那一份，主 Activity（Activity 作用域）的实例永远收不到 → 深色模式无法真正生效（实测：
// 设置页选深色，返回/重进后仍是浅色）。故把主题状态提升为模块级 State，MainActivity 与界面
// 设置页直接读写同一份，杜绝作用域分裂。
const val LX_THEME_PREFS = "lx_settings"   // 与 MainViewModel 共用持久化文件名

/** 全局当前主题模式（浅色/深色；MainActivity 读取、界面设置页写入）；默认深色 */
var currentThemeMode: LXThemeMode by mutableStateOf(LXThemeMode.DARK)

/** 全局当前主题色（赤焰红/暮色紫/靛青；实际生效，切换后全站强调色随之改变） */
var currentThemeColor: LXThemeColor by mutableStateOf(LXThemeColor.CRIMSON)

/** 启动时从 SharedPreferences 恢复主题模式/主题色（MainActivity.onCreate 在 setContent 前调用一次） */
fun initThemeState(context: Context) {
    val prefs = context.getSharedPreferences(LX_THEME_PREFS, Context.MODE_PRIVATE)
    currentThemeMode = runCatching {
        LXThemeMode.valueOf(prefs.getString("theme_mode", LXThemeMode.DARK.name) ?: LXThemeMode.DARK.name)
    }.getOrDefault(LXThemeMode.DARK)
    currentThemeColor = runCatching {
        LXThemeColor.valueOf(prefs.getString("theme_color", LXThemeColor.CRIMSON.name) ?: LXThemeColor.CRIMSON.name)
    }.getOrDefault(LXThemeColor.CRIMSON)
    // 同步令牌，避免启动首帧闪错配色（LXMusicTheme 的 SideEffect 首帧后才写入）
    currentLXTheme = resolvedLXTheme(currentThemeMode, currentThemeColor)
    Log.d("LX-Theme", "initThemeState: mode=${currentThemeMode} color=${currentThemeColor}")
}

/** 设置主题模式并持久化（界面设置页调用） */
fun setThemeMode(mode: LXThemeMode, context: Context) {
    currentThemeMode = mode
    // 同步直接写入主题令牌：不依赖 LXMusicTheme 的重组链，点击瞬间全局生效（含主题色）
    currentLXTheme = resolvedLXTheme(mode, currentThemeColor)
    Log.d("LX-Theme", "setThemeMode -> $mode (currentLXTheme=${if (mode == LXThemeMode.DARK) "Dark" else "Light"})")
    context.getSharedPreferences(LX_THEME_PREFS, Context.MODE_PRIVATE)
        .edit()
        .putString("theme_mode", mode.name)
        .apply()
}

/** 设置主题色并持久化（界面设置页调用；实际生效：切换后全站强调色随之改变） */
fun setThemeColor(color: LXThemeColor, context: Context) {
    currentThemeColor = color
    // 同步直接写入主题令牌：重建梯度与 Material 主色，点击瞬间全站强调色更新
    currentLXTheme = resolvedLXTheme(currentThemeMode, color)
    Log.d("LX-Theme", "setThemeColor -> $color (primary=${color.config.primary})")
    context.getSharedPreferences(LX_THEME_PREFS, Context.MODE_PRIVATE)
        .edit()
        .putString("theme_color", color.name)
        .apply()
}

// =================== 主/次强调色（随主题色切换；全站红色强调统一走这里，切换主题色即时生效） ===================
val LXPrimary: Color get() = currentLXTheme.primary
val LXSecondary: Color get() = currentLXTheme.secondary

// =================== 表面系统（通过 currentLXTheme 切换，浅色/深色自动生效） ===================
val LXSurfaceSidebar: Color get() = currentLXTheme.surfaceSidebar
val LXSurfaceMain: Color get() = currentLXTheme.surfaceMain
val LXSurfaceCard: Color get() = currentLXTheme.surfaceCard
val LXSurfaceDialog: Color get() = currentLXTheme.surfaceDialog
val LXSurfaceVariant: Color get() = currentLXTheme.surfaceVariant

// =================== 背景与表面（Material 主题用） ===================
val LXBackground: Color get() = currentLXTheme.background
val LXSurface: Color get() = currentLXTheme.surface

// =================== 文字 ===================
val LXOnPrimary: Color get() = currentLXTheme.onPrimary
val LXOnSecondary: Color get() = currentLXTheme.textSecondary
val LXOnBackground: Color get() = currentLXTheme.onBackground
val LXOnSurface: Color get() = currentLXTheme.onSurface

val LXTextPrimary: Color get() = currentLXTheme.textPrimary
val LXTextSecondary: Color get() = currentLXTheme.textSecondary
val LXTextDisabled: Color get() = currentLXTheme.textDisabled

// =================== 边框 ===================
val LXBorder: Color get() = currentLXTheme.border
val LXDivider: Color get() = currentLXTheme.divider

// =================== 主区顶部氛围渐变（仿 EchoMusic .layout-accent-gradient） ===================
// 实色主区 #F5F5F7 之上叠加，覆盖顶部约 50%：品牌红由 0.2 渐隐到透明
val LXAccentGradientBrush: Brush get() = currentLXTheme.accentGradient

// =================== 侧栏顶部氛围渐变（点1：侧栏也要渐变，与主区略有差别） ===================
// 侧栏基底为纯白 #FFFFFF（比主区灰 #F5F5F7 更亮），这里用略轻柔的品牌红氛围渐变，
// 让左侧同样有渐变、又因基底白而比右侧（灰底）稍亮，形成 EchoMusic 式的轻微色差。
val LXSidebarGradientBrush: Brush get() = currentLXTheme.sidebarGradient

// =================== 深色卡片（仿播放页播放列表暗色面板，点6） ===================
// 注意：用户将 LXCardDark 调为 0x201A1A1A（极淡黑），卡片几乎透明、底色以浅色主区为主，
// 故卡片上的文字/图标统一改为深色（黑/深灰），否则在浅底上不可见。
val LXCardDark: Color get() = currentLXTheme.cardDark
val LXOnCardDark: Color get() = currentLXTheme.onCardDark
val LXOnCardDarkSecondary: Color get() = currentLXTheme.onCardDarkSecondary

// =================== 功能色 ===================
val LXSuccess = Color(0xFF10B981)
val LXWarning = Color(0xFFF59E0B)
val LXError = Color(0xFFEF4444)
val LXInfo = Color(0xFF2196F3)

// =================== 统一焦点边框（浅底上呈中灰，含蓄） ===================
val FocusBorder: Color get() = currentLXTheme.focusBorder
val LXFocusFill: Color get() = currentLXTheme.focusFill

// =================== 阴影（EchoMusic 风格：极轻） ===================
val LXShadowCard: Color get() = currentLXTheme.shadowCard

/**
 * 浅色 Material 配色（主强调色来自所选主题色；每次重组按当前主题色重建）
 */
private fun lightColorSchemeFor(
    primary: Color,
    secondary: Color,
    primaryContainer: Color,
    onPrimaryContainer: Color,
) = lightColorScheme(
    primary = primary,
    onPrimary = LXOnPrimary,
    primaryContainer = primaryContainer,
    onPrimaryContainer = onPrimaryContainer,
    secondary = secondary,
    onSecondary = LXOnSecondary,
    secondaryContainer = Color(0xFFD6F0FF),
    onSecondaryContainer = Color(0xFF003355),
    tertiary = LXSuccess,
    onTertiary = Color.White,
    background = LXBackground,
    onBackground = LXOnBackground,
    surface = LXSurface,
    onSurface = LXOnSurface,
    surfaceVariant = LXSurfaceVariant,
    onSurfaceVariant = LXTextSecondary,
    outline = LXBorder,
    outlineVariant = LXDivider,
    error = LXError,
    onError = Color.White,
    errorContainer = Color(0xFFFFDAD6),
    onErrorContainer = Color(0xFF410002)
)

/**
 * 暗色 Material 配色（主强调色来自所选主题色；每次重组按当前主题色重建）
 */
private fun darkColorSchemeFor(
    primary: Color,
    secondary: Color,
    primaryContainer: Color,
    onPrimaryContainer: Color,
) = darkColorScheme(
    primary = primary,
    onPrimary = LXOnPrimary,
    primaryContainer = primaryContainer,
    onPrimaryContainer = onPrimaryContainer,
    secondary = secondary,
    onSecondary = Color.Black,
    secondaryContainer = Color(0xFF00476F),
    onSecondaryContainer = Color(0xFFD6F0FF),
    tertiary = LXSuccess,
    onTertiary = Color.Black,
    background = Color(0xFF090B0D),
    onBackground = Color(0xFFF3F5F6),
    surface = Color(0xFF111519),
    onSurface = Color(0xFFF3F5F6),
    surfaceVariant = Color(0xFF242A2E),
    onSurfaceVariant = Color(0xFFAAB3B8),
    outline = Color(0xFF2B343A),
    outlineVariant = Color(0xFF343D43),
    error = LXError,
    onError = Color.White,
    errorContainer = Color(0xFF3D1515),
    onErrorContainer = Color(0xFFFFDAD6)
)

/**
 * LX Music TV 主题组件
 * 2.5 起默认深色主题（赤焰红）；界面设置页切换浅色/深色与主色后即时生效
 *
 * 本组件直接订阅模块级 currentThemeMode：界面设置页写入后必然触发本组件重组，
 * 保证 Material colorScheme 与自定义令牌同步切换（不依赖 MainActivity 传参链）。
 */
@Composable
fun LXMusicTheme(
    darkTheme: Boolean = false,
    content: @Composable () -> Unit
) {
    // 直接读模块级主题模式（订阅）：currentThemeMode 变更即重组
    val isDark = darkTheme || currentThemeMode == LXThemeMode.DARK
    // 主强调色随当前主题色（currentThemeColor）解析；二者均为模块级 State，切换即重组
    val theme = resolvedLXTheme(currentThemeMode, currentThemeColor)
    val colorScheme = if (isDark) {
        darkColorSchemeFor(theme.primary, theme.secondary, theme.primaryContainer, theme.onPrimaryContainer)
    } else {
        lightColorSchemeFor(theme.primary, theme.secondary, theme.primaryContainer, theme.onPrimaryContainer)
    }

    // 组合提交后再写入全局主题令牌（组合期内直接写快照 State 会被读者读到旧值，见 code 71/72 教训）
    SideEffect {
        currentLXTheme = theme
        Log.d("LX-Theme", "LXMusicTheme SideEffect: isDark=$isDark color=${currentThemeColor}")
    }
    MaterialTheme(
        colorScheme = colorScheme,
        typography = LXTypography,
        shapes = LXShapes,
        content = content
    )
}

/**
 * 自定义颜色扩展（随主题色/模式切换；全部走 getter，读取 currentLXTheme 当前值）
 */
object LXColors {
    // 主要颜色（随主题色切换）
    val Primary get() = LXPrimary
    val Secondary get() = LXSecondary
    val Background get() = LXBackground           // 浅灰 #F5F5F7
    val Surface get() = LXSurface                  // 白 #FFFFFF

    // 功能颜色
    val Success get() = LXSuccess
    val Warning get() = LXWarning
    val Error get() = LXError
    val Info get() = LXInfo

    // 文字颜色
    val TextPrimary get() = LXTextPrimary          // 深 #1D1D1F
    val TextSecondary get() = LXTextSecondary
    val TextDisabled get() = LXTextDisabled

    // 边框和分隔线
    val Border get() = LXBorder
    val Divider get() = LXDivider

    // 渐变色（随主题色切换）
    val GradientStart get() = LXPrimary
    val GradientEnd get() = LXSecondary

    // 卡片颜色
    val CardBackground get() = LXSurfaceCard       // 白
    val CardBorder get() = LXBorder

    // 深色模式卡片：中性炭灰表面，文字維持高對比
    val CardDark get() = LXCardDark
    val OnCardDark get() = LXOnCardDark
    val OnCardDarkSecondary get() = LXOnCardDarkSecondary
    val AccentGradientBrush get() = LXAccentGradientBrush    // 主区顶部氛围渐变
    val SidebarGradientBrush get() = LXSidebarGradientBrush  // 侧栏顶部氛围渐变（略轻柔）

    // 按钮颜色（随主题色切换）
    val ButtonPrimary get() = LXPrimary
    val ButtonSecondary get() = LXSecondary
    val ButtonDisabled = Color(0xFFE5E5EA)

    // 输入框颜色（浅色）
    val InputBackground get() = LXSurfaceCard     // 白
    val InputBorder get() = LXBorder
    val InputFocusBorder get() = LXPrimary

    // 播放器颜色（2.5 不动播放页，保持原暗色）
    val PlayerBackground = Color(0xFF101519)
    val PlayerProgress get() = LXPrimary
    val PlayerProgressBackground = Color(0xFF242A2E)
}

/**
 * 扩展颜色函数
 */
fun Color.copyAlpha(alpha: Float): Color {
    return this.copy(alpha = alpha)
}

/**
 * 暗色变体
 */
fun Color.darken(factor: Float = 0.2f): Color {
    val red = (this.red * (1 - factor)).coerceIn(0f, 1f)
    val green = (this.green * (1 - factor)).coerceIn(0f, 1f)
    val blue = (this.blue * (1 - factor)).coerceIn(0f, 1f)
    return Color(red, green, blue, this.alpha)
}

/**
 * 亮色变体
 */
fun Color.lighten(factor: Float = 0.2f): Color {
    val red = (this.red + (1 - this.red) * factor).coerceIn(0f, 1f)
    val green = (this.green + (1 - this.green) * factor).coerceIn(0f, 1f)
    val blue = (this.blue + (1 - this.blue) * factor).coerceIn(0f, 1f)
    return Color(red, green, blue, this.alpha)
}