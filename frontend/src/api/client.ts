const API_BASE = import.meta.env.VITE_API_URL || '/api';

export type Counselor = {
  id: number;
  employee_id: string;
  name: string;
  email: string;
  is_active?: boolean;
};

export type Slot = {
  date: string;
  period: 'morning' | 'afternoon';
  hour: number;
  counselor_id: number;
};

export async function fetchCounselors(): Promise<Counselor[]> {
  const r = await fetch(`${API_BASE}/counselors`);
  if (!r.ok) throw new Error('Failed to fetch counselors');
  return r.json();
}

export async function fetchAvailability(
  counselorId: number | null,
  startDate: string,
  endDate: string
): Promise<Slot[]> {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  });
  if (counselorId !== null) {
    params.set('counselor_id', String(counselorId));
  }
  const r = await fetch(`${API_BASE}/availability?${params}`);
  if (!r.ok) throw new Error('Failed to fetch availability');
  return r.json();
}

export type CreateAppointmentBody = {
  counselor_id: number;
  date: string;
  period: 'morning' | 'afternoon';
  hour: number;
  content: string;
  contact_name: string;
  contact_phone?: string | null;
  contact_email?: string | null;
};

export async function createAppointment(body: CreateAppointmentBody): Promise<{ id: number }> {
  const r = await fetch(`${API_BASE}/appointments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    const msg = Array.isArray(err.detail) ? err.detail.map((e: { msg?: string }) => e.msg).join(', ') : (err.detail || r.statusText);
    throw new Error(msg);
  }
  return r.json();
}

// ---------- Admin API ----------

export async function fetchCounselorsAdmin(): Promise<Counselor[]> {
  const r = await fetch(`${API_BASE}/counselors?all=true`);
  if (!r.ok) throw new Error('Failed to fetch counselors');
  return r.json();
}

export type CounselorCreate = { employee_id: string; name: string; email: string; is_active?: boolean };
export type CounselorUpdate = { employee_id?: string; name?: string; email?: string; is_active?: boolean };

export async function createCounselor(body: CounselorCreate): Promise<Counselor> {
  const r = await fetch(`${API_BASE}/counselors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(typeof err.detail === 'string' ? err.detail : '创建失败');
  }
  return r.json();
}

export async function updateCounselor(id: number, body: CounselorUpdate): Promise<Counselor> {
  const r = await fetch(`${API_BASE}/counselors/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(typeof err.detail === 'string' ? err.detail : '更新失败');
  }
  return r.json();
}

export async function deleteCounselor(id: number): Promise<void> {
  const r = await fetch(`${API_BASE}/counselors/${id}`, { method: 'DELETE' });
  if (!r.ok) throw new Error('删除失败');
}

export type SlotTemplate = {
  id: number;
  period: string;
  hour: number;
};

export async function fetchSlotTemplates(): Promise<SlotTemplate[]> {
  const r = await fetch(`${API_BASE}/slot-templates`);
  if (!r.ok) throw new Error('Failed to fetch slot templates');
  return r.json();
}

export async function createSlotTemplate(period: string, hour: number): Promise<SlotTemplate> {
  const r = await fetch(`${API_BASE}/slot-templates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ period, hour }),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(typeof err.detail === 'string' ? err.detail : '创建失败');
  }
  return r.json();
}

export async function updateSlotTemplate(id: number, period: string, hour: number): Promise<SlotTemplate> {
  const r = await fetch(`${API_BASE}/slot-templates/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ period, hour }),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(typeof err.detail === 'string' ? err.detail : '更新失败');
  }
  return r.json();
}

export async function deleteSlotTemplate(id: number): Promise<void> {
  const r = await fetch(`${API_BASE}/slot-templates/${id}`, { method: 'DELETE' });
  if (!r.ok) throw new Error('删除失败');
}

export type AppointmentListItem = {
  id: number;
  counselor_id: number;
  date: string;
  period: string;
  hour: number;
  content: string;
  contact_name: string;
  contact_phone: string | null;
  contact_email: string | null;
  status: string;
  created_at: string | null;
};

export async function fetchAppointments(params?: {
  counselor_id?: number;
  start_date?: string;
  end_date?: string;
}): Promise<AppointmentListItem[]> {
  const search = new URLSearchParams();
  if (params?.counselor_id != null) search.set('counselor_id', String(params.counselor_id));
  if (params?.start_date) search.set('start_date', params.start_date);
  if (params?.end_date) search.set('end_date', params.end_date);
  const q = search.toString();
  const r = await fetch(`${API_BASE}/appointments${q ? `?${q}` : ''}`);
  if (!r.ok) throw new Error('Failed to fetch appointments');
  return r.json();
}

export async function deleteAppointment(id: number): Promise<void> {
  const r = await fetch(`${API_BASE}/appointments/${id}`, { method: 'DELETE' });
  if (!r.ok) throw new Error('取消失败');
}
