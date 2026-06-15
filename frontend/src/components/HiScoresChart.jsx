import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const COLORS = [
  '#c9a227', '#ef5350', '#42a5f5', '#66bb6a',
  '#ab47bc', '#ff7043', '#26c6da', '#ec407a',
  '#7e57c2', '#26a69a',
]

function formatValue(v) {
  if (v == null) return ''
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000)     return `${(v / 1_000).toFixed(1)}K`
  return Math.round(v).toLocaleString()
}

export default function HiScoresChart({ data, selected, metric, category }) {
  if (data.length === 0 || selected.length === 0) {
    return (
      <div className="chart-empty">
        {data.length === 0
          ? 'Run a query to see data.'
          : 'Select at least one item from the list.'}
      </div>
    )
  }

  const chartData = data.map(item => {
    const point = { timestamp: item.timestamp }
    for (const key of selected) {
      const val = item[category]?.[key]?.[metric]
      if (val != null) point[key] = val
    }
    return point
  })

  const aggLevel = (data[0]?.aggregationLevel ?? '')
    .replace('AggregationLevel.', '')

  return (
    <div className="chart-wrapper">
      {aggLevel && <div className="chart-meta">Aggregation: {aggLevel}</div>}
      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3a3a3a" />
          <XAxis dataKey="timestamp" tick={{ fill: '#e8d5a3', fontSize: 11 }} />
          <YAxis
            tickFormatter={formatValue}
            tick={{ fill: '#e8d5a3', fontSize: 11 }}
            width={60}
          />
          <Tooltip
            formatter={(value, name) => [Math.round(value).toLocaleString(), name]}
            contentStyle={{ background: '#2d2d2d', border: '1px solid #5c4b1e', color: '#e8d5a3' }}
            labelStyle={{ color: '#c9a227' }}
          />
          <Legend wrapperStyle={{ color: '#e8d5a3', fontSize: 12 }} />
          {selected.map((key, i) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={COLORS[i % COLORS.length]}
              dot={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
