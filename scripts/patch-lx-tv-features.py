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


# Remove the "Other" category from both settings navigation layouts.
# These replacements are intentionally idempotent because upstream variants may already omit an entry.
p = "src/screens/Home/Views/Setting/Main.tsx"
s = (ROOT / p).read_text()
s = s.replace("import Other from './settings/Other'\n", "")
s = s.replace("  'other',\n", "")
s = s.replace("      case 'other': return <Other />\n", "")
(ROOT / p).write_text(s)

p = "src/screens/Home/Views/Setting/Vertical/Main.tsx"
s = (ROOT / p).read_text()
s = s.replace("import Other from '../settings/Other'\n", "")
s = s.replace("    case 'other': return <Other />\n", "")
(ROOT / p).write_text(s)
print("Applied: remove Other settings category")



# Bundle the supplied Wildflower script and add it once to the local custom-source list.
# The persistent marker means deleting it in the app will not cause it to be re-added.
import json
wildflower_script = "/**\n * @name 野花🌷\n * @version 1\n */\n(function(p,O){const d={p:0xfe,O:'\\x30\\x78\\x31\\x30\\x65',w:'\\x30\\x78\\x31\\x31\\x63',r:0x109,g:0xc3,h:0xb6,E:0x117,u:0x112,C:'\\x30\\x78\\x31\\x30\\x61',U:0xdf,T:0xe5},v=Z,w=p();while(!![]){try{const r=-parseInt(v(d.p))/(-0x15*0x121+-0x168b+0x3*0xf6b)*(-parseInt(v(d.O))/(-0x1*0xec6+0x3*-0x41f+0x1b25*0x1))+parseInt(v(d.w))/(0x1e01*0x1+0x844*0x3+-0x1*0x36ca)+parseInt(v(d.r))/(-0x25+0x7c6+-0x79d)*(parseInt(v(d.g))/(-0x422*-0x3+0x9*0x2c+0x2c9*-0x5))+-parseInt(v(d.h))/(0x10fe+0xd65*0x1+-0x1e5d*0x1)+-parseInt(v(d.E))/(-0x19*0x82+-0x4f*-0x7d+-0x3*0x89e)+parseInt(v(d.u))/(-0x1cc9+0x1746+0x2b*0x21)*(parseInt(v(d.C))/(0x1460+-0x1787+-0x66*-0x8))+-parseInt(v(d.U))/(-0x67*-0x25+-0x25e4+0x170b*0x1)*(parseInt(v(d.T))/(-0x3*0xcaa+0x1a1d+0x1b4*0x7));if(r===O)break;else w['push'](w['shift']());}catch(g){w['push'](w['shift']());}}}(R,-0x658f*-0x11+0x78e4a+-0xf38*0x71),((()=>{const Ro={p:'\\x30\\x78\\x66\\x39',O:'\\x30\\x78\\x65\\x30',w:'\\x30\\x78\\x31\\x30\\x63',r:'\\x30\\x78\\x64\\x35',g:0xe6,h:'\\x30\\x78\\x66\\x37',E:'\\x30\\x78\\x63\\x35',u:'\\x30\\x78\\x31\\x30\\x30',C:'\\x30\\x78\\x66\\x33',U:0xe8,T:'\\x30\\x78\\x64\\x34',z:0xe2,P:0x110,e:'\\x30\\x78\\x31\\x30\\x66',L:0xd0,o:0x107,l:'\\x30\\x78\\x65\\x32',f:0x110,V:0xee,m:0xf1,j:'\\x30\\x78\\x65\\x61',c:'\\x30\\x78\\x31\\x30\\x64',N:'\\x30\\x78\\x66\\x64',S:0x105,q:0xec,y:0xde,G:'\\x30\\x78\\x31\\x30\\x32',F:'\\x30\\x78\\x62\\x61',K:0x118,b:'\\x30\\x78\\x64\\x31',t:'\\x30\\x78\\x65\\x34',D:0xff,Rl:0xd8,Rf:0x108,RV:0xdc,Rm:'\\x30\\x78\\x66\\x32',Rj:'\\x30\\x78\\x63\\x37',Rc:'\\x30\\x78\\x63\\x31'},RL={p:0xd7,O:'\\x30\\x78\\x31\\x30\\x34',w:'\\x30\\x78\\x66\\x30',r:'\\x30\\x78\\x66\\x35',g:0xef,h:0xf2,E:'\\x30\\x78\\x62\\x64',u:'\\x30\\x78\\x65\\x66',C:0xcf,U:'\\x30\\x78\\x63\\x66',T:'\\x30\\x78\\x66\\x61',z:'\\x30\\x78\\x31\\x31\\x64',P:0xdb,e:'\\x30\\x78\\x66\\x34',L:0x11a,o:'\\x30\\x78\\x62\\x66',l:0xe3,f:'\\x30\\x78\\x31\\x31\\x34',V:'\\x30\\x78\\x66\\x38',m:'\\x30\\x78\\x62\\x61',j:'\\x30\\x78\\x64\\x39',c:'\\x30\\x78\\x31\\x31\\x33'},RP={p:0xdd,O:'\\x30\\x78\\x62\\x62',w:0xbe},Ru={p:0xb9,O:'\\x30\\x78\\x65\\x31',w:0xbe,r:0xed,g:0xdb,h:'\\x30\\x78\\x31\\x30\\x31',E:0xcd},Rh={p:0xca},Rr={p:0xd9},Rw={p:'\\x30\\x78\\x63\\x63',O:0x116,w:0xb8,r:0xc9,g:0xc4},A=Z,p={'\\x64\\x63\\x41\\x4c\\x4e':function(c,N){return c(N);},'\\x42\\x4d\\x51\\x46\\x62':A(Ro.p),'\\x6e\\x42\\x66\\x48\\x77':function(c,N,S){return c(N,S);},'\\x6e\\x59\\x61\\x68\\x77':A(Ro.O),'\\x6d\\x44\\x42\\x63\\x4e':function(c,N,S,q){return c(N,S,q);},'\\x66\\x44\\x6d\\x6b\\x4b':function(c,N){return c+N;},'\\x62\\x46\\x74\\x70\\x48':A(Ro.w)+A(Ro.r)+A(Ro.g),'\\x51\\x5a\\x6b\\x43\\x73':A(Ro.h),'\\x43\\x70\\x6d\\x41\\x48':function(c,N){return c!=N;},'\\x6f\\x64\\x79\\x51\\x6a':A(Ro.E),'\\x67\\x73\\x68\\x48\\x57':function(c,N){return c(N);},'\\x7a\\x52\\x4f\\x4c\\x41':A(Ro.u),'\\x55\\x6d\\x58\\x45\\x72':function(c,N){return c(N);},'\\x64\\x61\\x73\\x53\\x4a':A(Ro.C),'\\x78\\x67\\x48\\x50\\x7a':function(c,N){return c(N);},'\\x53\\x61\\x56\\x6e\\x77':function(c,N){return c(N);},'\\x47\\x49\\x59\\x49\\x66':function(c,N,S,q){return c(N,S,q);},'\\x48\\x78\\x73\\x53\\x71':function(c,N){return c!=N;},'\\x4a\\x73\\x6f\\x58\\x66':A(Ro.U),'\\x4b\\x78\\x44\\x50\\x78':A(Ro.T),'\\x4a\\x46\\x67\\x43\\x65':function(c,N,S){return c(N,S);},'\\x45\\x49\\x71\\x61\\x54':function(c,N){return c>N;},'\\x4d\\x6e\\x50\\x55\\x67':function(c,N){return c(N);},'\\x72\\x4a\\x59\\x4c\\x75':function(c,N){return c(N);},'\\x41\\x51\\x49\\x76\\x5a':function(c,N,S){return c(N,S);},'\\x50\\x65\\x68\\x78\\x62':A(Ro.z)+A(Ro.P)+A(Ro.e)+A(Ro.L)+A(Ro.o)+'\\x73\\x74','\\x43\\x69\\x58\\x57\\x4d':A(Ro.l)+A(Ro.f)+A(Ro.V)+A(Ro.m)+A(Ro.j)+A(Ro.c),'\\x4b\\x48\\x4d\\x55\\x4e':A(Ro.N)+A(Ro.S)+A(Ro.q)+A(Ro.y),'\\x74\\x73\\x67\\x6e\\x64':function(c,N){return c(N);}};let {EVENT_NAMES:O,request:w,on:g,send:h,env:E,version:C,currentScriptInfo:U,utils:T}=globalThis['\\x6c\\x78'],z=(c,N)=>{const i=A;switch(c){case'\\x74\\x78':case'\\x77\\x79':case'\\x6b\\x77':return N[i(Rw.p)];case'\\x6b\\x67':return N[i(Rw.O)];case'\\x6d\\x67':return N[i(Rw.w)+'\\x64'];}throw p[i(Rw.r)](Error,p[i(Rw.g)]);},P={'\\x55\\x73\\x65\\x72\\x2d\\x41\\x67\\x65\\x6e\\x74':A(Ro.G)+E,'\\x76\\x65\\x72':C,'\\x73\\x6f\\x75\\x72\\x63\\x65\\x2d\\x76\\x65\\x72':U[A(Ro.F)]};p[A(Ro.K)](g,O[A(Ro.b)],({source:c,action:N,info:{musicInfo:S,type:q}})=>{const RE={p:'\\x30\\x78\\x63\\x65',O:0xe9,w:'\\x30\\x78\\x64\\x32',r:0x119,g:'\\x30\\x78\\x63\\x38',h:0x119,E:0xfc,u:'\\x30\\x78\\x31\\x31\\x35',C:'\\x30\\x78\\x63\\x62',U:0xda,T:0xeb,z:'\\x30\\x78\\x62\\x37',P:0xe7,e:0x106},Rg={p:0xfb},J=A,y={'\\x74\\x53\\x71\\x51\\x6f':function(G,F,K){const B=Z;return p[B(Rr.p)](G,F,K);},'\\x65\\x72\\x45\\x73\\x57':p[J(Ru.p)],'\\x78\\x42\\x41\\x57\\x4f':function(G,F,K,b){const x=J;return p[x(Rg.p)](G,F,K,b);},'\\x72\\x62\\x72\\x71\\x66':function(G,F){const W=J;return p[W(Rh.p)](G,F);},'\\x41\\x62\\x61\\x63\\x4a':p[J(Ru.O)],'\\x4d\\x76\\x7a\\x48\\x46':p[J(Ru.w)]};if(p[J(Ru.r)](p[J(Ru.g)],N))throw p[J(Ru.h)](Error,p[J(Ru.E)]);return new Promise((G,F)=>{const Y=J;let K=Y(RE.p)+c+'\\x2f'+y[Y(RE.O)](z,c,S)+'\\x2f'+q;P[Y(RE.w)]=T[Y(RE.r)][Y(RE.g)+'\\x67'](T[Y(RE.h)][Y(RE.E)](JSON[Y(RE.u)](K[Y(RE.C)](/(?:\\d\\w)+/g),null,0x216b+0x1224+-0x338e)),y[Y(RE.U)]),y[Y(RE.T)](w,y[Y(RE.z)](y[Y(RE.P)],K),{'\\x6d\\x65\\x74\\x68\\x6f\\x64':y[Y(RE.e)],'\\x68\\x65\\x61\\x64\\x65\\x72\\x73':P},(b,D)=>b?F(b):0x1e52+0x2476+-0x42c8!==D[Y(0x11b)][Y(0xd6)]?F(Error(D[Y(0x11b)][Y(0xf6)])):void G(D[Y(0x11b)][Y(0x103)]));});});let L=c=>new Promise((N,S)=>{const Rz={p:'\\x30\\x78\\x31\\x31\\x62',O:'\\x30\\x78\\x63\\x36',w:0xbc,r:0xbc,g:'\\x30\\x78\\x31\\x31\\x31',h:'\\x30\\x78\\x31\\x31\\x62',E:0xc6,u:'\\x30\\x78\\x62\\x61',C:0xc2,U:0x11b,T:'\\x30\\x78\\x63\\x36',z:0xc0},RT={p:'\\x30\\x78\\x64\\x33'},RU={p:0x10b},RC={p:'\\x30\\x78\\x66\\x32'},Q=A,q={'\\x71\\x57\\x49\\x57\\x44':function(y,G){const a=Z;return p[a(RC.p)](y,G);},'\\x59\\x4e\\x4f\\x65\\x45':p[Q(RP.p)],'\\x77\\x75\\x63\\x4c\\x7a':function(y,G){const s=Q;return p[s(RU.p)](y,G);},'\\x47\\x61\\x6d\\x46\\x4f':function(y,G){const H=Q;return p[H(RT.p)](y,G);}};p[Q(RP.O)](w,c,{'\\x6d\\x65\\x74\\x68\\x6f\\x64':p[Q(RP.w)]},(y,G,F)=>{const I=Q;if(y||!G[I(Rz.p)][I(Rz.O)])return q[I(Rz.w)](S,q[I(Rz.r)](Error,q[I(Rz.g)]));(F=G[I(Rz.h)][I(Rz.E)]?.[U[I(Rz.u)]])?q[I(Rz.C)](N,{'\\x73':F['\\x73'],'\\x6d':F['\\x6d'],'\\x6c\\x76':G[I(Rz.U)][I(Rz.O)]['\\x6c\\x76'],'\\x6c\\x75':G[I(Rz.U)][I(Rz.O)]['\\x6c\\x75'],'\\x6c\\x68':G[I(Rz.p)][I(Rz.T)]['\\x6c\\x68']}):q[I(Rz.z)](N,null);});}),V=[p[A(Ro.t)],p[A(Ro.D)]],j={'\\x73':p[A(Ro.Rl)]};Promise[A(Ro.Rf)]([p[A(Ro.RV)](L,V[-0x1*-0x134e+0x3*-0xcdc+0x1346]),p[A(Ro.Rm)](L,V[-0x12c4+0x1e65+-0xba0])])[A(Ro.Rj)](c=>{j=c;})[A(Ro.Rc)](()=>{const k=A;if(!j||j['\\x6d']&&p[k(RL.p)](T[k(RL.O)][k(RL.w)](U[k(RL.r)][k(RL.g)]()),j['\\x6d']))throw p[k(RL.h)](Error,p[k(RL.E)]);let c={};for(let S of j['\\x73'][k(RL.u)]()[k(RL.C)]('\\x26'))c[(S=S[k(RL.U)]('\\x7c'))[k(RL.T)]()]={'\\x74\\x79\\x70\\x65':p[k(RL.z)],'\\x61\\x63\\x74\\x69\\x6f\\x6e\\x73':[p[k(RL.P)]],'\\x71\\x75\\x61\\x6c\\x69\\x74\\x79\\x73':S};const N={};N[k(RL.e)]=c,(p[k(RL.L)](h,O[k(RL.o)],N),j['\\x6c\\x76']&&p[k(RL.l)](p[k(RL.f)](parseInt,j['\\x6c\\x76']),p[k(RL.V)](parseInt,U[k(RL.m)]))&&p[k(RL.j)](h,O[k(RL.c)+'\\x74'],{'\\x6c\\x6f\\x67':j['\\x6c\\x75'],'\\x75\\x70\\x64\\x61\\x74\\x65\\x55\\x72\\x6c':j['\\x6c\\x68']}));});})()));function Z(p,O){const w=R();return Z=function(r,g){r=r-(-0x914+-0xf05+0x18cf);let h=w[r];return h;},Z(p,O);}function R(){const Rl=['\\x6b\\x77\\x7c\\x31\\x32\\x38\\x6b\\x26\\x77\\x79','\\x37\\x71\\x7a\\x7a\\x72\\x4a\\x64','\\x43\\x69\\x58\\x57\\x4d','\\x66\\x69\\x61\\x6c\\x65\\x64','\\x67\\x73\\x68\\x48\\x57','\\x6c\\x78\\x2d\\x6d\\x75\\x73\\x69\\x63\\x2f','\\x64\\x61\\x74\\x61','\\x63\\x72\\x79\\x70\\x74\\x6f','\\x7c\\x31\\x32\\x38\\x6b\\x26\\x6d\\x67\\x7c\\x31','\\x4d\\x76\\x7a\\x48\\x46','\\x2d\\x69\\x6e\\x66\\x6f\\x2f\\x6c\\x61\\x74\\x65','\\x61\\x6e\\x79','\\x34\\x70\\x7a\\x65\\x56\\x52\\x58','\\x36\\x30\\x36\\x39\\x36\\x31\\x38\\x79\\x72\\x43\\x6a\\x74\\x53','\\x78\\x67\\x48\\x50\\x7a','\\x68\\x74\\x74\\x70\\x3a\\x2f\\x2f\\x39\\x37\\x2e','\\x6c\\x61\\x74\\x65\\x73\\x74','\\x38\\x34\\x32\\x34\\x34\\x51\\x55\\x55\\x6f\\x70\\x77','\\x6a\\x73\\x2e\\x6f\\x72\\x67\\x2f\\x66\\x6c\\x6f','\\x67\\x69\\x73\\x74\\x72\\x79\\x2e\\x6e\\x70\\x6d','\\x59\\x4e\\x4f\\x65\\x45','\\x38\\x75\\x47\\x47\\x55\\x49\\x51','\\x75\\x70\\x64\\x61\\x74\\x65\\x41\\x6c\\x65\\x72','\\x4d\\x6e\\x50\\x55\\x67','\\x73\\x74\\x72\\x69\\x6e\\x67\\x69\\x66\\x79','\\x68\\x61\\x73\\x68','\\x34\\x35\\x36\\x32\\x35\\x35\\x38\\x48\\x4b\\x44\\x6f\\x67\\x6c','\\x41\\x51\\x49\\x76\\x5a','\\x62\\x75\\x66\\x66\\x65\\x72','\\x4a\\x46\\x67\\x43\\x65','\\x62\\x6f\\x64\\x79','\\x31\\x37\\x34\\x36\\x39\\x37\\x32\\x78\\x67\\x71\\x46\\x62\\x47','\\x4b\\x78\\x44\\x50\\x78','\\x34\\x33\\x32\\x36\\x35\\x34\\x36\\x4a\\x75\\x6a\\x66\\x66\\x51','\\x72\\x62\\x72\\x71\\x66','\\x63\\x6f\\x70\\x79\\x72\\x69\\x67\\x68\\x74\\x49','\\x6e\\x59\\x61\\x68\\x77','\\x76\\x65\\x72\\x73\\x69\\x6f\\x6e','\\x47\\x49\\x59\\x49\\x66','\\x71\\x57\\x49\\x57\\x44','\\x4a\\x73\\x6f\\x58\\x66','\\x51\\x5a\\x6b\\x43\\x73','\\x69\\x6e\\x69\\x74\\x65\\x64','\\x47\\x61\\x6d\\x46\\x4f','\\x66\\x69\\x6e\\x61\\x6c\\x6c\\x79','\\x77\\x75\\x63\\x4c\\x7a','\\x34\\x31\\x30\\x34\\x31\\x38\\x30\\x66\\x69\\x6a\\x49\\x62\\x41','\\x42\\x4d\\x51\\x46\\x62','\\x6d\\x75\\x73\\x69\\x63\\x55\\x72\\x6c','\\x76\\x69\\x6e\\x66\\x6f','\\x74\\x68\\x65\\x6e','\\x62\\x75\\x66\\x54\\x6f\\x53\\x74\\x72\\x69\\x6e','\\x64\\x63\\x41\\x4c\\x4e','\\x66\\x44\\x6d\\x6b\\x4b','\\x6d\\x61\\x74\\x63\\x68','\\x73\\x6f\\x6e\\x67\\x6d\\x69\\x64','\\x7a\\x52\\x4f\\x4c\\x41','\\x2f\\x75\\x72\\x6c\\x2f','\\x73\\x70\\x6c\\x69\\x74','\\x77\\x65\\x72\\x2d\\x73\\x6f\\x75\\x72\\x63\\x65','\\x72\\x65\\x71\\x75\\x65\\x73\\x74','\\x74\\x61\\x67','\\x53\\x61\\x56\\x6e\\x77','\\x6d\\x75\\x73\\x69\\x63','\\x36\\x34\\x2e\\x33\\x37\\x2e\\x32\\x33\\x35\\x2f','\\x63\\x6f\\x64\\x65','\\x48\\x78\\x73\\x53\\x71','\\x4b\\x48\\x4d\\x55\\x4e','\\x6e\\x42\\x66\\x48\\x77','\\x65\\x72\\x45\\x73\\x57','\\x6f\\x64\\x79\\x51\\x6a','\\x74\\x73\\x67\\x6e\\x64','\\x64\\x61\\x73\\x53\\x4a','\\x6b\\x26\\x6b\\x67\\x7c\\x31\\x32\\x38\\x6b','\\x34\\x37\\x30\\x6a\\x68\\x48\\x6d\\x56\\x4d','\\x68\\x65\\x78','\\x62\\x46\\x74\\x70\\x48','\\x68\\x74\\x74\\x70\\x73\\x3a\\x2f\\x2f\\x72\\x65','\\x45\\x49\\x71\\x61\\x54','\\x50\\x65\\x68\\x78\\x62','\\x31\\x31\\x37\\x36\\x33\\x34\\x4b\\x52\\x51\\x68\\x46\\x49','\\x66\\x6c\\x6f\\x77\\x65\\x72\\x2f\\x76\\x31','\\x41\\x62\\x61\\x63\\x4a','\\u670d\\u52a1\\u5668\\u5f02\\u5e38','\\x74\\x53\\x71\\x51\\x6f','\\x75\\x72\\x63\\x65\\x2d\\x69\\x6e\\x66\\x6f\\x2f','\\x78\\x42\\x41\\x57\\x4f','\\x32\\x38\\x6b\\x26\\x74\\x78\\x7c\\x31\\x32\\x38','\\x43\\x70\\x6d\\x41\\x48','\\x6d\\x69\\x72\\x72\\x6f\\x72\\x2e\\x63\\x6f\\x6d','\\x74\\x72\\x69\\x6d','\\x6d\\x64\\x35','\\x2f\\x66\\x6c\\x6f\\x77\\x65\\x72\\x2d\\x73\\x6f','\\x55\\x6d\\x58\\x45\\x72','\\x46\\x41\\x49\\x4c\\x45\\x44','\\x73\\x6f\\x75\\x72\\x63\\x65\\x73','\\x72\\x61\\x77\\x53\\x63\\x72\\x69\\x70\\x74','\\x6d\\x73\\x67','\\x47\\x45\\x54','\\x72\\x4a\\x59\\x4c\\x75','\\x66\\x61\\x69\\x6c\\x65\\x64','\\x73\\x68\\x69\\x66\\x74','\\x6d\\x44\\x42\\x63\\x4e','\\x66\\x72\\x6f\\x6d'];R=function(){return Rl;};return R();}"
(ROOT / "src/sources/builtinWildflower.ts").write_text(
    "const wildflowerScript = " + json.dumps(wildflower_script, ensure_ascii=False) + "\nexport default wildflowerScript\n",
    encoding="utf-8",
)

