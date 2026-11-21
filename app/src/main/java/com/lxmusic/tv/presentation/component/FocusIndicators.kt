package com.lxmusic.tv.presentation.component

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.geometry.RoundRect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Outline
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.lxmusic.tv.presentation.theme.FocusBorder
import com.lxmusic.tv.presentation.theme.LXPrimary
import kotlinx.coroutines.delay
import kotlin.math.max

/**
 * 将 Shape.createOutline 得到的 Outline 转为可描边的 Path。
 */
private fun outlineToPath(outline: Outline): Path {
    return Path().apply {
        when (outline) {
            is Outline.Generic -> addPath(outline.path)
            is Outline.Rounded -> addRoundRect(outline.roundRect)
            is Outline.Rectangle -> addRect(outline.rect)
        }
    }
}

/**
 * 将描边轮廓向内（+）收缩或向外（-）扩张指定像素。
 * 注意：传【正数】= 向内收缩（本文件统一传 stroke/2，使描边外边缘贴合 shape 外边缘）。
 */
private fun Outline.insetBy(px: Float): Outline {
    return when (this) {
        is Outline.Rounded -> {
            val r = roundRect
            Outline.Rounded(
                RoundRect(
                    left = r.left + px,
                    top = r.top + px,
                    right = r.right - px,
                    bottom = r.bottom - px,
                    topLeftCornerRadius = r.topLeftCornerRadius.shrink(px),
                    topRightCornerRadius = r.topRightCornerRadius.shrink(px),
                    bottomRightCornerRadius = r.bottomRightCornerRadius.shrink(px),
                    bottomLeftCornerRadius = r.bottomLeftCornerRadius.shrink(px)
                )
            )
        }
        is Outline.Rectangle -> Outline.Rectangle(
            Rect(
                left = rect.left + px,
                top = rect.top + px,
                right = rect.right - px,
                bottom = rect.bottom - px
            )
        )
        is Outline.Generic -> this // 自定义路径退化处理，保持原样
    }
}

/**
 * 缩小圆角半径（收缩描边时同步缩小，保证圆角弧度贴合）。
 */
private fun CornerRadius.shrink(px: Float): CornerRadius =
    CornerRadius(x = max(0f, this.x - px), y = max(0f, this.y - px))

/**
 * 安全的初始焦点请求：等一小段时间（组合与 attach 完成后）再 requestFocus，
 * 若首次失败则重试一次。
 */
suspend fun requestInitialFocus(
    focusRequester: FocusRequester,
    attempted: () -> Boolean,
    markAttempted: () -> Unit
) {
    if (attempted()) return
    markAttempted()
    // 第一次：组合提交后立即尝试（通常已 attach）
    try {
        focusRequester.requestFocus()
    } catch (_: IllegalStateException) {
        // focusRequester 尚未初始化（attach 未完成），稍后重试
    }
    delay(80)
    // 第二次：若首次可能未生效，再确认请求一次（幂等，焦点已在则无副作用）
    try {
        focusRequester.requestFocus()
    } catch (_: IllegalStateException) {
        // 仍失败则放弃，交由用户按确定键由系统兜底落焦点
    }
}

/**
 * 列表卡片 / 按钮 / 行项 的统一焦点边框。
 * 修复：① 描边轮廓向内收缩 stroke/2（原来向外扩张导致边框画出边界、四角露直角残留）；
 *       ② 增加 clip(shape)，裁掉内容/背景的直角，杜绝直角穿出红框。
 */
@Composable
fun Modifier.lxFocusBorder(
    focusedColor: Color = FocusBorder,
    unfocusedColor: Color = FocusBorder.copy(alpha = 0.18f),
    focusedWidth: Dp = 3.dp,
    unfocusedWidth: Dp = 1.dp,
    focusedScale: Float = 1.0f,
    glow: Boolean = true,
    animated: Boolean = true,
    shape: Shape = RoundedCornerShape(10.dp)
): Modifier {    // 保留原有圓角裁切，只移除焦點框、背景、縮放與動畫。
    return this.clip(shape)
}

@Composable
fun Modifier.lxCircleButtonFocus(
    fillColor: Color = LXPrimary.copy(alpha = 0.18f),
    strokeColor: Color = FocusBorder,
    strokeWidth: Dp = 3.dp
): Modifier {    // 保留圓形裁切，不呈現聚焦填色或焦點環。
    return this.clip(CircleShape)
}

@Composable
fun Modifier.lxBackButtonFocus(
    focusedColor: Color = FocusBorder,
    glow: Boolean = false,
    animated: Boolean = false
): Modifier {    // 返回按鈕不顯示焦點視覺狀態。
    return this
}

@Composable
fun Modifier.lxSelectorFocus(
    focusedColor: Color = FocusBorder,
    focusedWidth: Dp = 3.dp,
    focusedScale: Float = 1.0f,
    glow: Boolean = true,
    animated: Boolean = true,
    shape: Shape = RoundedCornerShape(8.dp)
): Modifier {    // 保留選擇器原有圓角裁切，不顯示焦點外框或動畫。
    return this.clip(shape)
}
