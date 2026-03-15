import { useState, useEffect, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { fetchCounselors, fetchAvailability, type Counselor, type Slot } from '../api/client'
import './CalendarPage.css'

const PERIOD_LABEL: Record<string, string> = { morning: '上午', afternoon: '下午' }
const SLOT_WEEKS = 2
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

export default function CalendarPage() {
  const navigate = useNavigate()
  const [counselors, setCounselors] = useState<Counselor[]>([])
  const [selectedCounselorId, setSelectedCounselorId] = useState<number | null>(null)
  const [slots, setSlots] = useState<Slot[]>([])
  const [loading, setLoading] = useState(false)
  const [weekStart, setWeekStart] = useState(() => getWeekStart(new Date()))

  useEffect(() => {
    fetchCounselors().then((data) => {
      setCounselors(data)
      // Auto-select first counselor when data loads
      if (data.length > 0) {
        setSelectedCounselorId(data[0].id)
      }
    }).catch(console.error)
  }, [])

  const startStr = formatDate(weekStart)
  const endDate = new Date(weekStart)
  endDate.setDate(endDate.getDate() + SLOT_WEEKS * DAYS_PER_WEEK - 1)
  const endStr = formatDate(endDate)

  useEffect(() => {
    if (!selectedCounselorId) {
      setSlots([])
      return
    }
    setLoading(true)
    fetchAvailability(selectedCounselorId, startStr, endStr)
      .then(setSlots)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [selectedCounselorId, startStr, endStr])

  const slotSet = useMemo(
    () => new Set(slots.map((s) => `${s.date}|${s.period}|${s.hour}`)),
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

  const handleSlotClick = (date: string, period: string, hour: number) => {
    if (!selectedCounselorId) return
    navigate('/book', {
      state: { counselorId: selectedCounselorId, date, period, hour },
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
      <header className="calendar-header">
        <div className="title-block">
          <span className="college-badge">长空学院</span>
          <h1>谈话预约与查询</h1>
        </div>
        <Link to="/admin" className="admin-link">管理后台</Link>
        {selectedCounselorId && (
          <div className="counselor-filter">
            <label>选择辅导员：</label>
            <select
              value={selectedCounselorId ?? ''}
              onChange={(e) => setSelectedCounselorId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">请选择</option>
              {counselors.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.employee_id} - {c.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </header>

      {selectedCounselorId && (
        <div className="calendar-toolbar">
          <button type="button" onClick={prevWeek}>上一周</button>
          <span>
            {weekStart.getFullYear()}年{weekStart.getMonth() + 1}月
          </span>
          <button type="button" onClick={nextWeek}>下一周</button>
        </div>
      )}

      {loading && <p className="loading">加载中…</p>}
      {selectedCounselorId && !loading && (
        <div className="calendar-grid">
          <div className="calendar-row header">
            <div className="cell head">日期</div>
            {days.map((d, i) => (
              <div key={i} className="cell head">
                {d.getMonth() + 1}/{d.getDate()}
              </div>
            ))}
          </div>
          {([
            ['morning', 8], ['morning', 9], ['morning', 10], ['morning', 11],
            ['afternoon', 14], ['afternoon', 15], ['afternoon', 16], ['afternoon', 17],
          ] as const).map(([period, hour]) => (
            <div key={`${period}-${hour}`} className="calendar-row">
              <div className="cell label">
                {PERIOD_LABEL[period]} {hour}:00
              </div>
              {days.map((d) => {
                const dateStr = formatDate(d)
                const key = `${dateStr}|${period}|${hour}`
                const available = slotSet.has(key)
                return (
                  <div key={dateStr} className="cell">
                    <button
                      type="button"
                      className={available ? 'slot-available' : 'slot-unavailable'}
                      disabled={!available}
                      onClick={() => available && handleSlotClick(dateStr, period as 'morning' | 'afternoon', hour)}
                    >
                      {available ? '可约' : '—'}
                    </button>
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      )}

      {!selectedCounselorId && !loading && (
        <div className="counselor-selection-center">
          <div className="counselor-selection-card card">
            <h2>选择辅导员</h2>
            <p className="text-secondary">请选择一位辅导员查看可预约时段</p>
            <div className="counselor-filter-center">
              <select
                value={selectedCounselorId ?? ''}
                onChange={(e) => setSelectedCounselorId(e.target.value ? Number(e.target.value) : null)}
              >
                <option value="">请选择</option>
                {counselors.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.employee_id} - {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
