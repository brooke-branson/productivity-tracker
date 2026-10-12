import { useEffect, useState } from 'react'
import { CATEGORIES, FOCUS_LEVELS, STATUSES, WEEKDAYS, focusLabel, formatMinutes, formatWhen, toDateKey, toDateTimeInput, weekDays } from '../constants'

function taskToForm(task) {
  return {
    name: task.name,
    category: task.category,
    status: task.status,
    timeSpent: task.time_spent_minutes ?? '',
    focus: task.focus_level == null ? '' : String(task.focus_level),
    startedAt: toDateTimeInput(task.started_at),
  }
}

function formToPatch(form) {
  return {
    name: form.name.trim(),
    category: form.category,
    status: form.status,
    time_spent_minutes: form.timeSpent === '' ? null : Number(form.timeSpent),
    focus_level: form.focus === '' ? null : Number(form.focus),
    started_at: form.startedAt ? form.startedAt : null,
  }
}

const PAGE_SIZE = 5

export default function TaskBoard({ tasks, dateFilter, onDateFilter, onSave, onDelete, onOpen }) {
  const [filter, setFilter] = useState('all')
  const [page, setPage] = useState(0)
  const [editingId, setEditingId] = useState(null)
  const [draft, setDraft] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const visible = filter === 'all' ? tasks : tasks.filter((task) => task.status === filter)
  const pageCount = Math.max(1, Math.ceil(visible.length / PAGE_SIZE))
  const currentPage = Math.min(page, pageCount - 1)
  const pageTasks = visible.slice(currentPage * PAGE_SIZE, currentPage * PAGE_SIZE + PAGE_SIZE)

  useEffect(() => {
    // Close the editor when the open task is no longer in the selected week.
    if (editingId != null && !tasks.some((task) => task.id === editingId)) {
      setEditingId(null)
      setDraft(null)
    }
  }, [tasks, editingId])

  useEffect(() => {
    // A new date or status view starts on the first page.
    setPage(0)
  }, [filter, dateFilter])

  useEffect(() => {
    setPage((current) => Math.min(current, Math.max(0, pageCount - 1)))
  }, [pageCount])

  async function openEditor(task) {
    setError('')
    setEditingId(task.id)
    setDraft(taskToForm(task))
    try {
      // Reload the single task so the GET /tasks/{id} endpoint stays exercised.
      const fresh = await onOpen(task.id)
      setDraft(taskToForm(fresh))
    } catch (err) {
      setError(err.message)
    }
  }

  function update(field, value) {
    setDraft((current) => ({ ...current, [field]: value }))
  }

  async function save(event) {
    event.preventDefault()
    if (!draft || draft.name.trim().length < 3) {
      setError('Task name needs at least 3 characters.')
      return
    }
    if (draft.status === 'completed') {
      const time = draft.timeSpent === '' ? null : Number(draft.timeSpent)
      if (time == null || time <= 0 || draft.focus === '') {
        setError('Completing a task needs time spent above 0 and a focus level.')
        return
      }
    }

    setBusy(true)
    setError('')
    try {
      await onSave(editingId, formToPatch(draft))
      setEditingId(null)
      setDraft(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function remove(id) {
    setBusy(true)
    setError('')
    try {
      await onDelete(id)
      if (editingId === id) {
        setEditingId(null)
        setDraft(null)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel task-board">
      <div className="panel-head">
        <div>
          <p className="eyebrow">Tasks</p>
          <h2>{visible.length} shown</h2>
        </div>
        <div className="filters" role="tablist" aria-label="Filter by status">
          {['all', ...STATUSES].map((status) => (
            <button
              key={status}
              type="button"
              className={filter === status ? 'is-on' : ''}
              onClick={() => setFilter(status)}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      <DateFilter dateFilter={dateFilter} onDateFilter={onDateFilter} />

      {error && <p className="form-error">{error}</p>}

      {visible.length === 0 ? (
        <p className="empty-note">No tasks in this view yet.</p>
      ) : (
        <ul className="task-list">
          {pageTasks.map((task) => {
            const editing = editingId === task.id
            return (
              <li
                key={task.id}
                className={`task-card cat-${task.category} ${editing ? 'is-editing' : ''}`}
                style={{ '--edge': `var(--focus-${task.focus_level || 'none'})` }}
              >
                <div className="task-main">
                  <div>
                    <p className="task-name">{task.name}</p>
                    <p className="task-meta">
                      <span className={`chip cat-${task.category}`}>{task.category}</span>
                      <span className={`chip status-${task.status}`}>{task.status}</span>
                      <span>{formatMinutes(task.time_spent_minutes)}</span>
                      <span className={`focus-dot focus-${task.focus_level || 'none'}`}>
                        {focusLabel(task.focus_level)}
                      </span>
                    </p>
                  </div>
                  <div className="task-actions">
                    <button type="button" onClick={() => (editing ? setEditingId(null) : openEditor(task))}>
                      {editing ? 'Close' : 'Edit'}
                    </button>
                    <button type="button" className="danger" onClick={() => remove(task.id)} disabled={busy}>
                      Delete
                    </button>
                  </div>
                </div>
                <p className="task-dates">
                  Created {formatWhen(task.created_at)}
                  {task.started_at ? ` · Started ${formatWhen(task.started_at)}` : ''}
                  {task.completed_at ? ` · Done ${formatWhen(task.completed_at)}` : ''}
                </p>

                {editing && draft && (
                  <form className="edit-form" onSubmit={save}>
                    <label>
                      Name
                      <input value={draft.name} onChange={(event) => update('name', event.target.value)} maxLength={255} />
                    </label>
                    <div className="field-row">
                      <label>
                        Category
                        <select value={draft.category} onChange={(event) => update('category', event.target.value)}>
                          {CATEGORIES.map((category) => (
                            <option key={category} value={category}>
                              {category}
                            </option>
                          ))}
                        </select>
                      </label>
                      <label>
                        Status
                        <select value={draft.status} onChange={(event) => update('status', event.target.value)}>
                          {STATUSES.map((status) => (
                            <option key={status} value={status}>
                              {status}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                    <div className="field-row">
                      <label>
                        Minutes
                        <input
                          type="number"
                          min="0"
                          value={draft.timeSpent}
                          onChange={(event) => update('timeSpent', event.target.value)}
                        />
                      </label>
                      <label>
                        Focus
                        <select value={draft.focus} onChange={(event) => update('focus', event.target.value)}>
                          <option value="">Unset</option>
                          {FOCUS_LEVELS.map((level) => (
                            <option key={level.value} value={level.value}>
                              {level.value} · {level.label}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                    <label>
                      Started at
                      <input
                        type="datetime-local"
                        value={draft.startedAt}
                        onChange={(event) => update('startedAt', event.target.value)}
                      />
                    </label>
                    <button className="primary" type="submit" disabled={busy}>
                      {busy ? 'Saving…' : 'Save changes'}
                    </button>
                  </form>
                )}
              </li>
            )
          })}
        </ul>
      )}

      {visible.length > PAGE_SIZE && (
        <div className="pager">
          <button type="button" onClick={() => setPage(currentPage - 1)} disabled={currentPage === 0}>
            Previous
          </button>
          <span>
            {currentPage + 1} / {pageCount}
          </span>
          <button type="button" onClick={() => setPage(currentPage + 1)} disabled={currentPage >= pageCount - 1}>
            Next
          </button>
        </div>
      )}
    </section>
  )
}

function DateFilter({ dateFilter, onDateFilter }) {
  const { mode, weekOffset, start, end, weekday } = dateFilter
  const week = weekDays(weekOffset)
  const weekText = `${week[0].toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} – ${week[6].toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}`

  function chooseMode(nextMode) {
    onDateFilter((current) => {
      if (nextMode === 'range' && !current.start && !current.end) {
        const days = weekDays(current.weekOffset)
        return { ...current, mode: nextMode, start: toDateKey(days[0]), end: toDateKey(days[6]) }
      }
      return { ...current, mode: nextMode }
    })
  }

  return (
    <div className="date-filter">
      <div className="filters" role="tablist" aria-label="How to choose dates">
        {[
          ['week', 'Week'],
          ['range', 'Dates'],
          ['weekday', 'Weekday'],
        ].map(([value, label]) => (
          <button key={value} type="button" className={mode === value ? 'is-on' : ''} onClick={() => chooseMode(value)}>
            {label}
          </button>
        ))}
      </div>

      {mode === 'week' && (
        <div className="week-nav">
          <button type="button" className="week-arrow" aria-label="Previous week" onClick={() => onDateFilter((current) => ({ ...current, weekOffset: current.weekOffset - 1 }))}>
            ←
          </button>
          <button
            type="button"
            className="week-arrow"
            aria-label="Next week"
            disabled={weekOffset >= 0}
            onClick={() => onDateFilter((current) => ({ ...current, weekOffset: Math.min(current.weekOffset + 1, 0) }))}
          >
            →
          </button>
          <span className="week-range">{weekText}</span>
          <button type="button" disabled={weekOffset === 0} onClick={() => onDateFilter((current) => ({ ...current, weekOffset: 0 }))}>
            This week
          </button>
        </div>
      )}

      {mode === 'range' && (
        <div className="date-inputs">
          <label>
            Start
            <input type="date" value={start} onChange={(event) => onDateFilter((current) => ({ ...current, start: event.target.value }))} />
          </label>
          <label>
            End
            <input type="date" value={end} onChange={(event) => onDateFilter((current) => ({ ...current, end: event.target.value }))} />
          </label>
        </div>
      )}

      {mode === 'weekday' && (
        <div className="filters" role="group" aria-label="Day of week">
          {WEEKDAYS.map((day) => (
            <button
              key={day.value}
              type="button"
              className={weekday === day.value ? 'is-on' : ''}
              aria-pressed={weekday === day.value}
              onClick={() => onDateFilter((current) => ({ ...current, weekday: day.value }))}
            >
              {day.short}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
