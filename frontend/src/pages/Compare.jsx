import { useEffect, useState } from 'react'
import { fetchCompare } from '../api'

export default function Compare() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetchCompare().then(setData)
  }, [])

  if (!data) return <p className="text-slate-500">Loading comparison…</p>

  return (
    <div className="space-y-6">
      <p className="rounded-lg bg-amber-50 px-4 py-2 text-sm text-amber-900">{data.label}</p>
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3 font-medium">Metric</th>
              <th className="px-4 py-3 font-medium">Baseline AI</th>
              <th className="px-4 py-3 font-medium">OmniPost</th>
            </tr>
          </thead>
          <tbody>
            {data.metrics.map((row) => (
              <tr key={row.name} className="border-t border-slate-100">
                <td className="px-4 py-3">{row.name}</td>
                <td className="px-4 py-3 text-slate-600">
                  {row.baseline} {row.unit}
                </td>
                <td className="px-4 py-3 font-medium text-indigo-700">
                  {row.omnipost} {row.unit}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="font-semibold text-slate-800">Baseline AI (one-size-fits-all)</h3>
          <p className="mt-2 text-sm text-slate-600">{data.baseline_sample}</p>
        </div>
        <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-4">
          <h3 className="font-semibold text-indigo-900">OmniPost</h3>
          <p className="mt-2 text-sm text-indigo-800">{data.omnipost_note}</p>
        </div>
      </div>
    </div>
  )
}
