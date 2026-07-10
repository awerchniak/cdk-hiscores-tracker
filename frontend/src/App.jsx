import { useState, useCallback } from 'react'
import Controls from './components/Controls'
import CategorySelector from './components/CategorySelector'
import HiScoresChart from './components/HiScoresChart'
import { fetchHiScores } from './api'
import { SKILLS, ACTIVITIES } from './constants'

const SKILL_METRICS = [
  { value: 'xp',  label: 'XP' },
  { value: 'lvl', label: 'Level' },
  { value: 'rnk', label: 'Rank' },
]

const ACTIVITY_METRICS = [
  { value: 'kc',  label: 'Kill Count' },
  { value: 'rnk', label: 'Rank' },
]

function toDateInput(d) {
  return d.toISOString().slice(0, 10)
}

function sixMonthsAgo() {
  const d = new Date()
  d.setMonth(d.getMonth() - 6)
  return toDateInput(d)
}

export default function App() {
  const [players, setPlayers]         = useState(['Plinybis'])
  const [startDate, setStartDate]     = useState(sixMonthsAgo)
  const [endDate, setEndDate]         = useState(() => toDateInput(new Date()))
  const [granularity, setGranularity] = useState('auto')
  const [zoomYAxis, setZoomYAxis]     = useState(true)

  const [activeTab, setActiveTab]             = useState('Skills')
  const [selectedSkills, setSelectedSkills]   = useState(['Overall'])
  const [skillMetric, setSkillMetric]         = useState('lvl')
  const [selectedActivities, setSelectedActivities] = useState([])
  const [activityMetric, setActivityMetric]   = useState('kc')

  const [data, setData]     = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)

  const handleQuery = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const results = await Promise.all(
        players.map(p => fetchHiScores(p, startDate, endDate, granularity))
      )
      setData(results.flat())
    } catch (e) {
      setError(e.message)
      setData([])
    } finally {
      setLoading(false)
    }
  }, [players, startDate, endDate, granularity])

  const isSkills    = activeTab === 'Skills'
  const selected    = isSkills ? selectedSkills    : selectedActivities
  const metric      = isSkills ? skillMetric       : activityMetric
  const category    = isSkills ? 'skills'          : 'activities'

  const items       = isSkills ? SKILLS        : ACTIVITIES
  const metricLabel = (isSkills ? SKILL_METRICS : ACTIVITY_METRICS)
    .find(m => m.value === metric)?.label ?? metric
  const caption     = selected.length > 0
    ? `${selected.map(key => items.find(i => i.key === key)?.label ?? key).join(', ')} — ${metricLabel}`
    : ''

  return (
    <div className="app">
      <header className="app-header">
        <h1>OSRS HiScores Tracker</h1>
      </header>

      <Controls
        players={players}         onPlayersChange={setPlayers}
        startDate={startDate}     onStartChange={setStartDate}
        endDate={endDate}         onEndChange={setEndDate}
        granularity={granularity} onGranularityChange={setGranularity}
        zoomYAxis={zoomYAxis}     onZoomYAxisChange={setZoomYAxis}
        onQuery={handleQuery}     loading={loading}
      />

      {error && <div className="error">{error}</div>}

      <div className="content">
        <div className="sidebar">
          <div className="tabs">
            {['Skills', 'Activities'].map(tab => (
              <button
                key={tab}
                className={`tab${activeTab === tab ? ' active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          {isSkills ? (
            <CategorySelector
              items={SKILLS}
              selected={selectedSkills}
              onSelect={setSelectedSkills}
              metric={skillMetric}
              onMetricChange={setSkillMetric}
              metrics={SKILL_METRICS}
            />
          ) : (
            <CategorySelector
              items={ACTIVITIES}
              selected={selectedActivities}
              onSelect={setSelectedActivities}
              metric={activityMetric}
              onMetricChange={setActivityMetric}
              metrics={ACTIVITY_METRICS}
            />
          )}
        </div>

        <div className="chart-panel">
          <HiScoresChart
            data={data}
            selected={selected}
            metric={metric}
            category={category}
            caption={caption}
            zoomYAxis={zoomYAxis}
          />
        </div>
      </div>
    </div>
  )
}
