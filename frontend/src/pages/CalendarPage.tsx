import { useState, useEffect, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { fetchCounselors, fetchAvailability, type Counselor, type Slot } from '../api/client'
import AlgorithmArt from '../components/AlgorithmArt'
import './CalendarPage.css'

const PERIOD_LABEL: Record<string, string> = { morning: '上午', afternoon: '下午' }
const WEEKDAY_LABEL: Record<number, string> = {
  1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 0: '日'
}
const SLOT_WEEKS = 1
const DAYS_PER_WEEK = 7

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10)
}

function getWeekStart(d: Date): Date {
  const copy = new Date(d)
  const day = copy.getDay()
  const diff = copy.getDate() - day + (day === 0 ? -6 : 1)
  copy.setDate(diff)
  copy.setHours(0, 0, 0, 0)
  return copy
}

// Simple fuzzy search - check if search text contains query, supports pinyin initials rough matching by name characters
function fuzzyMatch(counselor: Counselor, query: string): boolean {
  if (!query) return true
  const q = query.toLowerCase().trim()
  const fullText = `${counselor.employee_id} ${counselor.name}`.toLowerCase()
  // Direct text contains
  if (fullText.includes(q)) return true
  // Simple initial matching: check if any character in query matches a character in name
  const name = counselor.name.toLowerCase()
  for (const ch of q) {
    if (name.includes(ch)) return true
  }
  return false
}

export default function CalendarPage() {
  const navigate = useNavigate()
  const [counselors, setCounselors] = useState<Counselor[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [slots, setSlots] = useState<Slot[]>([])
  const [loading, setLoading] = useState(false)
  const [weekStart, setWeekStart] = useState(() => getWeekStart(new Date()))

  useEffect(() => {
    fetchCounselors().then((data) => {
      setCounselors(data)
    }).catch(console.error)
  }, [])

  // Filter counselors based on search query
  const filteredCounselors = useMemo(() => {
    if (!searchQuery.trim()) return counselors
    return counselors.filter(c => fuzzyMatch(c, searchQuery))
  }, [counselors, searchQuery])

  const startStr = formatDate(weekStart)
  const endDate = new Date(weekStart)
  endDate.setDate(endDate.getDate() + SLOT_WEEKS * DAYS_PER_WEEK - 1)
  const endStr = formatDate(endDate)

  // Fetch all availability for the date range
  useEffect(() => {
    setLoading(true)
    fetchAvailability(null, startStr, endStr)
      .then(setSlots)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [startStr, endStr])

  // Check (counselorId, date, period) -> available?
  const availabilityMap = useMemo(
    () => {
      const map = new Map<string, boolean>()
      slots.forEach((s) => {
        const key = `${s.counselor_id}|${s.date}|${s.period}`
        map.set(key, true)
      })
      return map
    },
    [slots]
  )

  const days: Date[] = useMemo(() => {
    const list: Date[] = []
    for (let i = 0; i < SLOT_WEEKS * DAYS_PER_WEEK; i++) {
      const d = new Date(weekStart)
      d.setDate(d.getDate() + i)
      list.push(d)
    }
    return list
  }, [weekStart])

  const handleSlotClick = (counselorId: number, date: string, period: string) => {
    navigate('/book', {
      state: { counselorId, date, period },
    })
  }

  const prevWeek = () => {
    const d = new Date(weekStart)
    d.setDate(d.getDate() - DAYS_PER_WEEK)
    setWeekStart(d)
  }
  const nextWeek = () => {
    const d = new Date(weekStart)
    d.setDate(d.getDate() + DAYS_PER_WEEK)
    setWeekStart(d)
  }

  return (
    <div className="calendar-page">
      <AlgorithmArt opacity={0.08} particleCount={40} />
      <header className="calendar-header">
        <div className="title-block">
          <span className="college-badge">长空学院</span>
          <h1>谈话预约与查询</h1>
        </div>
        <div className="counselor-search">
          <input
            type="text"
            placeholder="搜索辅导员..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Link to="/admin" className="admin-link">管理后台</Link>
      </header>

      <div className="calendar-toolbar">
        <button type="button" onClick={prevWeek}>上一周</button>
        <span>
          {weekStart.getFullYear()}年{weekStart.getMonth() + 1}月
        </span>
        <button type="button" onClick={nextWeek}>下一周</button>
      </div>

      {loading && <p className="loading">加载中…</p>}
      {!loading && (
        <div className="calendar-grid">
          {/* Header row with days */}
          <div className="calendar-row header">
            <div className="cell header-label">辅导员</div>
            {days.map((d, i) => (
              <div key={i} className="cell head">
                <div className="day-date">{d.getMonth() + 1}/{d.getDate()}</div>
                <div className="day-weekday">{WEEKDAY_LABEL[d.getDay()]}</div>
              </div>
            ))}
          </div>

          {/* For each counselor × (morning / afternoon) */}
          {filteredCounselors.length === 0 && (
            <div className="no-counselors">
              没有找到匹配的辅导员
            </div>
          )}
          {filteredCounselors.map((counselor) => (
            <div key={counselor.id} className="counselor-group">
              <div className="counselor-header">
                <span className="counselor-header-name">{counselor.name}</span>
              </div>
              {(['morning', 'afternoon'] as const).map((period) => (
                <div key={period} className="calendar-row counselor-period-row">
                  <div className="cell period-label">
                    {PERIOD_LABEL[period]}
                  </div>
                  {days.map((d) => {
                    const dateStr = formatDate(d)
                    const key = `${counselor.id}|${dateStr}|${period}`
                    const available = availabilityMap.has(key)
                    return (
                      <div key={`${counselor.id}|${dateStr}|${period}`} className="cell">
                        <button
                          type="button"
                          className={available ? 'slot-available' : 'slot-unavailable'}
                          disabled={!available}
                          onClick={() => available && handleSlotClick(counselor.id, dateStr, period)}
                        >
                          {available ? '可约' : '—'}
                        </button>
                      </div>
                    )
                  })}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {counselors.length === 0 && !loading && (
        <p className="empty-message">加载辅导员列表中...</p>
      )}
    </div>
  )
}
