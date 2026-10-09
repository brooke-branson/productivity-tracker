import { useState } from 'react'
import { CATEGORIES, FOCUS_LEVELS, STATUSES } from '../constants'

const EMPTY = {
  name: '',
  category: 'uncategorized',
  status: 'planned',
  timeSpent: '',
  focus: '',
}

export default function TaskForm({ onCreate, busy }) {
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    const name = form.name.trim()
    if (name.length < 3) {
      setError('Task name needs at least 3 characters.')
      return
    }

    const time = form.timeSpent === '' ? null : Number(form.timeSpent)
    const focus = form.focus === '' ? null : Number(form.focus)

    // The API rejects a completed task that is missing time or focus.
    if (form.status === 'completed' && (time == null || time <= 0 || focus == null)) {
      setError('Completing a task needs time spent above 0 and a focus level.')
      return
    }

    const edits = {}
    if (form.category !== 'uncategorized') edits.category = form.category
    if (form.status !== 'planned') edits.status = form.status
    if (time != null) edits.time_spent_minutes = time
    if (focus != null) edits.focus_level = focus

    try {
      await onCreate(name, edits)
      setForm(EMPTY)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form className="panel task-form" onSubmit={handleSubmit}>
      <div className="panel-head">
        <div>
          <p className="eyebrow">Log work</p>
          <h2>New task</h2>
        </div>
      </div>

      <label>
        Task name
        <input
          value={form.name}
          onChange={(event) => update('name', event.target.value)}
          placeholder="Wrote code"
          maxLength={255}
          required
        />
      </label>

      <div className="field-row">
        <label>
          Category
          <select value={form.category} onChange={(event) => update('category', event.target.value)}>
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select value={form.status} onChange={(event) => update('status', event.target.value)}>
            {STATUSES.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label>
        Time spent (minutes)
        <input
          type="number"
          min="0"
          value={form.timeSpent}
          onChange={(event) => update('timeSpent', event.target.value)}
          placeholder="90"
        />
      </label>

      <fieldset>
        <legend>Focus level</legend>
        <div className="focus-picks">
          {FOCUS_LEVELS.map((level) => (
            <button
              key={level.value}
              type="button"
              className={`focus-pick focus-${level.value} ${form.focus === String(level.value) ? 'is-on' : ''}`}
              onClick={() => update('focus', form.focus === String(level.value) ? '' : String(level.value))}
              aria-pressed={form.focus === String(level.value)}
            >
              {level.value}
              <span>{level.label}</span>
            </button>
          ))}
        </div>
      </fieldset>

      {error && <p className="form-error">{error}</p>}

      <button className="primary" type="submit" disabled={busy}>
        {busy ? 'Saving…' : 'Add task'}
      </button>
    </form>
  )
}
