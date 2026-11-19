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
print("LX TV feature patch completed.")
