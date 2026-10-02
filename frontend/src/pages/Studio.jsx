import { useState } from 'react'
import { generate, learn, approve } from '../api'
import PlatformCard from '../components/PlatformCard'

const emptyBrief = {
  brand_product: '',
  campaign_goal: '',
  audience: '',
  key_facts: '',
  tone: '',
}

export default function Studio({ result, setResult }) {
  const [brief, setBrief] = useState(emptyBrief)
  const [loading, setLoading] = useState(false)
  const [editing, setEditing] = useState(null)
  const [editValue, setEditValue] = useState('')
  const [learnMsgs, setLearnMsgs] = useState({})
  const [approved, setApproved] = useState({})

  const setField = (k, v) => setBrief((b) => ({ ...b, [k]: v }))

  const runGenerate = async () => {
    setLoading(true)
    setLearnMsgs({})
    setApproved({})
    try {
      const data = await generate(brief)
      setResult(data)
    } catch (e) {
      alert(e.message)
    } finally {
      setLoading(false)
    }
  }

  const startEdit = (platform) => {
    setEditing(platform)
    setEditValue(result?.posts?.[platform] || '')
  }

  const saveEdit = async (platform) => {
    const before = result.posts[platform]
    const after = editValue
    setResult((r) => ({
      ...r,
      posts: { ...r.posts, [platform]: after },
    }))
    setEditing(null)
    const res = await learn(platform, before, after)
    setLearnMsgs((m) => ({ ...m, [platform]: res.message }))
  }

  const copyPost = (platform) => {
    navigator.clipboard.writeText(result.posts[platform])
  }

  const doApprove = async (platform) => {
    await approve(platform, result.posts[platform])
    setApproved((a) => ({ ...a, [platform]: true }))
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Campaign brief</h2>
        <p className="mt-1 text-sm text-slate-500">One brief → three platform-native posts</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {[
            ['brand_product', 'Brand / product'],
            ['campaign_goal', 'Campaign goal'],
            ['audience', 'Audience'],
            ['tone', 'Tone'],
          ].map(([key, label]) => (
            <label key={key} className="block text-sm">
              <span className="font-medium text-slate-700">{label}</span>
              <input
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                value={brief[key]}
                onChange={(e) => setField(key, e.target.value)}
              />
            </label>
          ))}
          <label className="block text-sm md:col-span-2">
            <span className="font-medium text-slate-700">Key facts (only use these numbers & claims)</span>
            <textarea
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              rows={3}
              value={brief.key_facts}
              onChange={(e) => setField('key_facts', e.target.value)}
            />
          </label>
        </div>
        <button type="button" onClick={runGenerate} disabled={loading} className="btn-primary mt-4">
          {loading ? 'Generating…' : 'Generate 3 Posts'}
        </button>
      </section>

      {!result?.posts && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center text-slate-500">
          Enter your campaign brief and generate platform-native posts.
        </div>
      )}

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
              approved={approved[p]}
              editing={editing === p}
              editValue={editValue}
              onEdit={() => startEdit(p)}
              onEditChange={setEditValue}
              onSaveEdit={() => saveEdit(p)}
              onCancelEdit={() => setEditing(null)}
              onCopy={() => copyPost(p)}
              onApprove={() => doApprove(p)}
              learnMessage={learnMsgs[p]}
            />
          ))}
        </div>
      )}
    </div>
  )
}
