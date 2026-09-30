const BASE = '/api'

export async function health() {
  const r = await fetch(`${BASE}/health`)
  return r.json()
}

export async function fetchSamples() {
  const r = await fetch(`${BASE}/samples`)
  return r.json()
}

export async function fetchCompare() {
  const r = await fetch(`${BASE}/compare`)
  return r.json()
}

export async function generate(brief, { goldenId } = {}) {
  const payload = {
    brand_product: brief.brand_product ?? '',
    campaign_goal: brief.campaign_goal ?? '',
    audience: brief.audience ?? '',
    key_facts: brief.key_facts ?? '',
    tone: brief.tone ?? '',
  }
  if (goldenId) payload.golden_id = goldenId

  const r = await fetch(`${BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!r.ok) throw new Error('Generate failed')
  return r.json()
}

export async function learn(platform, before, after) {
  const r = await fetch(`${BASE}/learn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ platform, before, after }),
  })
  return r.json()
}

export async function approve(platform, content) {
  const r = await fetch(`${BASE}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ platform, content }),
  })
  return r.json()
}
