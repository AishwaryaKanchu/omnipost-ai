const BASE = '/api'

export async function health() {
  const r = await fetch(`${BASE}/health`)
  if (!r.ok) throw new Error(`Health check failed (${r.status})`)
  return r.json()
}

export async function fetchSamples() {
  const r = await fetch(`${BASE}/samples`)
  if (!r.ok) throw new Error(`Fetch samples failed (${r.status})`)
  return r.json()
}

export async function fetchCompare() {
  const r = await fetch(`${BASE}/compare`)
  if (!r.ok) throw new Error(`Fetch compare failed (${r.status})`)
  return r.json()
}

export async function generate(brief = {}, options = {}) {
  const goldenId = options?.goldenId
  const payload = {
    brand_product: brief?.brand_product ?? '',
    campaign_goal: brief?.campaign_goal ?? '',
    audience: brief?.audience ?? '',
    key_facts: brief?.key_facts ?? '',
    tone: brief?.tone ?? '',
  }
  if (brief?.voice_samples) {
    payload.voice_samples = brief.voice_samples
  }
  if (goldenId) {
    payload.golden_id = goldenId
  }

  const r = await fetch(`${BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!r.ok) {
    let msg = `Generate failed (${r.status})`
    try {
      const errData = await r.json()
      if (errData?.detail) {
        msg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail)
      } else if (errData?.message) {
        msg = errData.message
      }
    } catch (_) {}
    throw new Error(msg)
  }
  return r.json()
}

export async function learn(platform, before, after) {
  const r = await fetch(`${BASE}/learn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ platform, before, after }),
  })
  if (!r.ok) throw new Error(`Learn failed (${r.status})`)
  return r.json()
}

export async function approve(platform, content) {
  const r = await fetch(`${BASE}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ platform, content }),
  })
  if (!r.ok) throw new Error(`Approve failed (${r.status})`)
  return r.json()
}
