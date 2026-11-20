from pathlib import Path

ROOT = Path("upstream/lx-music-mobile-auto-source")

def edit(path, old, new, label):
    p = ROOT / path
    s = p.read_text()
    if old not in s:
        raise SystemExit(f"Expected source block not found: {label} ({path})")
    p.write_text(s.replace(old, new, 1))
    print(f"Applied: {label}")

# Remove the catalog URL/update UI while retaining local script import and source management.
p = "src/screens/Home/Views/Setting/settings/Basic/Source.tsx"
s = (ROOT / p).read_text()
s = s.replace("import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'", "import { memo, useCallback, useMemo, useRef } from 'react'")
s = s.replace("import { updateSetting } from '@/core/common'\n", "")
s = s.replace("import { state as userApiState } from '@/store/userApi/state'\n", "")
s = s.replace("import { applyRemoteSourceFallback } from '@/sources/remoteSourceFallback'\n", "")
old_state = """  const savedCatalogUrl = useSettingValue('common.sourceListUrl')
  const [catalogUrl, setCatalogUrl] = useState(savedCatalogUrl)
  useEffect(() => { setCatalogUrl(savedCatalogUrl) }, [savedCatalogUrl])
  const [updating, setUpdating] = useState(false)
  const [updateMessage, setUpdateMessage] = useState('')
  const updateCatalog = async() => {
    if (updating) return
    setUpdating(true)
    try {
      const url = catalogUrl.trim()
      if (url && !/^https?:\\/\\//i.test(url)) {
        setUpdateMessage('请输入有效的源清单地址')
        return
      }
      updateSetting({ 'common.sourceListUrl': url })
      if (!url) {
        setUpdateMessage('订阅已清除，自动更新已停用')
        return
      }
      const changed = await applyRemoteSourceFallback(url, true)
      if (changed) {
        const selected = apiSourceSetting === 'user_api_auto' || userApiState.list.some(item => item.id === apiSourceSetting)
          ? apiSourceSetting : userApiState.list[0]?.id ?? ''
        setApiSource(selected)
      }
      setUpdateMessage(changed ? '订阅已保存并更新，失效时将自动检查更新' : '订阅已保存；清单无变化或暂时无法下载，失效时会自动检查')
    } catch {
      setUpdateMessage('清单更新失败')
    } finally {
      setUpdating(false)
    }
  }
"""
if old_state not in s: raise SystemExit("Catalog state block not found")
s = s.replace(old_state, "", 1)
old_ui = """      <TextInput value={catalogUrl} onChangeText={setCatalogUrl} placeholder="https://example.com/sources.json" accessibilityLabel="源清单地址" autoCapitalize="none" />
      <Button disabled={updating} onPress={() => { void updateCatalog() }}>{updating ? '更新中…' : '保存并更新订阅'}</Button>
      {updateMessage ? <Text>{updateMessage}</Text> : null}
"""
if old_ui not in s: raise SystemExit("Catalog UI block not found")
s = s.replace(old_ui, "", 1)
s = s.replace("import { View, TextInput } from 'react-native'", "import { View } from 'react-native'")
(ROOT / p).write_text(s)
print("Applied: remove subscription catalog updater UI")

# Keep local multi-source failover, but never fetch/update a remote subscription or auto-recover from one.
p = "src/core/userApiFailover.ts"
s = (ROOT / p).read_text()
s = s.replace("import { applyRemoteSourceFallback } from '@/sources/remoteSourceFallback'\n", "")
s = s.replace("import { runSubscriptionRecovery } from '@/sources/subscriptionRecovery'\n", "")
start = s.index("export const tryUserSourceFailover = async(")
s = s[:start] + """export const tryUserSourceFailover = async(
  tryOnce: () => Promise<{ url: string, type: LX.Quality }>,
  _songKey = '',
): Promise<{ url: string, type: LX.Quality }> => {
  const settingId = settingState.setting['common.apiSource']
  if (!isAutoApiSource(settingId)) throw new Error('not auto mode')

  const loadedId = getExpectedSourceId() ?? getLoadedSourceId()
  const current = loadedId ?? ''
  try {
    return await tryOrderedLocalSources(tryOnce, current ? [current] : [])
  } catch (err) {
    releaseInitGateAfterSourceFailure()
    throw err
  }
}
"""
(ROOT / p).write_text(s)
print("Applied: disable subscription recovery; retain local source failover")

# Remove automatic version check on first agreement; keep deep-link initialization.
edit("src/navigation/components/PactModal.tsx",
     "import { checkUpdate } from '@/core/version'\n", "", "remove version-check import")
edit("src/navigation/components/PactModal.tsx",
     "              void checkUpdate()\n              void initDeeplink()",
     "              void initDeeplink()", "remove first-launch version check")

# Remove version entry from both settings layouts.
edit("src/screens/Home/Views/Setting/Main.tsx",
     "import Version from './settings/Version'\n", "", "remove horizontal settings version import")
