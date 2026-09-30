import { useEffect, useState } from 'react'
import { fetchSamples } from '../api'

export default function Demo({ onLoadBrief, onQuickGenerate }) {
  const [briefs, setBriefs] = useState([])

  useEffect(() => {
    fetchSamples().then((d) => setBriefs(d.briefs || []))
  }, [])

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-600">
        Load a sample brief and jump to Studio. Use <strong>Voice Match Demo</strong> for the 71 → 88 rewrite and{' '}
        <strong>Fact Guard Demo</strong> for unsupported claims — no API keys required.
      </p>
      <div className="grid gap-4 md:grid-cols-3">
        {briefs.map((b) => (
          <div key={b.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="font-semibold">{b.label}</h3>
            <p className="mt-1 text-xs text-slate-500">{b.brand_product}</p>
            <button
              type="button"
              className="btn-primary mt-3 w-full text-sm"
              onClick={() => {
                onLoadBrief(b)
                onQuickGenerate?.(b)
              }}
            >
              Run demo
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
