import { PLAYERS } from '../constants'

const GRANULARITIES = [
  { value: 'auto',    label: 'Auto',    title: 'Let the backend infer from date range (default: daily)' },
  { value: 'monthly', label: 'Monthly', title: 'Force monthly aggregation (YYYY-MM)' },
  { value: 'daily',   label: 'Daily',   title: 'Force daily aggregation (YYYY-MM-DD)' },
  { value: 'raw',     label: 'Raw',     title: 'No aggregation — best for ranges under 7 days' },
]

export default function Controls({
  player, onPlayerChange,
  startDate, onStartChange,
  endDate, onEndChange,
  granularity, onGranularityChange,
  onQuery, loading,
}) {
  return (
    <div className="controls">
      <div className="control-group">
        <label htmlFor="player">Player</label>
        <input
          id="player"
          type="text"
          value={player}
          onChange={e => onPlayerChange(e.target.value)}
          list="players-list"
          placeholder="Enter player name…"
        />
        <datalist id="players-list">
          {PLAYERS.map(p => <option key={p} value={p} />)}
        </datalist>
      </div>

      <div className="control-group">
        <label htmlFor="start-date">Start</label>
        <input
          id="start-date"
          type="date"
          value={startDate}
          onChange={e => onStartChange(e.target.value)}
        />
      </div>

      <div className="control-group">
        <label htmlFor="end-date">End</label>
        <input
          id="end-date"
          type="date"
          value={endDate}
          onChange={e => onEndChange(e.target.value)}
        />
      </div>

      <div className="control-group">
        <label>Granularity</label>
        <div className="radio-group">
          {GRANULARITIES.map(g => (
            <label key={g.value} className="radio-label" title={g.title}>
              <input
                type="radio"
                name="granularity"
                value={g.value}
                checked={granularity === g.value}
                onChange={() => onGranularityChange(g.value)}
              />
              {g.label}
            </label>
          ))}
        </div>
      </div>

      <button
        className="query-btn"
        onClick={onQuery}
        disabled={loading || !player || !startDate || !endDate}
      >
        {loading ? 'Loading…' : 'Query'}
      </button>
    </div>
  )
}
