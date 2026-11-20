from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")


def edit(path: str, old: str, new: str, label: str) -> None:
    target = ROOT / path
    source = target.read_text(encoding="utf-8")
    if old not in source:
        if new in source:
            print(f"Already applied: {label}")
            return
        raise SystemExit(f"Expected source block not found: {label} ({path})")
    target.write_text(source.replace(old, new, 1), encoding="utf-8")
    print(f"Applied: {label}")


# Extend the existing OpenCC helper created by patch-lx-tv-features.py.
traditional_util = ROOT / "src/utils/chineseTraditional.ts"
traditional_util.write_text("""import { Children, type ReactNode } from 'react'
import OpenCC from 'opencc-js'

const convertToTraditional = OpenCC.Converter({ from: 'cn', to: 'twp' })

export const toTraditionalString = (value: string): string => convertToTraditional(value)

export const toTraditionalText = (value: ReactNode): ReactNode => Children.map(value, item => {
  return typeof item === 'string' ? convertToTraditional(item) : item
})
""", encoding="utf-8")
print("Applied: shared Simplified-to-Traditional conversion helpers")

# Top navigation sizing is defined by patch-tv-controls.py; do not re-patch Aside.tsx here.

# 2. Convert TextInput placeholders supplied through the shared input component.
edit(
    "src/components/common/Input.tsx",
    "import { setSpText } from '@/utils/pixelRatio'\n",
    "import { setSpText } from '@/utils/pixelRatio'\nimport { toTraditionalString } from '@/utils/chineseTraditional'\n",
    "enable Traditional Chinese conversion for shared input placeholders",
)
edit(
    "src/components/common/Input.tsx",
    "        ref={inputRef} {...props} />",
    "        ref={inputRef} {...props} placeholder={props.placeholder ? toTraditionalString(props.placeholder) : props.placeholder} />",
    "convert shared input placeholder text",
)

# Also cover the one direct TextInput used by the TV quick-add source form.
edit(
    "src/screens/Home/Views/Setting/settings/Basic/SourceQuickAdd.tsx",
    "import { useTheme } from '@/store/theme/hook'\n",
    "import { useTheme } from '@/store/theme/hook'\nimport { toTraditionalString } from '@/utils/chineseTraditional'\n",
    "enable Traditional Chinese conversion in quick-add input",
)
edit(
    "src/screens/Home/Views/Setting/settings/Basic/SourceQuickAdd.tsx",
    'placeholder="输入源链接或订阅地址"',
    'placeholder={toTraditionalString("输入源链接或订阅地址")}',
    "convert quick-add input placeholder",
)

# Apply the new default once to existing installations too, then preserve later user choices.
edit(
    "src/config/setting.ts",
    "  const updatedSetting = updateSetting(setting, true)\n  void saveData(storageDataPrefix.setting, updatedSetting.setting)",
    """  const updatedSetting = updateSetting(setting, true)
  const s2tDefaultMigrated = await getData<boolean>('@lx_tv_s2t_default_v1')
  if (!s2tDefaultMigrated) {
    updatedSetting.setting['player.isS2t'] = true
    await saveData('@lx_tv_s2t_default_v1', true)
  }
  void saveData(storageDataPrefix.setting, updatedSetting.setting)""",
    "enable lyric conversion once for existing installations without overriding later user choices",
)

# 3. Enable Simplified-to-Traditional conversion by default for new settings profiles.
edit(
    "src/config/defaultSetting.ts",
    "  'player.isS2t': false,",
    "  'player.isS2t': true,",
    "enable Chinese lyric conversion by default",
)

# Apply the setting to both horizontal and vertical playback lyric renderers.
for lyric_path in (
    "src/screens/PlayDetail/Horizontal/Lyric.tsx",
    "src/screens/PlayDetail/Vertical/Lyric.tsx",
):
    edit(
        lyric_path,
        "import { AnimatedColorText } from '@/components/common/Text'\n",
        "import { AnimatedColorText } from '@/components/common/Text'\nimport { toTraditionalString } from '@/utils/chineseTraditional'\n",
        "load Traditional Chinese converter in " + lyric_path,
    )
    edit(
        lyric_path,
        "  const textAlign = useSettingValue('playDetail.style.align')\n",
        "  const textAlign = useSettingValue('playDetail.style.align')\n  const isS2t = useSettingValue('player.isS2t')\n",
        "read lyric conversion setting in " + lyric_path,
    )
    edit(
        lyric_path,
        "size={size}>{line.text}</AnimatedColorText>",
        "size={size}>{isS2t ? toTraditionalString(line.text) : line.text}</AnimatedColorText>",
        "convert primary lyric line in " + lyric_path,
    )
    edit(
        lyric_path,
        "size={size * 0.8}>{lrc}</AnimatedColorText>",
        "size={size * 0.8}>{isS2t ? toTraditionalString(lrc) : lrc}</AnimatedColorText>",
        "convert extended lyric line in " + lyric_path,
    )

# 4. Always enter the Songlist tab on a fresh app launch instead of restoring the last tab.
edit(
    "src/core/init/dataInit.ts",
    "import { getViewPrevState } from '@/utils/data'\n",
    "",
    "remove last-tab restore import",
)
edit(
    "src/core/init/dataInit.ts",
    "  setNavActiveId((await getViewPrevState()).id)",
    "  setNavActiveId('nav_home')",
    "default startup navigation to TV Home dashboard",
)

print("LX TV polish patch completed.")
