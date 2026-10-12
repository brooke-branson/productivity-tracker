import { useEffect, useState } from 'react'
import { generateWeeklySummary, getWeeklySummary } from '../api'
import { formatMinutes } from '../constants'

function focusText(value) {
  return value == null ? '—' : Number(value).toFixed(1)
}

export default function WeeklySummary({ weekStart, label }) {
  const [summary, setSummary] = useState(null)
  const [status, setStatus] = useState(weekStart ? 'loading' : 'idle')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!weekStart) {
      setSummary(null)
      setStatus('idle')
      setError('')
      return
    }

    let cancelled = false
    setStatus('loading')
    setError('')

    // Saved summaries are fetched. Generating is a separate action because it calls Gemini.
    getWeeklySummary(weekStart)
      .then((result) => {
        if (cancelled) return
        setSummary(result)
        setStatus(result ? 'ready' : 'empty')
      })
      .catch((err) => {
        if (cancelled) return
        setSummary(null)
        setError(err.message)
        setStatus('error')
      })

    return () => {
      cancelled = true
    }
  }, [weekStart])

  async function handleGenerate() {
    setStatus('generating')
    setError('')
    try {
      const created = await generateWeeklySummary(weekStart)
      setSummary(created)
      setStatus('ready')
    } catch (err) {
      setStatus(summary ? 'ready' : 'empty')
      setError(err.message)
    }
  }

  const suggestions = Array.isArray(summary?.weekly_summary_suggestions)
    ? summary.weekly_summary_suggestions
    : []

  return (
    <section className="panel weekly-summary" aria-labelledby="summary-heading">
      <div className="panel-head">
        <div>
          <p className="eyebrow">{label || 'Week'}</p>
          <h2 id="summary-heading">Weekly summary</h2>
        </div>
        {weekStart && !summary && status !== 'loading' && (
          <button type="button" onClick={handleGenerate} disabled={status === 'generating'}>
            {status === 'generating' ? 'Writing…' : 'Generate'}
          </button>
        )}
      </div>

      {!weekStart && <p className="empty-note">Choose a week to see its summary.</p>}
      {weekStart && status === 'loading' && <p className="empty-note">Looking up this week…</p>}
      {error && <p className="form-error">{error}</p>}

      {summary && status !== 'loading' && (
        <>
          <p className="summary-metrics">
            {summary.total_tasks_completed} completed · {formatMinutes(summary.total_time_spent_minutes)} · focus{' '}
            {focusText(summary.average_focus_level)}
          </p>
          <p className="summary-notes">{summary.weekly_summary_notes || 'No written summary yet.'}</p>
          {suggestions.length > 0 && (
            <>
              <h3 className="summary-suggestions-heading">Suggestions:</h3>
              <ul className="summary-list">
                {suggestions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          )}
        </>
      )}

      {weekStart && status === 'empty' && !error && (
        <p className="empty-note">No summary for this week yet.</p>
      )}
    </section>
  )
}
