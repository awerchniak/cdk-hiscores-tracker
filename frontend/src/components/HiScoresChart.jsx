import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const COLORS = [
  '#c9a227', '#ef5350', '#42a5f5', '#66bb6a',
  '#ab47bc', '#ff7043', '#26c6da', '#ec407a',
  '#7e57c2', '#26a69a',
]

const MAX_RECOMMENDED_LINES = 8

function formatValue(v) {
  if (v == null) return ''
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000)     return `${(v / 1_000).toFixed(1)}K`
  return Math.round(v).toLocaleString()
}

// A "line" is a (player, item) pair. When only one dimension has more than
// one value selected, the other is implied, so the label collapses to just
// the varying dimension (matching the original single-player behavior).
function seriesLabel(player, itemKey, multiPlayer, multiItem) {
  if (multiPlayer && multiItem) return `${player} – ${itemKey}`
  if (multiPlayer) return player
  return itemKey
}

// Raw scrapes are triggered every 30 minutes, but each player's row lands a
// few seconds (or more, under queue backlog) after the trigger — grouping by
// the exact timestamp fractures a single collection cycle across several
// x-axis points. Bucket to the 30-minute mark the scrape belongs to so rows
// from the same cycle line up. Daily/monthly timestamps have no time-of-day
// component and pass through unchanged.
function bucketTimestamp(timestamp) {
  const match = timestamp.match(/^(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):\d{2}$/)
  if (!match) return timestamp
  const [, date, hh, mm] = match
  const bucketMinute = Number(mm) < 30 ? '00' : '30'
  return `${date} ${hh}:${bucketMinute}:00`
}

export default function HiScoresChart({ data, selected, metric, category, caption, zoomYAxis }) {
  if (data.length === 0 || selected.length === 0) {
    return (
      <div className="chart-empty">
        {data.length === 0
          ? 'Run a query to see data.'
          : 'Select at least one item from the list.'}
      </div>
    )
  }

  // Derived from `data` itself, not the live player picker: the picker can
  // change (e.g. removing a player) without a re-query, and grouping by a
  // player list that doesn't match what's actually in `data` merges rows
  // from different players into the same series.
  const players = [...new Set(data.map(item => item.player))]
  const multiPlayer = players.length > 1
  const multiItem = selected.length > 1

  const chartDataByTimestamp = new Map()
  for (const item of data) {
    const bucket = bucketTimestamp(item.timestamp)
    if (!chartDataByTimestamp.has(bucket)) {
      chartDataByTimestamp.set(bucket, { timestamp: bucket })
    }
    const point = chartDataByTimestamp.get(bucket)
    for (const key of selected) {
      const val = item[category]?.[key]?.[metric]
      if (val != null) {
        point[seriesLabel(item.player, key, multiPlayer, multiItem)] = val
      }
    }
  }
  const chartData = [...chartDataByTimestamp.values()]
    .sort((a, b) => a.timestamp.localeCompare(b.timestamp))

  let lineIndex = 0
  const lines = players.flatMap((p, playerIdx) =>
    selected.map((key, itemIdx) => ({
      key: seriesLabel(p, key, multiPlayer, multiItem),
      // Color by whichever dimension varies; if both vary, each line gets
      // its own color in selection order.
      colorIndex: multiPlayer && !multiItem ? playerIdx
        : !multiPlayer ? itemIdx
        : lineIndex++,
    }))
  )
  const lineCount = lines.length
  const tooManyLines = lineCount > MAX_RECOMMENDED_LINES

  const aggLevel = (data[0]?.aggregationLevel ?? '')
    .replace('AggregationLevel.', '')

  return (
    <div className="chart-wrapper">
      {caption && <h3 className="chart-title">{caption}</h3>}
      {aggLevel && <div className="chart-meta">Aggregation: {aggLevel}</div>}
      {tooManyLines && (
        <div className="chart-warning">
          Showing {lineCount} lines ({players.length} players × {selected.length} {category}) —
          the chart may be hard to read. Consider narrowing your player or {category} selection.
        </div>
      )}
      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3a3a3a" />
          <XAxis dataKey="timestamp" tick={{ fill: '#e8d5a3', fontSize: 11 }} />
          <YAxis
            domain={zoomYAxis ? ['auto', 'auto'] : [0, 'auto']}
            tickFormatter={formatValue}
            tick={{ fill: '#e8d5a3', fontSize: 11 }}
            width={60}
          />
          <Tooltip
            formatter={(value, name) => [Math.round(value).toLocaleString(), name]}
            contentStyle={{ background: '#2d2d2d', border: '1px solid #5c4b1e', color: '#e8d5a3' }}
            labelStyle={{ color: '#e8d5a3', fontWeight: 600 }}
          />
          <Legend wrapperStyle={{ color: '#e8d5a3', fontSize: 12 }} />
          {lines.map(line => (
            <Line
              key={line.key}
              type="monotone"
              dataKey={line.key}
              stroke={COLORS[line.colorIndex % COLORS.length]}
              dot={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
