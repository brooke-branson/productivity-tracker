export const CATEGORIES = [
  'uncategorized',
  'work',
  'learning',
  'personal',
  'fitness',
  'other',
]

export const STATUSES = ['planned', 'in-progress', 'completed']

export const FOCUS_LEVELS = [
  { value: 1, label: 'Very low' },
  { value: 2, label: 'Low' },
  { value: 3, label: 'Medium' },
  { value: 4, label: 'High' },
  { value: 5, label: 'Very high' },
]

export function focusLabel(level) {
  return FOCUS_LEVELS.find((item) => item.value === level)?.label ?? 'Unset'
}

// SQLite often returns "YYYY-MM-DD HH:MM:SS". Normalize before parsing.
export function parseApiDate(value) {
  if (!value) return null
  const normalized = typeof value === 'string' ? value.replace(' ', 'T') : value
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

export const WEEKDAYS = [
  { value: 0, short: 'Sun', label: 'Sundays' },
  { value: 1, short: 'Mon', label: 'Mondays' },
  { value: 2, short: 'Tue', label: 'Tuesdays' },
  { value: 3, short: 'Wed', label: 'Wednesdays' },
  { value: 4, short: 'Thu', label: 'Thursdays' },
  { value: 5, short: 'Fri', label: 'Fridays' },
  { value: 6, short: 'Sat', label: 'Saturdays' },
]

export const WEEK_LENGTH = 7

export function startOfWeek(date) {
  const start = new Date(date)
  start.setHours(0, 0, 0, 0)
  start.setDate(start.getDate() - start.getDay())
  return start
}

// Sunday–Saturday dates for the current week, or earlier when weekOffset is negative.
export function weekDays(weekOffset) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const start = startOfWeek(today)
  start.setDate(start.getDate() + weekOffset * WEEK_LENGTH)
  return Array.from({ length: WEEK_LENGTH }, (_, index) => {
    const date = new Date(start)
    date.setDate(start.getDate() + index)
    return date
  })
}

// Same day the chart uses: finished, then started, then logged.
export function taskDay(task) {
  return parseApiDate(task.completed_at) || parseApiDate(task.started_at) || parseApiDate(task.created_at)
}

// Date inputs are local calendar days. Parsing them as UTC shifts the day.
export function parseDateInput(value) {
  if (!value) return null
  const [year, month, day] = value.split('-').map(Number)
  if (!year || !month || !day) return null
  return new Date(year, month - 1, day)
}

export function eachDay(start, end) {
  const first = new Date(start)
  const last = new Date(end)
  first.setHours(0, 0, 0, 0)
  last.setHours(0, 0, 0, 0)
  const [from, to] = first <= last ? [first, last] : [last, first]
  const days = []
  const cursor = new Date(from)
  while (cursor <= to && days.length < 120) {
    days.push(new Date(cursor))
    cursor.setDate(cursor.getDate() + 1)
  }
  return days
}

export function toDateKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function toDateTimeInput(value) {
  const date = parseApiDate(value)
  if (!date) return ''
  const pad = (part) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function formatWhen(value) {
  const date = parseApiDate(value)
  if (!date) return '—'
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function formatMinutes(minutes) {
  if (minutes == null) return '—'
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  if (hours === 0) return `${rest}m`
  if (rest === 0) return `${hours}h`
  return `${hours}h ${rest}m`
}
