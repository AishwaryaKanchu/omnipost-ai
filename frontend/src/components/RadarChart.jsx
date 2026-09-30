/** Simple SVG radar for Voice DNA (no chart library). */
export default function RadarChart({ dna }) {
  if (!dna) return null

  const axes = [
    { key: 'avg_sentence_length', label: 'Sent len', max: 25 },
    { key: 'emoji_rate', label: 'Emoji', max: 5 },
    { key: 'hashtag_rate', label: 'Hashtags', max: 8 },
    { key: 'exclamation_rate', label: 'Exclaim', max: 10 },
    { key: 'question_rate', label: 'Questions', max: 10 },
  ]

  const cx = 120
  const cy = 120
  const R = 80
  const n = axes.length

  const point = (i, val, max) => {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2
    const r = (val / max) * R
    return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)]
  }

  const values = axes.map((a) => Math.min(dna[a.key] ?? 0, a.max))
  const poly = values
    .map((v, i) => {
      const [x, y] = point(i, v, axes[i].max)
      return `${x},${y}`
    })
    .join(' ')

  return (
    <svg viewBox="0 0 240 260" className="mx-auto w-full max-w-xs">
      {[0.25, 0.5, 0.75, 1].map((s) => (
        <polygon
          key={s}
          points={axes
            .map((_, i) => {
              const [x, y] = point(i, axes[i].max * s, axes[i].max)
              return `${x},${y}`
            })
            .join(' ')}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="1"
        />
      ))}
      {axes.map((a, i) => {
        const [x, y] = point(i, a.max, a.max)
        const [lx, ly] = point(i, a.max * 1.15, a.max)
        return (
          <g key={a.key}>
            <line x1={cx} y1={cy} x2={x} y2={y} stroke="#cbd5e1" strokeWidth="1" />
            <text x={lx} y={ly} textAnchor="middle" dominantBaseline="middle" className="fill-slate-500 text-[9px]">
              {a.label}
            </text>
          </g>
        )
      })}
      <polygon points={poly} fill="rgba(99,102,241,0.35)" stroke="#6366f1" strokeWidth="2" />
    </svg>
  )
}
