export default function CategorySelector({ items, selected, onSelect, metric, onMetricChange, metrics }) {
  const toggle = key => {
    onSelect(selected.includes(key)
      ? selected.filter(k => k !== key)
      : [...selected, key]
    )
  }

  return (
    <div className="selector">
      <div className="selector-actions">
        <button className="btn-sm" onClick={() => onSelect(items.map(i => i.key))}>All</button>
        <button className="btn-sm" onClick={() => onSelect([])}>None</button>
      </div>

      <div className="items-list">
        {items.map(({ key, label }) => (
          <label key={key} className="item-checkbox">
            <input
              type="checkbox"
              checked={selected.includes(key)}
              onChange={() => toggle(key)}
            />
            {label}
          </label>
        ))}
      </div>

      <div className="metric-group">
        <p>Metric</p>
        <div className="radio-group">
          {metrics.map(m => (
            <label key={m.value} className="radio-label">
              <input
                type="radio"
                name="metric"
                value={m.value}
                checked={metric === m.value}
                onChange={() => onMetricChange(m.value)}
              />
              {m.label}
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}
