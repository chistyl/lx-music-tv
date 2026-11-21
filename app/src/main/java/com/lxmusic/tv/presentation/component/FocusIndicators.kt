package com.lxmusic.tv.presentation.component

import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
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
 * 焦點邊框視覺已依需求停用；保留 shape clip，避免改變元件原有外觀輪廓。
 * 不監聽焦點、不繪製邊框、不改變尺寸或焦點導覽。
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
): Modifier = this.clip(shape)

/**
 * 圓形按鈕焦點填色與圓環視覺已停用；保留呼叫端既有 Modifier 鏈。
 */
@Composable
fun Modifier.lxCircleButtonFocus(
    fillColor: Color = LXPrimary.copy(alpha = 0.18f),
    strokeColor: Color = FocusBorder,
    strokeWidth: Dp = 3.dp
): Modifier = this

/**
 * 圓形返回按鈕焦點視覺已停用。
 */
@Composable
fun Modifier.lxBackButtonFocus(
    focusedColor: Color = FocusBorder,
    glow: Boolean = false,
    animated: Boolean = false
): Modifier = this.clip(CircleShape)

/**
 * 單選標籤／平台芯片焦點邊框視覺已停用；保留原有圓角裁切。
 */
@Composable
fun Modifier.lxSelectorFocus(
    focusedColor: Color = FocusBorder,
    focusedWidth: Dp = 3.dp,
    focusedScale: Float = 1.0f,
    glow: Boolean = true,
    animated: Boolean = true,
    shape: Shape = RoundedCornerShape(8.dp)
): Modifier = this.clip(shape)
