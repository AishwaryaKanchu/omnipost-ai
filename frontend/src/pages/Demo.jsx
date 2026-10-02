import { useEffect, useState } from 'react'
import { fetchSamples, generate } from '../api'
import PlatformCard from '../components/PlatformCard'

export default function Demo({ result, setResult }) {
  const [briefs, setBriefs] = useState([])
  const [loadingId, setLoadingId] = useState(null)

  useEffect(() => {
    fetchSamples().then((d) => setBriefs(d.briefs || []))
  }, [])

  const runDemo = async (b) => {
    setLoadingId(b.id)
    try {
      const data = await generate(b, { goldenId: b.id })
      setResult(data)
    } catch (e) {
      alert(e.message)
    } finally {
      setLoadingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-600">
        Presentation-only golden demos — results stay on this tab. Use <strong>Voice Match Demo</strong> for 71 → 88
        and <strong>Fact Guard Demo</strong> for unsupported claims. Studio uses your own brief when you click
        Generate.
      </p>
      <div className="grid gap-4 md:grid-cols-3">
        {briefs.map((b) => (
          <div key={b.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="font-semibold">{b.label}</h3>
            <p className="mt-1 text-xs text-slate-500">{b.brand_product}</p>
            <button
              type="button"
              className="btn-primary mt-3 w-full text-sm"
              disabled={loadingId === b.id}
              onClick={() => runDemo(b)}
            >
              {loadingId === b.id ? 'Running…' : 'Run demo'}
            </button>
          </div>
        ))}
      </div>

      {result?.posts && (
        <div className="grid gap-6 lg:grid-cols-3">
          {['instagram', 'linkedin', 'x'].map((p) => (
            <PlatformCard
              key={p}
              platform={p}
              content={result.posts[p]}
              angle={result.angles?.[p]}
              voiceScore={result.voice_scores?.[p]}
              voiceRewrite={result.voice_rewrites?.[p]}
              factGuard={result.fact_guard}
              suggestedAudio={result?.suggested_audio}
              approved={false}
              editing={false}
              onEdit={() => {}}
              onCopy={() => navigator.clipboard.writeText(result.posts[p])}
              onApprove={() => {}}
            />
          ))}
        </div>
      )}
    </div>
  )
}
