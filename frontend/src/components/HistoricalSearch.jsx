import { useEffect, useRef, useState } from 'react'
import { searchHistory } from '../api'

export default function HistoricalSearch() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')
  const inputRef = useRef(null)
  const rootRef = useRef(null)

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  // A click on the page, outside this control, dismisses the open panel.
  useEffect(() => {
    if (!open) return

    function handlePointerDown(event) {
      if (!rootRef.current?.contains(event.target)) {
        setOpen(false)
      }
    }

    document.addEventListener('pointerdown', handlePointerDown)
    return () => document.removeEventListener('pointerdown', handlePointerDown)
  }, [open])

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) return

    setStatus('searching')
    setError('')
    try {
      const answer = await searchHistory(trimmed)
      setResult(answer)
      setStatus('ready')
    } catch (err) {
      setStatus('error')
      setError(err.message)
    }
  }

  const matched = Array.isArray(result?.matched_summary_ids) ? result.matched_summary_ids : []

  return (
    <div className="ai-search" ref={rootRef}>
      <div className="ai-search-bar">
        <span>AI assisted search</span>
        <button
          type="button"
          className="ai-search-icon"
          aria-expanded={open}
          aria-controls="ai-search-panel"
          aria-label="AI assisted search"
          onClick={() => setOpen((value) => !value)}
        >
          <svg viewBox="0 0 16 16" aria-hidden="true">
            <circle cx="7" cy="7" r="4.25" fill="none" stroke="currentColor" strokeWidth="1.6" />
            <path d="M10.2 10.2 13.5 13.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
        </button>
      </div>

      {open && (
        <form id="ai-search-panel" className="ai-search-panel" onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Which weeks had the most deep work?"
            aria-label="Question"
          />
          <button className="primary" type="submit" disabled={status === 'searching' || !query.trim()}>
            {status === 'searching' ? 'Searching…' : 'Search'}
          </button>

          {error && <p className="form-error">{error}</p>}

          {result && status === 'ready' && (
            <div className="ai-search-answer">
              <p>{result.answer}</p>
              {matched.length > 0 && (
                <p className="history-matches">Matched summaries: {matched.join(', ')}</p>
              )}
            </div>
          )}
        </form>
      )}
    </div>
  )
}
