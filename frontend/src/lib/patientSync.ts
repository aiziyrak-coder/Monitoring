import { apiUrl } from './api';
import type { PatientData } from '../store';
import { useStore } from '../store';

/** Bitta bemorni serverdan (socket dan mustaqil). */
export async function fetchPatientById(id: string): Promise<PatientData | null> {
  const r = await fetch(apiUrl(`/api/patients/${encodeURIComponent(id)}`));
  if (r.status === 404) return null;
  if (!r.ok) return null;
  return (await r.json()) as PatientData;
}

/** Barcha bemorlarni ro‘yxatdan. */
export async function fetchAllPatients(): Promise<PatientData[] | null> {
  const r = await fetch(apiUrl('/api/patients'));
  if (!r.ok) return null;
  const data = await r.json();
  return Array.isArray(data) ? (data as PatientData[]) : null;
}

/** Store ga birlashtirish (mavjud kartani yangilash yoki yangisini qo‘shish). */
export function mergePatientsIntoStore(rows: PatientData[]) {
  useStore.setState((s) => {
    const next = { ...s.patients };
    for (const row of rows) {
      const prev = next[row.id];
      next[row.id] = prev ? { ...prev, ...row } : row;
    }
    return { patients: next };
  });
}
