import { useNavigate, useLocation } from 'react-router-dom'
import './SuccessPage.css'

const PERIOD_LABEL: Record<string, string> = { morning: '上午', afternoon: '下午' }

export default function SuccessPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const state = (location.state || {}) as { date?: string; period?: string; hour?: number }

  return (
    <div className="success-page">
      <span className="college-badge">长空学院</span>
      <h1>预约成功</h1>
      <p className="message">
        您的预约已提交。若已配置邮件，辅导员将收到通知。
        {state.date && state.period && state.hour != null && (
          <span className="detail">
            预约时间：{state.date} {PERIOD_LABEL[state.period] ?? state.period} {state.hour}:00
          </span>
        )}
      </p>
      <button type="button" className="back" onClick={() => navigate('/')}>
        返回日历
      </button>
    </div>
  )
}
