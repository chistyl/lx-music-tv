from pathlib import Path

target = Path("upstream/lx-music-mobile-auto-source/src/utils/chineseTraditional.ts")
source = target.read_text(encoding="utf-8")

old = """export const toTraditionalString = (value: string): string => convertToTraditional(value)

export const toTraditionalText = (value: ReactNode): ReactNode => Children.map(value, item => {
  return typeof item === 'string' ? convertToTraditional(item) : item
})
"""
new = """// Simplified-to-Traditional conversion is active only while the app UI language
// is Taiwan Traditional Chinese. Other language selections remain untouched.
const isTraditionalChineseLanguage = (): boolean => global.i18n?.locale === 'zh_tw'

export const toTraditionalString = (value: string): string => {
  return isTraditionalChineseLanguage() ? convertToTraditional(value) : value
}

export const toTraditionalText = (value: ReactNode): ReactNode => {
  if (!isTraditionalChineseLanguage()) return value
  return Children.map(value, item => {
    return typeof item === 'string' ? convertToTraditional(item) : item
  })
}
"""

if old not in source:
    if new in source:
        print("Already applied: conversion is limited to Traditional Chinese UI language")
    else:
        raise SystemExit("Expected conversion helper source block not found")
else:
    target.write_text(source.replace(old, new, 1), encoding="utf-8")
    print("Applied: enable conversion only when global.i18n.locale is zh_tw")

print("Traditional Chinese conversion language gate completed.")
