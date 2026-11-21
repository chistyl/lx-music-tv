package com.lxmusic.tv.presentation.component

import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import androidx.compose.ui.graphics.drawscope.drawOutline
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.lxmusic.tv.presentation.theme.FocusBorder
import com.lxmusic.tv.presentation.theme.LXPrimary
import kotlinx.coroutines.delay

/**
 * 安全的初始焦點請求：等一小段時間（組合與 attach 完成後）再 requestFocus，
 * 若首次失敗則重試一次。此功能屬於焦點導覽，不涉及焦點視覺。
 */
suspend fun requestInitialFocus(
    focusRequester: FocusRequester,
    attempted: () -> Boolean,
    markAttempted: () -> Unit
) {
    if (attempted()) return
    markAttempted()
    try {
        focusRequester.requestFocus()
    } catch (_: IllegalStateException) {
        // focusRequester 尚未初始化，稍後重試
    }
    delay(80)
    try {
        focusRequester.requestFocus()
    } catch (_: IllegalStateException) {
        // 仍失敗則交由使用者按確定鍵由系統兜底落焦點
    }
}

/**
 * 統一圓角焦點視覺：聚焦時使用柔和主題色填充與圓角描邊，
 * 不改變元件尺寸、點擊行為或遙控器焦點導覽。
 */
@Composable
private fun Modifier.lxRoundedFocusVisual(
    shape: Shape,
    fillColor: Color,
    strokeColor: Color,
    strokeWidth: Dp
): Modifier = composed {
    var isFocused by remember { mutableStateOf(false) }
    this
        .onFocusChanged { isFocused = it.isFocused }
        .clip(shape)
        .drawBehind {
            if (isFocused) {
                val outline = shape.createOutline(size, layoutDirection, this)
                drawOutline(outline, fillColor)
                drawOutline(outline, strokeColor, style = Stroke(width = strokeWidth.toPx()))
            }
        }
}

/** 一般卡片／選單焦點：圓角 12dp，聚焦時顯示柔和填色與描邊。 */
@Composable
fun Modifier.lxFocusBorder(
    focusedColor: Color = FocusBorder,
    unfocusedColor: Color = FocusBorder.copy(alpha = 0.18f),
    focusedWidth: Dp = 3.dp,
    unfocusedWidth: Dp = 1.dp,
    focusedScale: Float = 1.0f,
    glow: Boolean = true,
    animated: Boolean = true,
    shape: Shape = RoundedCornerShape(12.dp)
): Modifier = lxRoundedFocusVisual(
    shape = shape,
    fillColor = LXPrimary.copy(alpha = 0.10f),
    strokeColor = focusedColor,
    strokeWidth = focusedWidth
)

/** 圓形按鈕焦點：保持完整圓形填色與圓環。 */
@Composable
fun Modifier.lxCircleButtonFocus(
    fillColor: Color = LXPrimary.copy(alpha = 0.18f),
    strokeColor: Color = FocusBorder,
    strokeWidth: Dp = 3.dp
): Modifier = lxRoundedFocusVisual(
    shape = CircleShape,
    fillColor = fillColor,
    strokeColor = strokeColor,
    strokeWidth = strokeWidth
)

/** 圓形返回按鈕焦點。 */
@Composable
fun Modifier.lxBackButtonFocus(
    focusedColor: Color = FocusBorder,
    glow: Boolean = false,
    animated: Boolean = false
): Modifier = lxRoundedFocusVisual(
    shape = CircleShape,
    fillColor = LXPrimary.copy(alpha = 0.10f),
    strokeColor = focusedColor,
    strokeWidth = 2.dp
)

/** 單選標籤／平台芯片焦點：依呼叫端 shape 顯示圓角選取效果。 */
@Composable
fun Modifier.lxSelectorFocus(
    focusedColor: Color = FocusBorder,
    focusedWidth: Dp = 2.dp,
    focusedScale: Float = 1.0f,
    glow: Boolean = false,
    animated: Boolean = false,
    shape: Shape = RoundedCornerShape(10.dp)
): Modifier = lxRoundedFocusVisual(
    shape = shape,
    fillColor = LXPrimary.copy(alpha = 0.10f),
    strokeColor = focusedColor,
    strokeWidth = focusedWidth
)
