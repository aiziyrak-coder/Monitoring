import { create } from 'zustand';
import { io, Socket } from 'socket.io-client';
import { socketIoUrl } from './lib/api';

export interface VitalSigns {
  hr: number;
  spo2: number;
  nibpSys: number;
  nibpDia: number;
  rr: number;
  temp: number;
  nibpTime?: number;
}

export interface AlarmLimits {
  hr: { low: number; high: number };
  spo2: { low: number; high: number };
  nibpSys: { low: number; high: number };
  nibpDia: { low: number; high: number };
  rr: { low: number; high: number };
  temp: { low: number; high: number };
}

export interface AlarmState {
  level: 'none' | 'blue' | 'yellow' | 'red' | 'purple';
  message?: string;
  patientId?: string;
}

export interface VitalHistory {
  timestamp: number;
  hr: number;
  spo2: number;
  nibpSys: number;
  nibpDia: number;
  rr: number;
  temp: number;
}

export interface Medication {
  id: string;
  name: string;
  dose: string;
  rate?: string;
}

export interface LabResult {
  id: string;
  name: string;
  value: string;
  unit: string;
  time: number;
  isAbnormal: boolean;
}

export interface ClinicalNote {
  id: string;
  text: string;
  author: string;
  time: number;
}

export interface PatientData {
  id: string;
  name: string;
  /** Bemor yotgan karavat (qurilma ham shu ID ga biriktirilishi kerak) */
  bedId?: string | null;
  /** Shu karavatdagi qurilma (server ma'lumoti) */
  linkedDeviceId?: string | null;
  linkedDeviceLastSeenMs?: number | null;
  /** Bemorga oxirgi muvaffaqiyatli vital yozilgan vaqt (ms) */
  linkedDeviceLastVitalsAppliedMs?: number | null;
  room: string;
  diagnosis: string;
  doctor: string;
  assignedNurse: string;
  deviceBattery: number;
  admissionDate: number;
  vitals: VitalSigns;
  alarm: AlarmState;
  alarmLimits: AlarmLimits;
  scheduledCheck?: {
    intervalMs: number;
    nextCheckTime: number;
  };
  history: VitalHistory[];
  isPinned: boolean;
  lastRealVitalsMs?: number | null;
  medications: Medication[];
  labs: LabResult[];
  notes: ClinicalNote[];
}

/** Socket `vitals_update` dan minimal bemor kartasi (kartada yo‘q bo‘lsa ham yangilanish yo‘qolmasin). */
function patientStubFromVitalsUpdate(update: VitalsUpdatePayload): PatientData {
  return {
    id: update.id,
    name: '',
    room: '',
    diagnosis: '',
    doctor: '',
    assignedNurse: '',
    bedId: update.bedId ?? null,
    linkedDeviceId: update.linkedDeviceId ?? null,
    linkedDeviceLastSeenMs: update.linkedDeviceLastSeenMs ?? null,
    linkedDeviceLastVitalsAppliedMs: update.linkedDeviceLastVitalsAppliedMs ?? null,
    deviceBattery: update.deviceBattery ?? 100,
    admissionDate: Date.now(),
    vitals: update.vitals,
    alarm: update.alarm,
    alarmLimits: update.alarmLimits,
    scheduledCheck: update.scheduledCheck,
    history: update.history ?? [],
    isPinned: update.isPinned ?? false,
    lastRealVitalsMs: update.lastRealVitalsMs ?? null,
    medications: update.medications ?? [],
    labs: update.labs ?? [],
    notes: update.notes ?? [],
  };
}

/** Server `vitals_update` payload (one row per patient). */
export interface VitalsUpdatePayload {
  id: string;
  vitals: VitalSigns;
  alarm: AlarmState;
  alarmLimits: AlarmLimits;
  scheduledCheck?: PatientData['scheduledCheck'];
  deviceBattery: number;
  isPinned: boolean;
  lastRealVitalsMs?: number | null;
  bedId?: string | null;
  linkedDeviceId?: string | null;
  linkedDeviceLastSeenMs?: number | null;
  linkedDeviceLastVitalsAppliedMs?: number | null;
  medications: Medication[];
  labs: LabResult[];
  notes: ClinicalNote[];
  history?: VitalHistory[];
}

interface AppState {
  patients: Record<string, PatientData>;
  socket: Socket | null;
  privacyMode: boolean;
  searchQuery: string;
  selectedPatientId: string | null;
  isAudioMuted: boolean;
  togglePrivacyMode: () => void;
  setSearchQuery: (q: string) => void;
  setSelectedPatientId: (id: string | null) => void;
  toggleAudioMute: () => void;
  togglePinPatient: (patientId: string) => void;
  addClinicalNote: (patientId: string, note: Omit<ClinicalNote, 'id' | 'time'>) => void;
  acknowledgeAlarm: (patientId: string) => void;
  setSchedule: (patientId: string, intervalMs: number) => void;
  setAllSchedules: (intervalMs: number) => void;
  clearAlarm: (patientId: string) => void;
  updateLimits: (patientId: string, limits: Partial<AlarmLimits>) => void;
  admitPatient: (data: Partial<PatientData>) => void;
  dischargePatient: (patientId: string) => void;
  connect: () => void;
  disconnect: () => void;
}

