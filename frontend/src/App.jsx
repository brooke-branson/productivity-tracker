import { useCallback, useEffect, useMemo, useState } from 'react'
import { checkHealth, createTask, deleteTask, getTask, listTasks, updateTask } from './api'
import TaskBoard from './components/TaskBoard'
import TaskForm from './components/TaskForm'
import TrendChart from './components/TrendChart'
import WeeklySummary from './components/WeeklySummary'
import { WEEKDAYS, eachDay, formatMinutes, parseDateInput, taskDay, toDateKey, weekDays } from './constants'
import './App.css'

function rangeLabel(days) {
  if (!days.length) return 'No dates selected'
  const start = days[0].toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  if (days.length === 1) return start
  const end = days[days.length - 1]
  const endText = end.toLocaleDateString(
    undefined,
    end.getMonth() === days[0].getMonth() ? { day: 'numeric' } : { month: 'short', day: 'numeric' },
  )
  return `${start} – ${endText}`
}

function tasksOnDays(tasks, days) {
  const keys = new Set(days.map(toDateKey))
  return tasks.filter((task) => {
    const when = taskDay(task)
    return when && keys.has(toDateKey(when))
  })
}

// The task-list date controls decide which days the chart and list share.
function selectByDate(tasks, filter) {
  if (filter.mode === 'range') {
    const start = parseDateInput(filter.start)
    const end = parseDateInput(filter.end)
    const days = start || end ? eachDay(start || end, end || start) : []
    return { chartDays: days, chartLabel: rangeLabel(days), dateTasks: tasksOnDays(tasks, days) }
  }

  if (filter.mode === 'weekday') {
    const name = WEEKDAYS.find((day) => day.value === filter.weekday)?.label ?? 'Weekday'
    if (filter.weekday == null) {
      return { chartDays: [], chartLabel: 'Pick a weekday', dateTasks: [] }
    }
    const dated = tasks.map(taskDay).filter(Boolean)
    if (!dated.length) {
      return { chartDays: [], chartLabel: name, dateTasks: [] }
    }
    const first = new Date(Math.min(...dated.map((day) => day.getTime())))
    const last = new Date(Math.max(...dated.map((day) => day.getTime())))
    first.setHours(0, 0, 0, 0)
    last.setHours(0, 0, 0, 0)
    while (first.getDay() !== filter.weekday) first.setDate(first.getDate() + 1)
    const days = []
    for (let cursor = new Date(first); cursor <= last && days.length < 52; cursor.setDate(cursor.getDate() + 7)) {
      days.push(new Date(cursor))
    }
    const matched = tasks.filter((task) => taskDay(task)?.getDay() === filter.weekday)
    return { chartDays: days, chartLabel: name, dateTasks: matched }
  }

  const days = weekDays(filter.weekOffset)
  return {
    chartDays: days,
    chartLabel: filter.weekOffset === 0 ? 'This week' : rangeLabel(days),
    dateTasks: tasksOnDays(tasks, days),
  }
}

function averageFocus(tasks) {
  const scored = tasks.filter((task) => task.focus_level != null)
  if (!scored.length) return '—'
  const total = scored.reduce((sum, task) => sum + task.focus_level, 0)
  return (total / scored.length).toFixed(1)
}

export default function App() {
  const [tasks, setTasks] = useState([])
  const [health, setHealth] = useState('checking')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [dateFilter, setDateFilter] = useState({
    mode: 'week',
    weekOffset: 0,
    start: '',
    end: '',
    weekday: null,
  })

  const refresh = useCallback(async () => {
    const [healthResult, taskResult] = await Promise.allSettled([checkHealth(), listTasks()])

    if (healthResult.status === 'fulfilled' && healthResult.value?.status === 'ok') {
      setHealth('ok')
    } else {
      setHealth('down')
    }

    if (taskResult.status === 'fulfilled') {
      setTasks(taskResult.value)
      setError('')
    } else {
      setError(taskResult.reason.message)
    }
  }, [])

  useEffect(() => {
    // Reload from the API on mount so a refresh keeps the tasks the backend stored.
    refresh()
  }, [refresh])

  async function handleCreate(name, edits) {
    setSaving(true)
    setError('')
    try {
      const created = await createTask(name)
      if (Object.keys(edits).length) {
        await updateTask(created.id, edits)
      }
      await refresh()
    } catch (err) {
      await refresh()
      throw err
    } finally {
      setSaving(false)
    }
  }

  async function handleSave(id, edits) {
    await updateTask(id, edits)
    await refresh()
  }

  async function handleDelete(id) {
    await deleteTask(id)
    await refresh()
  }

  const { chartDays, chartLabel, dateTasks } = useMemo(
    () => selectByDate(tasks, dateFilter),
    [tasks, dateFilter],
  )

  const minutes = tasks.reduce((sum, task) => sum + (task.time_spent_minutes || 0), 0)
  const completed = tasks.filter((task) => task.status === 'completed').length

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <p className="eyebrow">Daily log</p>
          <h1>Productivity tracker</h1>
        </div>
        <p className={`health health-${health}`}>
          API {health === 'ok' ? 'connected' : health === 'down' ? 'offline' : 'checking'}
        </p>
      </header>

      {error && <p className="banner">{error}</p>}

      <section className="stats" aria-label="Summary">
        <article>
          <span>Tasks</span>
          <strong>{tasks.length}</strong>
        </article>
        <article>
          <span>Completed</span>
          <strong>{completed}</strong>
        </article>
        <article>
          <span>Time logged</span>
          <strong>{formatMinutes(minutes)}</strong>
        </article>
        <article>
          <span>Avg focus</span>
          <strong>{averageFocus(tasks)}</strong>
        </article>
      </section>

      <TrendChart
        tasks={dateTasks}
        days={chartDays}
        label={chartLabel}
        showAverage={dateFilter.mode === 'weekday'}
      />

      <WeeklySummary
        weekStart={dateFilter.mode === 'week' && chartDays[0] ? toDateKey(chartDays[0]) : null}
        label={dateFilter.mode === 'week' ? chartLabel : 'Week'}
      />

      <div className="workspace">
        <TaskForm onCreate={handleCreate} busy={saving} />
        <TaskBoard
          tasks={dateTasks}
          dateFilter={dateFilter}
          onDateFilter={setDateFilter}
          onSave={handleSave}
          onDelete={handleDelete}
          onOpen={getTask}
        />
      </div>
    </div>
  )
}
