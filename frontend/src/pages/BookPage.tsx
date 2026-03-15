import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { fetchCounselors, createAppointment, type Counselor } from '../api/client'
import './BookPage.css'

type LocationState = {
  counselorId?: number
  date?: string
  period?: 'morning' | 'afternoon'
  hour?: number
}

const PERIOD_LABEL: Record<string, string> = { morning: '上午', afternoon: '下午' }

export default function BookPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const state = (location.state || {}) as LocationState

  const [counselors, setCounselors] = useState<Counselor[]>([])
  const [counselorId, setCounselorId] = useState<number>(state.counselorId ?? 0)
  const [date, setDate] = useState(state.date ?? '')
  const [period, setPeriod] = useState<'morning' | 'afternoon'>(state.period ?? 'morning')
  const [hour, setHour] = useState<number>(() => {
    // Default to first available hour for the period
    if (state.hour !== undefined) return state.hour
    return state.period === 'afternoon' ? 14 : 8
  })
  const [content, setContent] = useState('')
  const [contactName, setContactName] = useState('')
  const [contactPhone, setContactPhone] = useState('')
  const [contactEmail, setContactEmail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchCounselors().then(setCounselors).catch(console.error)
  }, [])

  useEffect(() => {
    if (state.counselorId) setCounselorId(state.counselorId)
    if (state.date) setDate(state.date)
    if (state.period) {
      setPeriod(state.period)
      // If no hour specified from calendar, set default to first hour of the period
      if (state.hour === undefined) {
        setHour(state.period === 'afternoon' ? 14 : 8)
      }
    }
    if (state.hour !== undefined) setHour(state.hour)
  }, [state.counselorId, state.date, state.period, state.hour])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!counselorId || !date || !content.trim() || !contactName.trim()) {
      setError('请填写辅导员、日期、内容和联系人。')
      return
    }
    if (!contactPhone.trim() && !contactEmail.trim()) {
      setError('请至少填写电话或邮箱之一。')
      return
    }
    setSubmitting(true)
    try {
      await createAppointment({
        counselor_id: counselorId,
        date,
        period,
        hour,
        content: content.trim(),
        contact_name: contactName.trim(),
        contact_phone: contactPhone.trim() || null,
        contact_email: contactEmail.trim() || null,
      })
      navigate('/success', { state: { date, period, hour } })
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败，请重试。')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="book-page">
      <header className="book-header">
        <div className="title-block">
          <span className="college-badge">长空学院</span>
          <h1>填写预约</h1>
        </div>
        <button type="button" className="back" onClick={() => navigate('/')}>
          返回日历
        </button>
      </header>
      <form className="book-form" onSubmit={handleSubmit}>
        {error && <p className="form-error">{error}</p>}
        <div className="field">
          <label>辅导员 *</label>
          <select
            value={counselorId || ''}
            onChange={(e) => setCounselorId(Number(e.target.value))}
            required
          >
            <option value="">请选择</option>
            {counselors.map((c) => (
              <option key={c.id} value={c.id}>
                {c.employee_id} - {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>日期 *</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>时段 *</label>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value as 'morning' | 'afternoon')}
          >
            <option value="morning">{PERIOD_LABEL.morning}</option>
            <option value="afternoon">{PERIOD_LABEL.afternoon}</option>
          </select>
        </div>
        <div className="field">
          <label>具体小时 *</label>
          <select value={hour} onChange={(e) => setHour(Number(e.target.value))}>
            {period === 'morning'
              ? [8, 9, 10, 11].map((h) => (
                  <option key={h} value={h}>
                    {h}:00
                  </option>
                ))
              : [14, 15, 16, 17].map((h) => (
                  <option key={h} value={h}>
                    {h}:00
                  </option>
                ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="content">谈话内容/主题 *</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            required
            placeholder="简要说明预约事由"
          />
        </div>
        <div className="field">
          <label htmlFor="contact-name">联系人姓名 *</label>
          <input
            id="contact-name"
            type="text"
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
            required
            placeholder="您的姓名"
          />
        </div>
        <div className="field">
          <label htmlFor="contact-phone">联系电话</label>
          <input
            id="contact-phone"
            type="tel"
            value={contactPhone}
            onChange={(e) => setContactPhone(e.target.value)}
            placeholder="手机号"
          />
        </div>
        <div className="field">
          <label htmlFor="contact-email">联系邮箱</label>
          <input
            id="contact-email"
            type="email"
            value={contactEmail}
            onChange={(e) => setContactEmail(e.target.value)}
            placeholder="email@example.com"
          />
        </div>
        <p className="hint">请至少填写电话或邮箱之一。</p>
        <button type="submit" className="submit" disabled={submitting}>
          {submitting ? '提交中…' : '提交预约'}
        </button>
      </form>
    </div>
  )
}