p = ROOT / "src/core/init/index.ts"
s = p.read_text()
if "importUserApi" not in s:
    s = s.replace(
        "import initUserApi from './userApi'\n",
        "import initUserApi from './userApi'\nimport { importUserApi } from '@/core/userApi'\nimport { getData, saveData } from '@/plugins/storage'\nimport wildflowerScript from '@/sources/builtinWildflower'\nimport { state as userApiState } from '@/store/userApi/state'\n",
        1,
    )
anchor = "  await initUserApi(setting)\n  bootLog('User Api inited.')\n"
if "wildflowerInstallKey" not in s:
    if anchor not in s:
        raise SystemExit("Expected initUserApi anchor not found (built-in Wildflower source)")
    s = s.replace(anchor, anchor + """  const wildflowerInstallKey = '@lx_builtin_wildflower_installed_v1'
  if (!(await getData<boolean>(wildflowerInstallKey))) {
    if (!userApiState.list.some(item => item.name === '野花🌷')) {
      await importUserApi(wildflowerScript)
    }
    await saveData(wildflowerInstallKey, true)
  }
""", 1)
p.write_text(s)
print("Applied: install built-in Wildflower source once; user can remove it permanently")


# Hide the entire lyric/status text row only in the left home player.
# Keep song title, elapsed/total time, progress bar, and controls unchanged.
p = "src/components/player/PlayerBar/components/PlayInfo.tsx"
s = (ROOT / p).read_text()
old_status_row = """      <View style={styles.status}>
        <Status autoUpdate={autoUpdate} />
      </View>
"""
new_status_row = """      {!isHome && (
        <View style={styles.status}>
          <Status autoUpdate={autoUpdate} />
        </View>
      )}
"""
if old_status_row not in s:
    raise SystemExit("Expected PlayInfo status row not found; refusing to build without applying lyric-row fix")
