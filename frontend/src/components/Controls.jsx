import { useEffect } from 'react'
import { PLAYERS } from '../constants'

const RAW_MAX_DAYS = 7

const GRANULARITIES = [
  { value: 'auto',    label: 'Auto',    title: 'Let the backend infer from date range (default: daily)' },
  { value: 'monthly', label: 'Monthly', title: 'Force monthly aggregation (YYYY-MM)' },
  { value: 'daily',   label: 'Daily',   title: 'Force daily aggregation (YYYY-MM-DD)' },
  { value: 'raw',     label: 'Raw',     title: `No aggregation — only available for ranges under ${RAW_MAX_DAYS} days` },
]

function daysBetween(startDate, endDate) {
  const start = new Date(startDate)
  const end = new Date(endDate)
  return (end - start) / (1000 * 60 * 60 * 24)
}

export default function Controls({
  player, onPlayerChange,
  startDate, onStartChange,
  endDate, onEndChange,
  granularity, onGranularityChange,
  onQuery, loading,
}) {
  const rawDisabled = !!startDate && !!endDate && daysBetween(startDate, endDate) >= RAW_MAX_DAYS

  useEffect(() => {
    if (rawDisabled && granularity === 'raw') {
      onGranularityChange('auto')
    }
  }, [rawDisabled, granularity, onGranularityChange])

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
          {GRANULARITIES.map(g => {
            const disabled = g.value === 'raw' && rawDisabled
            return (
              <label
                key={g.value}
                className={`radio-label${disabled ? ' disabled' : ''}`}
                title={disabled ? `Raw is only available for ranges under ${RAW_MAX_DAYS} days` : g.title}
              >
                <input
                  type="radio"
                  name="granularity"
                  value={g.value}
                  checked={granularity === g.value}
                  disabled={disabled}
                  onChange={() => onGranularityChange(g.value)}
                />
                {g.label}
                {disabled && (
                  <span className="granularity-hint">
                    Raw disabled — select a range under {RAW_MAX_DAYS} days to use it.
                  </span>
                )}
              </label>
            )
          })}
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
