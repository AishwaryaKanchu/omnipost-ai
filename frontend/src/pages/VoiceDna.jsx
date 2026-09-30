import RadarChart from '../components/RadarChart'

export default function VoiceDna({ result }) {
  const dna = result?.voice_dna

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Voice DNA</h2>
        <p className="mt-2 text-sm text-slate-600">
          Computed locally from 3–5 sample posts: sentence length, emoji & hashtag habits, punctuation, and CTA
          style. Generated posts are scored against this fingerprint.
        </p>
        {dna && (
          <dl className="mt-4 grid grid-cols-2 gap-2 text-sm">
            <div>
              <dt className="text-slate-500">Avg sentence length</dt>
              <dd className="font-medium">{dna.avg_sentence_length} words</dd>
            </div>
            <div>
              <dt className="text-slate-500">Emoji / post</dt>
              <dd className="font-medium">{dna.emoji_rate}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Hashtags / post</dt>
              <dd className="font-medium">{dna.hashtag_rate}</dd>
            </div>
            <div>
              <dt className="text-slate-500">CTA style</dt>
              <dd className="font-medium capitalize">{dna.cta_style}</dd>
            </div>
          </dl>
        )}
      </section>
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-center text-sm font-medium text-slate-600">Voice fingerprint</h3>
        <RadarChart dna={dna} />
      </section>
    </div>
  )
}