export const useStore = create<AppState>((set, get) => ({
  patients: {},
  socket: null,
  privacyMode: false,
  searchQuery: '',
  selectedPatientId: null,
  isAudioMuted: false,
  
  togglePrivacyMode: () => set((state) => ({ privacyMode: !state.privacyMode })),
  setSearchQuery: (q) => set({ searchQuery: q }),
  setSelectedPatientId: (id) => set({ selectedPatientId: id }),
  toggleAudioMute: () => set((state) => ({ isAudioMuted: !state.isAudioMuted })),
  
  togglePinPatient: (patientId) => {
    const socket = get().socket;
    if (socket) socket.emit('toggle_pin', { patientId });
  },
  addClinicalNote: (patientId, note) => {
    const socket = get().socket;
    if (socket) socket.emit('add_note', { patientId, note });
  },
  acknowledgeAlarm: (patientId) => {
    const socket = get().socket;
    if (socket) socket.emit('acknowledge_alarm', { patientId });
  },

  setSchedule: (patientId, intervalMs) => {
    const socket = get().socket;
    if (socket) {
      socket.emit('set_schedule', { patientId, intervalMs });
    }
  },
  setAllSchedules: (intervalMs) => {
    const socket = get().socket;
    if (socket) {
      socket.emit('set_all_schedules', { intervalMs });
    }
  },
  clearAlarm: (patientId) => {
    const socket = get().socket;
    if (socket) {
      socket.emit('clear_alarm', { patientId });
    }
  },
  updateLimits: (patientId, limits) => {
    const socket = get().socket;
    if (socket) {
      socket.emit('update_limits', { patientId, limits });
    }
  },
  admitPatient: (data) => {
    const socket = get().socket;
    if (socket) {
      socket.emit('admit_patient', data);
    }
  },
  dischargePatient: (patientId) => {
    const socket = get().socket;
    if (socket) {
      socket.emit('discharge_patient', { patientId });
    }
  },
  connect: () => {
    if (get().socket) return;
    
    const socket = io(socketIoUrl(), {
      path: '/socket.io',
      // WebSocket tezroq; proxy xato bersa avtomatik polling ga o‘tadi
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 8000,
      timeout: 25000,
    });
    
    socket.on('initial_state', (data: PatientData[]) => {
      const patientsMap = data.reduce((acc, p) => {
        acc[p.id] = p;
        return acc;
      }, {} as Record<string, PatientData>);
      set({ patients: patientsMap });
    });

    socket.on('vitals_update', (updates: VitalsUpdatePayload[]) => {
      set((state) => {
        const newPatients = { ...state.patients };
        updates.forEach((update) => {
          const p = newPatients[update.id] ?? patientStubFromVitalsUpdate(update);
          newPatients[update.id] = {
            ...p,
            vitals: update.vitals,
            alarm: update.alarm,
            alarmLimits: update.alarmLimits ?? p.alarmLimits,
            scheduledCheck: update.scheduledCheck,
            deviceBattery: update.deviceBattery ?? p.deviceBattery,
            history: update.history ?? p.history,
            isPinned: update.isPinned ?? p.isPinned,
            lastRealVitalsMs:
              update.lastRealVitalsMs !== undefined
                ? update.lastRealVitalsMs
                : p.lastRealVitalsMs,
            medications: update.medications ?? p.medications,
            labs: update.labs ?? p.labs,
            notes: update.notes ?? p.notes,
            bedId: update.bedId !== undefined ? update.bedId : p.bedId,
            linkedDeviceId:
              update.linkedDeviceId !== undefined
                ? update.linkedDeviceId
                : p.linkedDeviceId,
            linkedDeviceLastSeenMs:
              update.linkedDeviceLastSeenMs !== undefined
                ? update.linkedDeviceLastSeenMs
                : p.linkedDeviceLastSeenMs,
            linkedDeviceLastVitalsAppliedMs:
              update.linkedDeviceLastVitalsAppliedMs !== undefined
                ? update.linkedDeviceLastVitalsAppliedMs
                : p.linkedDeviceLastVitalsAppliedMs,
          };
        });
        return { patients: newPatients };
      });
    });

    socket.on('patient_admitted', (patient: PatientData) => {
      set((state) => ({
        patients: { ...state.patients, [patient.id]: patient }
      }));
    });

    socket.on('patient_discharged', (patientId: string) => {
      set((state) => {
        const newPatients = { ...state.patients };
        delete newPatients[patientId];
        return { 
          patients: newPatients,
          selectedPatientId: state.selectedPatientId === patientId ? null : state.selectedPatientId
        };
      });
    });

    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
    });

    socket.on('disconnect', (reason) => {
      if (reason === 'io server disconnect') {
        socket.connect();
      }
      // transport close / ping timeout — client o'zi qayta ulanadi; konsolni ifloslamaslik
      else if (reason !== 'transport close' && reason !== 'ping timeout') {
        console.warn('Socket disconnected:', reason);
      }
    });

    set({ socket });
  },
  disconnect: () => {
    const socket = get().socket;
    if (socket) {
      socket.disconnect();
      set({ socket: null });
    }
  }
}));
