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


# Set clean-install defaults to Taiwan Traditional Chinese and original platform names.
edit(
    "src/config/defaultSetting.ts",
    "  'common.langId': null,",
    "  'common.langId': 'zh_tw',",
    "default interface language to Traditional Chinese",
)
edit(
    "src/config/defaultSetting.ts",
    "  'common.sourceNameType': 'alias',",
    "  'common.sourceNameType': 'real',",
    "default music platform labels to their original names",
)

# Use Traditional Chinese only when there is no valid saved language.
# A valid language selected by the user remains unchanged on later launches.
(ROOT / "src/core/init/i18n.ts").write_text("""import { createI18n } from '@/lang/i18n'
import { setLanguage, updateSetting } from '@/core/common'


export default async(setting: LX.AppSetting) => {
  let lang = setting['common.langId']

  global.i18n = createI18n()

  if (!lang || !global.i18n.availableLocales.includes(lang)) {
    lang = 'zh_tw'
    updateSetting({ 'common.langId': lang })
  }
  setLanguage(lang)
}
""", encoding="utf-8")
print("Applied: Traditional Chinese fallback without overriding a saved language")

# Existing installations receive the new platform-name default once.
# After migration, subsequent user selections are preserved.
edit(
    "src/config/setting.ts",
    """  const updatedSetting = updateSetting(setting, true)
  const s2tDefaultMigrated = await getData<boolean>('@lx_tv_s2t_default_v1')
  if (!s2tDefaultMigrated) {
    updatedSetting.setting['player.isS2t'] = true
    await saveData('@lx_tv_s2t_default_v1', true)
  }
  void saveData(storageDataPrefix.setting, updatedSetting.setting)""",
    """  const updatedSetting = updateSetting(setting, true)
  const s2tDefaultMigrated = await getData<boolean>('@lx_tv_s2t_default_v1')
  if (!s2tDefaultMigrated) {
    updatedSetting.setting['player.isS2t'] = true
    await saveData('@lx_tv_s2t_default_v1', true)
  }
  const sourceNameDefaultMigrated = await getData<boolean>('@lx_tv_source_name_default_v1')
  if (!sourceNameDefaultMigrated) {
    if (updatedSetting.setting['common.sourceNameType'] === 'alias') {
      updatedSetting.setting['common.sourceNameType'] = 'real'
    }
    await saveData('@lx_tv_source_name_default_v1', true)
  }
  void saveData(storageDataPrefix.setting, updatedSetting.setting)""",
    "migrate existing default platform labels to original names once",
)

print("LX TV default language and platform-name patch completed.")
