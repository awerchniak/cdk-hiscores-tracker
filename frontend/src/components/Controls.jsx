import { useEffect, useState } from 'react'
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
  players, onPlayersChange,
  startDate, onStartChange,
  endDate, onEndChange,
  granularity, onGranularityChange,
  zoomYAxis, onZoomYAxisChange,
  onQuery, loading,
}) {
  const rawDisabled = !!startDate && !!endDate && daysBetween(startDate, endDate) >= RAW_MAX_DAYS
  const [playerInput, setPlayerInput] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [highlighted, setHighlighted] = useState(0)

  useEffect(() => {
    if (rawDisabled && granularity === 'raw') {
      onGranularityChange('auto')
    }
  }, [rawDisabled, granularity, onGranularityChange])

  const filteredPlayers = PLAYERS.filter(p =>
    !players.includes(p) && p.toLowerCase().includes(playerInput.trim().toLowerCase())
  )

  const addPlayer = name => {
    if (!name || players.includes(name)) return
    onPlayersChange([...players, name])
    setPlayerInput('')
    setHighlighted(0)
  }

  const removePlayer = name => {
    onPlayersChange(players.filter(p => p !== name))
  }

  const handlePlayerKeyDown = e => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (filteredPlayers[highlighted]) addPlayer(filteredPlayers[highlighted])
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      setDropdownOpen(true)
      setHighlighted(h => Math.min(h + 1, filteredPlayers.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setHighlighted(h => Math.max(h - 1, 0))
    } else if (e.key === 'Escape') {
      setDropdownOpen(false)
    } else if (e.key === 'Backspace' && !playerInput && players.length > 0) {
      removePlayer(players[players.length - 1])
    }
  }

  return (
    <div className="controls">
      <div className="control-group">
        <label htmlFor="player">Players</label>
        <div className="player-combobox">
          <div className="player-chips">
            {players.map(p => (
              <span key={p} className="player-chip">
                {p}
                <button
                  type="button"
                  className="player-chip-remove"
                  onClick={() => removePlayer(p)}
                  aria-label={`Remove ${p}`}
                >
                  ×
                </button>
              </span>
            ))}
            <input
              id="player"
              type="text"
              value={playerInput}
              onChange={e => {
                setPlayerInput(e.target.value)
                setHighlighted(0)
                setDropdownOpen(true)
              }}
              onFocus={() => setDropdownOpen(true)}
              onBlur={() => setDropdownOpen(false)}
              onKeyDown={handlePlayerKeyDown}
              placeholder={players.length ? 'Add another…' : 'Select a player…'}
              autoComplete="off"
              role="combobox"
              aria-expanded={dropdownOpen}
            />
          </div>
          {dropdownOpen && filteredPlayers.length > 0 && (
            <ul className="player-dropdown">
              {filteredPlayers.map((p, i) => (
                <li
                  key={p}
                  className={`player-option${i === highlighted ? ' highlighted' : ''}`}
                  // onMouseDown fires before the input's onBlur, so the click
                  // still registers before the dropdown closes.
                  onMouseDown={e => { e.preventDefault(); addPlayer(p) }}
                  onMouseEnter={() => setHighlighted(i)}
                >
                  {p}
                </li>
              ))}
            </ul>
          )}
        </div>
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

      <div className="control-group">
        <label>Display</label>
        <label className="checkbox-label" title="Scale the Y-axis to the visible data instead of always starting at zero">
          <input
            type="checkbox"
            checked={zoomYAxis}
            onChange={e => onZoomYAxisChange(e.target.checked)}
          />
          Zoom Y-axis to data
        </label>
      </div>

      <button
        className="query-btn"
        onClick={onQuery}
        disabled={loading || players.length === 0 || !startDate || !endDate}
      >
        {loading ? 'Loading…' : 'Query'}
      </button>
    </div>
  )
}
