// Thin client for the task API. Paths are relative so Vite can proxy them
// to the FastAPI server on port 8000.

async function readError(response) {
  const text = await response.text()
  if (!text) return response.statusText || 'Request failed'

  try {
    const body = JSON.parse(text)
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail.map((item) => item.msg || JSON.stringify(item)).join(' ')
    }
    return text
  } catch {
    return text
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(path, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
  } catch {
    throw new Error('Cannot reach the API. Start the backend on port 8000.')
  }

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  if (response.status === 204) return null
  return response.json()
}

export function checkHealth() {
  return request('/healthz')
}

export function listTasks() {
  return request('/tasks')
}

export function getTask(id) {
  return request(`/tasks/${id}`)
}

// Create only accepts a name. Extra fields are applied with a follow-up patch.
export function createTask(name) {
  return request('/tasks', {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

export function updateTask(id, edits) {
  return request(`/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(edits),
  })
}

export function deleteTask(id) {
  return request(`/tasks/${id}`, { method: 'DELETE' })
}

// A missing week is an empty card, not a failed page.
export async function getWeeklySummary(weekStart) {
  try {
    return await request(`/weekly-summary/${weekStart}`)
  } catch (err) {
    if (err.message === 'Weekly summary not found') return null
    throw err
  }
}

export function generateWeeklySummary(weekStart) {
  return request(`/weekly-summary/${weekStart}`, { method: 'POST' })
}

// The agent searches saved weekly summaries and answers from those weeks only.
export function searchHistory(query) {
  const params = new URLSearchParams({ query })
  return request(`/historical-search?${params}`)
}
