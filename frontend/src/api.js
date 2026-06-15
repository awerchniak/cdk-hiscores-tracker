const API_BASE = import.meta.env.VITE_API_URL

if (!API_BASE) {
  console.error('VITE_API_URL is not set. Create frontend/.env.local with your API Gateway URL.')
}

function formatTime(dateStr, granularity) {
  if (!dateStr) return dateStr
  switch (granularity) {
    case 'monthly': return dateStr.slice(0, 7)       // YYYY-MM
    case 'raw':     return `${dateStr} 00:00:00`     // YYYY-MM-DD HH:MM:SS
    default:        return dateStr                    // YYYY-MM-DD (daily / auto)
  }
}

export async function fetchHiScores(player, startDate, endDate, granularity) {
  if (!API_BASE) throw new Error('API URL not configured. Set VITE_API_URL in frontend/.env.local')

  const params = new URLSearchParams({
    player,
    startTime: formatTime(startDate, granularity),
    endTime:   formatTime(endDate,   granularity),
  })

  const res = await fetch(`${API_BASE}/v0?${params}`)
  const json = await res.json()

  if (!res.ok) {
    throw new Error(json?.message || json?.body || `HTTP ${res.status}`)
  }

  return json
}