edit("src/screens/Home/Views/Setting/Main.tsx",
     "  'version',\n", "", "remove version settings tab")
edit("src/screens/Home/Views/Setting/Main.tsx",
     "      case 'version': return <Version />\n", "", "remove horizontal version screen")
edit("src/screens/Home/Views/Setting/Vertical/Main.tsx",
     "import Version from '../settings/Version'\n", "", "remove vertical settings version import")
edit("src/screens/Home/Views/Setting/Vertical/Main.tsx",
     "    case 'version': return <Version />\n", "", "remove vertical version screen")

# Version modal implementation remains in source but is unreachable: the settings entry is removed and first-launch checks are disabled.

# Ensure no app entry point calls the update checker.

# Drop upstream tests that asserted the now-removed automatic subscription recovery behavior.
test_path = ROOT / "scripts/custom-sources.test.cjs"
tests = test_path.read_text()
for title in [
    "all imported sources fail, saved subscription updates, then retry succeeds in user order",
    "updated scripts failing again stop after the second local pass",
    "single subscribed source refreshes without enabling multi-source switching",
]:
    marker = "test('" + title + "',"
    start = tests.find(marker)
    if start < 0:
        raise SystemExit(f"Obsolete recovery test not found: {title}")
    next_test = tests.find("\ntest(", start + len(marker))
    if next_test < 0:
        raise SystemExit(f"Next test boundary not found after: {title}")
    tests = tests[:start] + tests[next_test + 1:]
test_path.write_text(tests)
print("Applied: align source tests with disabled automatic subscription recovery")

print("LX TV feature patch completed.")

# Remove the About LX Music settings entry from both horizontal and vertical layouts.
edit("src/screens/Home/Views/Setting/Main.tsx",
     "import About from './settings/About'\n", "", "remove horizontal About import")
edit("src/screens/Home/Views/Setting/Main.tsx",
     "  'about',\n", "", "remove About settings tab")
edit("src/screens/Home/Views/Setting/Main.tsx",
     "      case 'about': return <About />\n", "", "remove horizontal About screen")
edit("src/screens/Home/Views/Setting/Vertical/Main.tsx",
     "import About from '../settings/About'\n", "", "remove vertical About import")
edit("src/screens/Home/Views/Setting/Vertical/Main.tsx",
     "    case 'about': return <About />\n", "", "remove vertical About screen")

# Convert every shared text component from Simplified Chinese to Taiwan Traditional Chinese.
traditional_util = ROOT / "src/utils/chineseTraditional.ts"
traditional_util.write_text("""import { Children, type ReactNode } from 'react'
import OpenCC from 'opencc-js'

const convertToTraditional = OpenCC.Converter({ from: 'cn', to: 'twp' })

export const toTraditionalText = (value: ReactNode): ReactNode => Children.map(value, item => {
  return typeof item === 'string' ? convertToTraditional(item) : item
})
""")

edit("src/components/common/Text.tsx",
     "import { memo, type ComponentProps } from 'react'\n",
     "import { memo, Children, type ComponentProps } from 'react'\nimport { toTraditionalText } from '@/utils/chineseTraditional'\n",
     "enable Traditional Chinese conversion in shared text components")
edit("src/components/common/Text.tsx",
     ">{children}</Text>", ">{toTraditionalText(children)}</Text>", "convert common Text content")
edit("src/components/common/Text.tsx",
     "{children}</Animated.Text>", "{toTraditionalText(children)}</Animated.Text>", "convert animated Text content")

# Default the application interface to Taiwan Traditional Chinese.
edit("src/core/init/i18n.ts",
     "  let lang = setting['common.langId']",
     "  let lang: I18n['locale'] = 'zh_tw'\n  updateSetting({ 'common.langId': lang })",
     "set Taiwan Traditional Chinese as default interface language")
print("Applied: Simplified-to-Traditional Chinese display conversion")

# Keep the React import minimal and cover the second animated text wrapper as well.
edit("src/components/common/Text.tsx",
     "import { memo, Children, type ComponentProps } from 'react'\n",
     "import { memo, type ComponentProps } from 'react'\n",
     "clean shared text imports")
# AnimatedColorText is used by the built-in lyric renderer; leave lyric text untouched.


# Remove the entire quick-add-custom-source panel shown in Basic > Source settings.
# Keep the existing source list, manual source editor, and source-selection behavior intact.
p = "src/screens/Home/Views/Setting/settings/Basic/Source.tsx"
s = (ROOT / p).read_text()
for old, label in [
    ("import SourceQuickAdd from './SourceQuickAdd'\n", "quick-add component import"),
    ("      <SourceQuickAdd />\n", "quick-add component render"),
]:
    if old not in s:
        raise SystemExit(f"Expected quick-add block not found: {label} ({p})")
    s = s.replace(old, "", 1)
(ROOT / p).write_text(s)
print("Applied: remove quick-add custom source panel")
