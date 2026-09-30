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

export async function generate(brief) {
  const r = await fetch(`${BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(brief),
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
