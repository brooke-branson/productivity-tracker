import { taskDay, toDateKey } from '../constants'

function dayLabel(date) {
  return date.toLocaleDateString(undefined, { weekday: 'short' })
}

function dateLabel(date) {
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export default function TrendChart({ tasks, days, label, showAverage = false }) {
  const buckets = days.map((date) => ({
    key: toDateKey(date),
    date,
    minutes: 0,
    focusTotal: 0,
    focusCount: 0,
    completed: 0,
    completedFocusTotal: 0,
    completedFocusCount: 0,
  }))
  const byKey = new Map(buckets.map((day) => [day.key, day]))

  tasks.forEach((task) => {
    const when = taskDay(task)
    if (!when) return
    const bucket = byKey.get(toDateKey(when))
    if (!bucket) return
    bucket.minutes += task.time_spent_minutes || 0
    if (task.focus_level != null) {
      bucket.focusTotal += task.focus_level
      bucket.focusCount += 1
    }
    if (task.status === 'completed') {
      bucket.completed += 1
      if (task.focus_level != null) {
        bucket.completedFocusTotal += task.focus_level
        bucket.completedFocusCount += 1
      }
    }
  })

  // A date only stays on the chart when at least one task was completed that day.
  const plotted = buckets.filter((day) => day.completed > 0)
  const completedFocusCount = plotted.reduce((sum, day) => sum + day.completedFocusCount, 0)
  const averageFocus = completedFocusCount
    ? plotted.reduce((sum, day) => sum + day.completedFocusTotal, 0) / completedFocusCount
    : null
  const maxMinutes = Math.max(...plotted.map((day) => day.minutes), 1)
  const columnCount = plotted.length + (showAverage && averageFocus != null ? 1 : 0)
  const wide = columnCount > 7

  return (
    <section className="panel chart-panel" aria-labelledby="trend-heading">
      <div className="panel-head">
        <div>
          <p className="eyebrow">{label}</p>
          <h2 id="trend-heading">Time logged</h2>
        </div>
        <p className="panel-note">Follows the dates selected on the task list.</p>
      </div>

      {days.length === 0 ? (
        <p className="empty-note">Choose a week, a date range, or a weekday to plot.</p>
      ) : plotted.length === 0 ? (
        <p className="empty-note">No completed tasks in this view.</p>
      ) : (
        <div className={`chart-scroll ${wide ? 'is-scroll' : ''}`}>
          <div
            className="chart"
            style={{ '--cols': columnCount }}
            role="img"
            aria-label={`Minutes logged for ${label}`}
          >
            {plotted.map((day) => {
              const height = Math.max((day.minutes / maxMinutes) * 100, day.minutes ? 8 : 0)
              const average = day.focusCount ? Math.round(day.focusTotal / day.focusCount) : 0
              return (
                <div className="chart-col" key={day.key}>
                  <div className="chart-bar-wrap">
                    <div
                      className={`chart-bar focus-${average || 'none'}`}
                      style={{ height: `${height}%` }}
                      title={`${dateLabel(day.date)}: ${day.minutes} min, ${day.completed} completed`}
                    />
                  </div>
                  <span className="chart-day">{dayLabel(day.date)}</span>
                  <span className="chart-date">{day.date.getDate()}</span>
                </div>
              )
            })}
            {showAverage && averageFocus != null && (
              <div className="chart-col">
                <div className="chart-bar-wrap">
                  <div
                    className={`chart-bar is-average focus-${Math.round(averageFocus)}`}
                    style={{ height: `${(averageFocus / 5) * 100}%` }}
                    title={`Average focus ${averageFocus.toFixed(1)} of 5`}
                  />
                </div>
                <span className="chart-day">Avg</span>
                <span className="chart-date">{averageFocus.toFixed(1)}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
