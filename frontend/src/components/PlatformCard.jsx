const META = {
  instagram: { name: 'Instagram', color: 'from-pink-500 to-purple-600', icon: '📸' },
  linkedin: { name: 'LinkedIn', color: 'from-blue-600 to-blue-800', icon: '💼' },
  x: { name: 'X', color: 'from-slate-800 to-black', icon: '𝕏' },
}

export default function PlatformCard({
  platform,
  content,
  angle,
  voiceScore,
  voiceRewrite,
  factGuard,
  approved,
  onEdit,
  onCopy,
  onApprove,
  editing,
  editValue,
  onEditChange,
  onSaveEdit,
  onCancelEdit,
  learnMessage,
}) {
  const m = META[platform] || META.x
  const fg = factGuard?.[platform]

  return (
    <article className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className={`bg-gradient-to-r ${m.color} px-4 py-3 text-white`}>
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold">
            {m.icon} {m.name}
          </span>
          {approved && (
            <span className="rounded-full bg-white/20 px-2 py-0.5 text-xs font-medium">Approved ✓</span>
          )}
        </div>
        {angle && <p className="mt-1 text-xs text-white/90">Angle: {angle}</p>}
      </div>

      <div className="space-y-3 p-4">
        {editing ? (
          <textarea
            className="min-h-[140px] w-full rounded-lg border border-slate-300 p-3 text-sm"
            value={editValue}
            onChange={(e) => onEditChange(e.target.value)}
          />
        ) : (
          <div className="whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-sm leading-relaxed">{content}</div>
        )}

        <div className="flex flex-wrap gap-2 text-xs">
          <span className="rounded-full bg-indigo-50 px-2 py-1 font-medium text-indigo-700">
            Voice Match: {voiceScore ?? '—'}
          </span>
          {voiceRewrite && (
            <span className="rounded-full bg-amber-50 px-2 py-1 text-amber-800">{voiceRewrite.message}</span>
          )}
          {fg && (
            <span
              className={`rounded-full px-2 py-1 ${
                fg.status === 'grounded' ? 'bg-emerald-50 text-emerald-800' : 'bg-red-50 text-red-800'
              }`}
            >
              {fg.label}
              {fg.unsupported_claims?.length > 0 && `: ${fg.unsupported_claims.join(', ')}`}
            </span>
          )}
        </div>

        {learnMessage && <p className="text-sm text-emerald-600">{learnMessage}</p>}

        <div className="flex flex-wrap gap-2 pt-1">
          {editing ? (
            <>
              <button type="button" onClick={onSaveEdit} className="btn-primary text-sm">
                Save edit
              </button>
              <button type="button" onClick={onCancelEdit} className="btn-secondary text-sm">
                Cancel
              </button>
            </>
          ) : (
            <>
              <button type="button" onClick={onEdit} className="btn-secondary text-sm">
                Edit
              </button>
              <button type="button" onClick={onCopy} className="btn-secondary text-sm">
                Copy
              </button>
              <button type="button" onClick={onApprove} className="btn-primary text-sm">
                Approve
              </button>
            </>
          )}
        </div>
      </div>
    </article>
  )
}