s = s.replace(old_status_row, new_status_row, 1)
(ROOT / p).write_text(s)
print("Applied: hide lyric/status row only in the left home player")


# Match the requested custom-source settings layout:
# remove multi-source auto toggle, add per-source trash, and show two direct import buttons.
p = "src/screens/Home/Views/Setting/settings/Basic/UserApiEditModal/ImportBtn.tsx"
s = (ROOT / p).read_text()
s = s.replace(
    "interface BtnProps {\n  btnStyle?: _DorpDownMenuProps<any[]>['btnStyle']\n}",
    "interface BtnProps {\n  btnStyle?: _DorpDownMenuProps<any[]>['btnStyle']\n  mode?: 'local' | 'online'\n}",
    1,
)
s = s.replace(
    "export default ({ btnStyle }: BtnProps) => {",
    "export default ({ btnStyle, mode }: BtnProps) => {",
    1,
)
s = s.replace(
    "import { useTheme } from '@/store/theme/hook'\n",
    "import { useTheme } from '@/store/theme/hook'\nimport Button from '@/components/common/Button'\n",
    1,
)
old_return = """  return (
    <DorpDownMenu
      btnStyle={btnStyle}
      menus={importTypes}
      center
      onPress={handleAction}
    >
      <Text size={14} color={theme['c-button-font']}>{t('user_api_btn_import')}</Text>
      <ScriptImportExport ref={scriptImportExportRef} />
      <ScriptImportOnline ref={scriptImportOnlineRef} />
    </DorpDownMenu>
  )
"""
new_return = """  if (mode) {
    return (
      <Button
        style={btnStyle}
        onPress={() => {
          if (state.list.length > 20) {
            void tipDialog({ message: t('user_api_max_tip'), btnText: t('ok') })
            return
          }
          if (mode === 'local') scriptImportExportRef.current?.import()
          else scriptImportOnlineRef.current?.show()
        }}
      >
        <Text size={14} color={theme['c-button-font']}>
          {mode === 'local' ? '從本機匯入' : '從線上匯入'}
        </Text>
        <ScriptImportExport ref={scriptImportExportRef} />
        <ScriptImportOnline ref={scriptImportOnlineRef} />
      </Button>
    )
  }

  return (
    <DorpDownMenu btnStyle={btnStyle} menus={importTypes} center onPress={handleAction}>
      <Text size={14} color={theme['c-button-font']}>{t('user_api_btn_import')}</Text>
      <ScriptImportExport ref={scriptImportExportRef} />
      <ScriptImportOnline ref={scriptImportOnlineRef} />
    </DorpDownMenu>
  )
"""
if old_return not in s: raise SystemExit("ImportBtn return block not found")
s = s.replace(old_return, new_return, 1)
(ROOT / p).write_text(s)

