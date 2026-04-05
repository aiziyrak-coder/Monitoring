import React, { useState, useEffect } from 'react';
import { apiUrl } from '../lib/api';
import { useStore } from '../store';
import { X, UserPlus } from 'lucide-react';
import { LocationCascadeSelects } from './LocationCascadeSelects';

export function AdmitPatientModal({ onClose }: { onClose: () => void }) {
  const admitPatient = useStore(state => state.admitPatient);
  const [departments, setDepartments] = useState<any[]>([]);
  const [beds, setBeds] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [departmentId, setDepartmentId] = useState('');
  const [roomId, setRoomId] = useState('');
  const [bedId, setBedId] = useState('');
  
  useEffect(() => {
    const controller = new AbortController();
    
    fetch(apiUrl('/api/infrastructure'), { signal: controller.signal })
      .then(res => {
        if (!res.ok) throw new Error("Infratuzilma ma'lumotlarini yuklashda xatolik");
        return res.json();
      })
      .then(data => {
        setDepartments(data.departments || []);
        setBeds(data.beds || []);
        setRooms(data.rooms || []);
        setIsLoading(false);
      })
      .catch(err => {
        if (err.name === 'AbortError') return;
        console.error(err);
        setError(err.message);
        setIsLoading(false);
      });
      
    return () => controller.abort();
  }, []);

  const [formData, setFormData] = useState({
    name: '',
    diagnosis: '',
    doctor: '',
    assignedNurse: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!bedId) return;
    admitPatient({ ...formData, bedId });
    onClose();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-zinc-900/40 backdrop-blur-sm p-4">
      <div className="bg-white border border-zinc-200 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden">
        
        <div className="flex items-center justify-between p-5 border-b border-zinc-200 bg-white/90">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600">
              <UserPlus className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-zinc-900">Bemor Qabul Qilish</h2>
          </div>
          <button onClick={onClose} className="p-2 text-zinc-500 hover:text-zinc-900 bg-zinc-100 hover:bg-red-100 hover:text-red-600 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-zinc-600 mb-1">F.I.Sh.</label>
            <input 
              type="text" 
              id="name" 
              name="name" 
              required
              value={formData.name}
              onChange={handleChange}
              className="w-full bg-white border border-zinc-300 rounded-lg px-4 py-2.5 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
              placeholder="Masalan: Karimov A.B."
            />
          </div>
          
          <div className="rounded-xl border border-emerald-200 bg-emerald-50/40 p-4">
            <p className="text-sm font-medium text-emerald-900 mb-3">Joylashuv</p>
            <LocationCascadeSelects
              departments={departments}
              rooms={rooms}
              beds={beds}
              departmentId={departmentId}
              roomId={roomId}
              bedId={bedId}
              onDepartmentChange={setDepartmentId}
              onRoomChange={setRoomId}
              onBedChange={setBedId}
              disabled={isLoading || !!error}
              bedRequired
              emphasize
            />
            <p className="mt-2 text-xs text-zinc-600">
              Monitor vitallari: shu karavatga qurilma ham biriktirilgan bo&apos;lsin (Sozlamalar → Qurilmalar).
            </p>
          </div>

          <div>
            <label htmlFor="diagnosis" className="block text-sm font-medium text-zinc-600 mb-1">Tashxis</label>
            <input 
              type="text" 
              id="diagnosis" 
              name="diagnosis" 
              required
              value={formData.diagnosis}
              onChange={handleChange}
              className="w-full bg-white border border-zinc-300 rounded-lg px-4 py-2.5 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
              placeholder="Asosiy tashxis"
            />
          </div>

          <div>
            <label htmlFor="doctor" className="block text-sm font-medium text-zinc-600 mb-1">Mas'ul Shifokor</label>
            <input 
              type="text" 
              id="doctor" 
              name="doctor" 
              required
              value={formData.doctor}
              onChange={handleChange}
              className="w-full bg-white border border-zinc-300 rounded-lg px-4 py-2.5 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
              placeholder="Shifokor F.I.Sh."
            />
          </div>

          <div>
            <label htmlFor="assignedNurse" className="block text-sm font-medium text-zinc-600 mb-1">Mas'ul Hamshira</label>
            <input 
              type="text" 
              id="assignedNurse" 
              name="assignedNurse" 
              required
              value={formData.assignedNurse}
              onChange={handleChange}
              className="w-full bg-white border border-zinc-300 rounded-lg px-4 py-2.5 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
              placeholder="Hamshira F.I.Sh."
            />
          </div>

          <div className="pt-4 flex justify-end space-x-3">
            <button 
              type="button" 
              onClick={onClose}
              className="px-5 py-2.5 rounded-lg text-sm font-medium text-zinc-700 bg-zinc-100 hover:bg-zinc-200 transition-colors"
            >
              Bekor qilish
            </button>
            <button 
              type="submit"
              className="px-5 py-2.5 rounded-lg text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-500 transition-colors shadow-lg shadow-emerald-500/20"
            >
              Qabul qilish
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
