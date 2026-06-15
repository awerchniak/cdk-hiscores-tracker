// In dev, VITE_API_URL is read from .env.local.
// In production the build has no API URL baked in, so we fetch config.json
// (written to the S3 bucket by CDK at deploy time) to discover it at runtime.
const _basePromise = import.meta.env.VITE_API_URL
  ? Promise.resolve(import.meta.env.VITE_API_URL)
  : fetch('/config.json').then(r => r.json()).then(c => c.apiUrl)

function formatTime(dateStr, granularity) {
  if (!dateStr) return dateStr
  switch (granularity) {
    case 'monthly': return dateStr.slice(0, 7)       // YYYY-MM
    case 'raw':     return `${dateStr} 00:00:00`     // YYYY-MM-DD HH:MM:SS
    default:        return dateStr                    // YYYY-MM-DD (daily / auto)
  }
}

export async function fetchHiScores(player, startDate, endDate, granularity) {
  const apiBase = await _basePromise

  const params = new URLSearchParams({
    player,
    startTime: formatTime(startDate, granularity),
    endTime:   formatTime(endDate,   granularity),
  })

  const res = await fetch(`${apiBase}/v0?${params}`)
  const json = await res.json()

  if (!res.ok) {
    throw new Error(json?.message || json?.body || `HTTP ${res.status}`)
  }

  return json
}