p = "src/screens/Home/Views/Setting/settings/Basic/Source.tsx"
s = (ROOT / p).read_text()
s = s.replace("import { memo, useCallback, useMemo, useRef } from 'react'", "import { memo, useCallback, useMemo } from 'react'", 1)
s = s.replace("import Button from '../../components/Button'\n", "", 1)
s = s.replace("import UserApiEditModal, { type UserApiEditModalType } from './UserApiEditModal'\n", "", 1)
s = s.replace("import Text from '@/components/common/Text'\n", """import Text from '@/components/common/Text'
import ImportBtn from './UserApiEditModal/ImportBtn'
import { Icon } from '@/components/common/Icon'
import { TouchableOpacity } from 'react-native'
import { confirmDialog } from '@/utils/tools'
import { removeUserApi } from '@/core/userApi'
import { state as userApiState } from '@/store/userApi'
import settingState from '@/store/setting/state'
""", 1)
# The multi-source auto selector is intentionally removed from the rendered list.
s = s.replace("""        {!userApiList.length ? <Text>请在设置中导入自定义源</Text> : (
          <Item name="多源自动切换" id="user_api_auto" change={id => { setApiSourceId(apiSourceSetting === id ? userApiList[0].id : id) }} />
        )}
""", "", 1)
# Add a delete affordance beside each user-defined source, preserving its selection checkbox.
old_map = """          userApiList.map(({ id, name, desc, statusLabel }) => <Item name={name} desc={desc} statusLabel={statusLabel} id={id} key={id} change={setApiSourceId} />)
"""
new_map = """          userApiList.map(({ id, name, desc, statusLabel }) => (
            <View key={id} style={styles.userSourceRow}>
              <View style={styles.userSourceItem}>
                <Item name={name} desc={desc} statusLabel={statusLabel} id={id} change={setApiSourceId} />
              </View>
              <TouchableOpacity
                accessibilityLabel="刪除自訂來源"
                style={styles.deleteSource}
                onPress={async() => {
                  const confirmed = await confirmDialog({
                    message: global.i18n.t('user_api_remove_tip', { name }),
                    cancelButtonText: global.i18n.t('cancel_button_text_2'),
                    confirmButtonText: global.i18n.t('confirm_button_text'),
                    bgClose: false,
                  })
                  if (!confirmed) return
                  void removeUserApi([id]).finally(() => {
                    if (settingState.setting['common.apiSource'] === id || !userApiState.list.length) {
                      const fallback = apiSourceList.find(api => !api.disabled)?.id ?? userApiState.list[0]?.id ?? ''
                      setApiSource(fallback)
                    }
                  })
                }}
              >
                <Icon name="trash-2" color="#888888" size={20} />
              </TouchableOpacity>
            </View>
          ))
"""
if old_map not in s: raise SystemExit("Custom source list render not found")
s = s.replace(old_map, new_map, 1)
old_button = """      <View style={styles.btn}>
        <Button onPress={handleShow}>{t('setting_basic_source_user_api_btn')}</Button>
      </View>
"""
new_button = """      <View style={styles.importButtons}>
        <ImportBtn mode="local" btnStyle={styles.importButton} />
        <ImportBtn mode="online" btnStyle={styles.importButton} />
      </View>
"""
if old_button not in s: raise SystemExit("Source management button block not found")
s = s.replace(old_button, new_button, 1)
s = s.replace("      <UserApiEditModal ref={modalRef} />\n", "", 1)
# Remove the obsolete modal refs and handler.
s = s.replace("""  const modalRef = useRef<UserApiEditModalType>(null)
  const handleShow = () => {
    modalRef.current?.show()
  }

""", "", 1)
# Styles: side-by-side import buttons and a compact delete icon aligned with each source.
s = s.replace("""  btn: {
    marginTop: 10,
    flexDirection: 'row',
  },
""", """  importButtons: {
    marginTop: 10,
    flexDirection: 'row',
    gap: 12,
  },
  importButton: {
    flex: 1,
    minWidth: 0,
  },
  userSourceRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  userSourceItem: {
    flex: 1,
  },
  deleteSource: {
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
""", 1)
(ROOT / p).write_text(s)
print("Applied: requested custom-source layout with direct local/online import and delete icon")
