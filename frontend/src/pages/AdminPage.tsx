import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  fetchCounselorsAdmin,
  createCounselor,
  updateCounselor,
  deleteCounselor,
  fetchSlotTemplates,
  createSlotTemplate,
  updateSlotTemplate,
  deleteSlotTemplate,
  fetchAppointments,
  deleteAppointment,
  type Counselor,
  type SlotTemplate,
  type AppointmentListItem,
} from '../api/client'
import './AdminPage.css'

const PERIOD_LABEL: Record<string, string> = { morning: '上午', afternoon: '下午' }

type Tab = 'counselors' | 'slots' | 'appointments'

export default function AdminPage() {
  const navigate = useNavigate()
  const [tab, setTab] = useState<Tab>('counselors')
  const [counselors, setCounselors] = useState<Counselor[]>([])
  const [slots, setSlots] = useState<SlotTemplate[]>([])
  const [appointments, setAppointments] = useState<AppointmentListItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [counselorForm, setCounselorForm] = useState<Partial<Counselor> | null>(null)
  const [slotForm, setSlotForm] = useState<Partial<SlotTemplate> | null>(null)

  const loadCounselors = () => {
    setLoading(true)
    fetchCounselorsAdmin()
      .then(setCounselors)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }
  const loadSlots = () => {
    setLoading(true)
    fetchSlotTemplates()
      .then(setSlots)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }
  const loadAppointments = () => {
    setLoading(true)
    fetchAppointments()
      .then(setAppointments)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (tab === 'counselors') loadCounselors()
    else if (tab === 'slots') loadSlots()
    else loadAppointments()
  }, [tab])

  const onCounselorSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!counselorForm) return
    setError('')
    try {
      if (counselorForm.id) {
        await updateCounselor(counselorForm.id, {
          employee_id: counselorForm.employee_id,
          name: counselorForm.name,
          email: counselorForm.email,
          is_active: counselorForm.is_active,
        })
      } else {
        await createCounselor({
          employee_id: counselorForm.employee_id!,
          name: counselorForm.name!,
          email: counselorForm.email!,
          is_active: counselorForm.is_active ?? true,
        })
      }
      setCounselorForm(null)
      loadCounselors()
    } catch (e) {
      setError(e instanceof Error ? e.message : '操作失败')
    }
  }

  const onSlotSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!slotForm || slotForm.period == null || slotForm.hour == null) return
    setError('')
    try {
      if (slotForm.id) {
        await updateSlotTemplate(slotForm.id, slotForm.period, slotForm.hour)
      } else {
        await createSlotTemplate(slotForm.period, slotForm.hour)
      }
      setSlotForm(null)
      loadSlots()
    } catch (e) {
      setError(e instanceof Error ? e.message : '操作失败')
    }
  }

  const onDeleteCounselor = async (id: number) => {
    if (!confirm('确定要停用该辅导员吗？')) return
    try {
      await deleteCounselor(id)
      loadCounselors()
    } catch (e) {
      setError(e instanceof Error ? e.message : '删除失败')
    }
  }

  const onDeleteSlot = async (id: number) => {
    if (!confirm('确定删除该时段？')) return
    try {
      await deleteSlotTemplate(id)
      loadSlots()
    } catch (e) {
      setError(e instanceof Error ? e.message : '删除失败')
    }
  }

  const onCancelAppointment = async (id: number) => {
    if (!confirm('确定取消该预约？')) return
    try {
      await deleteAppointment(id)
      loadAppointments()
    } catch (e) {
      setError(e instanceof Error ? e.message : '取消失败')
    }
  }

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="title-block">
          <span className="college-badge">长空学院</span>
          <h1>管理后台</h1>
        </div>
        <button type="button" className="back" onClick={() => navigate('/')}>
          返回预约页
        </button>
      </header>
      <nav className="admin-tabs">
        <button
          type="button"
          className={tab === 'counselors' ? 'active' : ''}
          onClick={() => setTab('counselors')}
        >
          辅导员
        </button>
        <button
          type="button"
          className={tab === 'slots' ? 'active' : ''}
          onClick={() => setTab('slots')}
        >
          可预约时段
        </button>
        <button
          type="button"
          className={tab === 'appointments' ? 'active' : ''}
          onClick={() => setTab('appointments')}
        >
          预约记录
        </button>
      </nav>
      {error && (
        <div className="admin-error" role="alert">
          {error}
          <button type="button" onClick={() => setError('')}>关闭</button>
        </div>
      )}
      {loading && <p className="admin-loading">加载中…</p>}

      {tab === 'counselors' && (
        <section className="admin-section">
          <div className="section-head">
            <h2>辅导员管理</h2>
            <button type="button" onClick={() => setCounselorForm({ employee_id: '', name: '', email: '', is_active: true })}>
              新增辅导员
            </button>
          </div>
          {counselorForm && (
            <form className="admin-form" onSubmit={onCounselorSubmit}>
              <input
                placeholder="工号"
                value={counselorForm.employee_id ?? ''}
                onChange={(e) => setCounselorForm({ ...counselorForm, employee_id: e.target.value })}
                required
              />
              <input
                placeholder="姓名"
                value={counselorForm.name ?? ''}
                onChange={(e) => setCounselorForm({ ...counselorForm, name: e.target.value })}
                required
              />
              <input
                type="email"
                placeholder="邮箱"
                value={counselorForm.email ?? ''}
                onChange={(e) => setCounselorForm({ ...counselorForm, email: e.target.value })}
                required
              />
              {counselorForm.id != null && (
                <label>
                  <input
                    type="checkbox"
                    checked={counselorForm.is_active ?? true}
                    onChange={(e) => setCounselorForm({ ...counselorForm, is_active: e.target.checked })}
                  />
                  启用
                </label>
              )}
              <div className="form-actions">
                <button type="submit">{counselorForm.id != null ? '保存' : '新增'}</button>
                <button type="button" onClick={() => setCounselorForm(null)}>取消</button>
              </div>
            </form>
          )}
          <table className="admin-table">
            <thead>
              <tr>
                <th>工号</th>
                <th>姓名</th>
                <th>邮箱</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {counselors.map((c) => (
                <tr key={c.id}>
                  <td>{c.employee_id}</td>
                  <td>{c.name}</td>
                  <td>{c.email}</td>
                  <td>{c.is_active !== false ? '启用' : '停用'}</td>
                  <td>
                    <button type="button" onClick={() => setCounselorForm({ ...c })}>编辑</button>
                    {c.is_active !== false && (
                      <button type="button" className="danger" onClick={() => onDeleteCounselor(c.id)}>停用</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {tab === 'slots' && (
        <section className="admin-section">
          <div className="section-head">
            <h2>可预约时段</h2>
            <button type="button" onClick={() => setSlotForm({ period: 'morning', hour: 8 })}>
              新增时段
            </button>
          </div>
          {slotForm && (
            <form className="admin-form" onSubmit={onSlotSubmit}>
              <select
                value={slotForm.period ?? 'morning'}
                onChange={(e) => setSlotForm({ ...slotForm, period: e.target.value })}
              >
                <option value="morning">上午</option>
                <option value="afternoon">下午</option>
              </select>
              <input
                type="number"
                min={0}
                max={23}
                placeholder="小时(0-23)"
                value={slotForm.hour ?? 8}
                onChange={(e) => setSlotForm({ ...slotForm, hour: parseInt(e.target.value, 10) || 0 })}
              />
              <div className="form-actions">
                <button type="submit">{slotForm.id != null ? '保存' : '新增'}</button>
                <button type="button" onClick={() => setSlotForm(null)}>取消</button>
              </div>
            </form>
          )}
          <table className="admin-table">
            <thead>
              <tr>
                <th>时段</th>
                <th>小时</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {slots.map((s) => (
                <tr key={s.id}>
                  <td>{PERIOD_LABEL[s.period] ?? s.period}</td>
                  <td>{s.hour}:00</td>
                  <td>
                    <button type="button" onClick={() => setSlotForm({ ...s })}>编辑</button>
                    <button type="button" className="danger" onClick={() => onDeleteSlot(s.id)}>删除</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {tab === 'appointments' && (
        <section className="admin-section">
          <h2>预约记录</h2>
          <table className="admin-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>时段</th>
                <th>内容</th>
                <th>联系人</th>
                <th>联系方式</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((a) => (
                <tr key={a.id}>
                  <td>{a.date}</td>
                  <td>{PERIOD_LABEL[a.period] ?? a.period} {a.hour}:00</td>
                  <td>{a.content}</td>
                  <td>{a.contact_name}</td>
                  <td>{a.contact_phone || a.contact_email || '—'}</td>
                  <td>{a.status === 'confirmed' ? '已确认' : a.status === 'cancelled' ? '已取消' : a.status}</td>
                  <td>
                    {a.status === 'confirmed' && (
                      <button type="button" className="danger" onClick={() => onCancelAppointment(a.id)}>取消预约</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {appointments.length === 0 && !loading && <p className="empty">暂无预约记录</p>}
        </section>
      )}
    </div>
  )
}
