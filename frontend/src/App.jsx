import { useEffect, useState } from 'react'
import { generate, health } from './api'
import Studio from './pages/Studio'
import VoiceDna from './pages/VoiceDna'
import Compare from './pages/Compare'
import Demo from './pages/Demo'

const TABS = [
  { id: 'studio', label: 'Studio' },
  { id: 'voice', label: 'Voice DNA' },
  { id: 'compare', label: 'Compare' },
  { id: 'demo', label: 'Demo' },
]

export default function App() {
  const [tab, setTab] = useState('studio')
  const [provider, setProvider] = useState('…')
  const [result, setResult] = useState(null)
  const [briefSeed, setBriefSeed] = useState(null)

  useEffect(() => {
    health().then((h) => setProvider(h.provider || (h.demo_mode ? 'DEMO MODE' : 'Live')))
  }, [])

  const loadBrief = (b) => {
    setBriefSeed({ ...b })
    setTab('studio')
  }

  const quickGenerate = async (b) => {
    const brief = {
      brand_product: b.brand_product,
      campaign_goal: b.campaign_goal,
      audience: b.audience,
      key_facts: b.key_facts,
      tone: b.tone,
    }
    const data = await generate(brief)
    setResult(data)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              OmniPost <span className="text-indigo-600">AI</span>
            </h1>
            <p className="text-sm text-slate-500">One brief → native posts → voice & facts → approve</p>
          </div>
          <nav className="flex flex-wrap gap-1 rounded-lg bg-slate-100 p-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  tab === t.id ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {t.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
        {tab === 'studio' && (
          <Studio key={briefSeed?.id || 'default'} initialBrief={briefSeed} result={result} setResult={setResult} />
        )}
        {tab === 'voice' && <VoiceDna result={result} />}
        {tab === 'compare' && <Compare />}
        {tab === 'demo' && <Demo onLoadBrief={loadBrief} onQuickGenerate={quickGenerate} />}
      </main>

      <footer className="border-t border-slate-200 bg-white py-3 text-center text-xs text-slate-500">
        {provider === 'DEMO MODE' ? (
          <span className="font-semibold text-amber-700">DEMO MODE</span>
        ) : (
          <span>{provider}</span>
        )}
      </footer>

    </div>
  )
}
