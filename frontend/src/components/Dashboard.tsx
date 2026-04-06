import { useEffect, useState, memo, useMemo } from 'react';
import { useStore } from '../store';
import { PatientMonitor } from './PatientMonitor';
import { Activity, Settings, Users, Eye, EyeOff, Search, UserPlus, Volume2, VolumeX, Wifi, WifiOff, Pin } from 'lucide-react';
import { format } from 'date-fns';
import { PatientDetailsModal } from './PatientDetailsModal';
import { AdmitPatientModal } from './AdmitPatientModal';
import { useAudioAlarm } from '../hooks/useAudioAlarm';
import { SettingsModal } from './SettingsModal';
import {
  CLINIC_OPEN_SETTINGS_EVENT,
  type ClinicSettingsTab,
} from '../lib/openSettings';

const Clock = memo(() => {
  const [currentTime, setCurrentTime] = useState(new Date());
  
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex flex-col items-end justify-center">
      <span className="text-sm font-bold text-zinc-950">{format(currentTime, 'HH:mm:ss')}</span>
      <span className="text-xs font-mono text-zinc-800">{format(currentTime, 'dd MMM yyyy')}</span>
    </div>
  );
});

export function Dashboard() {
  useAudioAlarm(); // Initialize audio alarms

  const { patients, socket, connect, disconnect, privacyMode, togglePrivacyMode, searchQuery, setSearchQuery, isAudioMuted, toggleAudioMute } = useStore();
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'pinned'>('all');
  const [departmentFilter, setDepartmentFilter] = useState<'all' | 'reanimatsiya' | 'palata'>('all');
  const [isConnected, setIsConnected] = useState(false);
  const [isAdmitModalOpen, setIsAdmitModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [settingsInitialTab, setSettingsInitialTab] =
    useState<ClinicSettingsTab>('structure');

  useEffect(() => {
    const onOpenSettings = (e: Event) => {
      const t = (e as CustomEvent<{ tab?: ClinicSettingsTab }>).detail?.tab;
      if (t) setSettingsInitialTab(t);
      setIsSettingsModalOpen(true);
    };
    window.addEventListener(CLINIC_OPEN_SETTINGS_EVENT, onOpenSettings);
    return () => window.removeEventListener(CLINIC_OPEN_SETTINGS_EVENT, onOpenSettings);
  }, []);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  const patientList = useMemo(() => Object.values(patients), [patients]);

  useEffect(() => {
    if (socket) {
      const onConnect = () => setIsConnected(true);
      const onDisconnect = () => setIsConnected(false);
      
      socket.on('connect', onConnect);
      socket.on('disconnect', onDisconnect);
      setIsConnected(socket.connected);

      return () => {
        socket.off('connect', onConnect);
        socket.off('disconnect', onDisconnect);
      };
    }
  }, [socket]);

  const filteredPatients = useMemo(() => {
    const filtered = patientList.filter(p => {
      // Search filter
      if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase()) && !p.id.toLowerCase().includes(searchQuery.toLowerCase())) return false;

      // Severity filter
      if (filter === 'critical' && p.alarm.level !== 'red') return false;
      if (filter === 'warning' && p.alarm.level !== 'yellow' && p.alarm.level !== 'blue' && p.alarm.level !== 'purple') return false;
      if (filter === 'pinned' && !p.isPinned) return false;
      
      // Department filter
      if (departmentFilter === 'reanimatsiya' && !p.room.toLowerCase().includes('reanimatsiya')) return false;
      if (departmentFilter === 'palata' && !p.room.toLowerCase().includes('palata')) return false;

      return true;
    });

    return filtered.sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      return 0;
    });
  }, [patientList, searchQuery, filter, departmentFilter]);

  const criticalCount = useMemo(() => patientList.filter(p => p.alarm.level === 'red').length, [patientList]);
  const warningCount = useMemo(() => patientList.filter(p => p.alarm.level === 'yellow' || p.alarm.level === 'blue' || p.alarm.level === 'purple').length, [patientList]);
  const pinnedCount = useMemo(() => patientList.filter(p => p.isPinned).length, [patientList]);

  return (
    <div className="min-h-screen text-zinc-800 font-sans selection:bg-emerald-500/30 relative bg-zinc-50">
      {/* Background Image with Light Overlay */}
      <div className="fixed inset-0 z-0">
        <img 
          src="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?q=80&w=2053&auto=format&fit=crop" 
          alt="Clinic Background" 
          className="w-full h-full object-cover opacity-20"
          referrerPolicy="no-referrer"
        />
        <div className="absolute inset-0 bg-white/80 backdrop-blur-[2px]"></div>
      </div>

      {/* Content Wrapper */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Top Navigation Bar */}
        <header className="sticky top-0 z-40 flex items-center justify-between px-6 py-4 bg-white/90 border-b border-zinc-200 backdrop-blur-md shadow-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
              <Activity className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-zinc-900 tracking-tight">ClinicMonitoring</h1>
              <div className="flex items-center space-x-2">
                <p className="text-xs text-zinc-500 font-mono uppercase tracking-wider">Farg'ona jamoat salomatlik instituti</p>
                <div className={`flex items-center text-[10px] px-1.5 py-0.5 rounded-full border ${isConnected ? 'bg-emerald-100 text-emerald-700 border-emerald-200' : 'bg-red-100 text-red-700 border-red-200'}`}>
                  {isConnected ? <Wifi className="w-3 h-3 mr-1" /> : <WifiOff className="w-3 h-3 mr-1" />}
                  {isConnected ? 'Online' : 'Offline'}
                </div>
              </div>
            </div>
          </div>

        <div className="flex items-center space-x-6">
          {/* Search */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-zinc-400" />
            </div>
            <input
              type="text"
              placeholder="Bemor qidirish..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-zinc-100 border border-zinc-300 text-zinc-800 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block w-48 pl-10 p-2 outline-none transition-all focus:w-64"
            />
          </div>

          <div className="h-6 w-px bg-zinc-300" />

          {/* Status Indicators */}
          <div className="flex space-x-2">
            <button 
              onClick={() => setFilter('all')}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter === 'all' ? 'bg-zinc-800 text-white' : 'text-zinc-600 hover:text-zinc-900 bg-zinc-100'}`}
            >
              Barchasi ({patientList.length})
            </button>
            <button 
              onClick={() => setFilter('critical')}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors flex items-center ${filter === 'critical' ? 'bg-red-100 text-red-700 border border-red-200' : 'text-zinc-600 hover:text-red-600 bg-zinc-100'}`}
            >
              <span className="w-2 h-2 rounded-full bg-red-500 mr-2 animate-pulse" />
              Kritik ({criticalCount})
            </button>
            <button 
              onClick={() => setFilter('warning')}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors flex items-center ${filter === 'warning' ? 'bg-yellow-100 text-yellow-700 border border-yellow-200' : 'text-zinc-600 hover:text-yellow-600 bg-zinc-100'}`}
            >
              <span className="w-2 h-2 rounded-full bg-yellow-500 mr-2" />
              Ogohlantirish ({warningCount})
            </button>
            <button 
              onClick={() => setFilter('pinned')}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors flex items-center ${filter === 'pinned' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' : 'text-zinc-600 hover:text-emerald-600 bg-zinc-100'}`}
            >
              <Pin className="w-3 h-3 mr-2" />
              Qadalgan ({pinnedCount})
            </button>
          </div>

          <div className="h-6 w-px bg-zinc-300" />

          {/* Department Filter */}
          <select 
            value={departmentFilter} 
            onChange={(e) => setDepartmentFilter(e.target.value as 'all' | 'reanimatsiya' | 'palata')}
            className="bg-zinc-100 border border-zinc-300 text-zinc-800 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2 outline-none"
          >
            <option value="all">Barcha bo'limlar</option>
            <option value="reanimatsiya">Reanimatsiya</option>
            <option value="palata">Umumiy palatalar</option>
          </select>

          <div className="h-6 w-px bg-zinc-300" />

          <div className="flex items-center space-x-4 text-zinc-600">
            <div className="flex items-center mr-2">
              <span className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-emerald-500' : 'bg-red-500'}`} />
              <span className="text-xs font-mono">{isConnected ? 'ONLAYN' : 'OFLAYN'}</span>
            </div>
            <Clock />

            <button 
              onClick={() => setIsAdmitModalOpen(true)}
              className="p-2 rounded-full hover:bg-emerald-100 hover:text-emerald-600 transition-colors" 
              title="Yangi bemor qabul qilish"
            >
              <UserPlus className="w-5 h-5" />
            </button>
            <button 
              onClick={toggleAudioMute} 
              className="p-2 rounded-full hover:bg-zinc-200 transition-colors" 
              title={isAudioMuted ? "Ovozni yoqish" : "Ovozni o'chirish"}
            >
              {isAudioMuted ? <VolumeX className="w-5 h-5 text-red-500" /> : <Volume2 className="w-5 h-5 text-emerald-600" />}
            </button>
            <button 
              onClick={togglePrivacyMode} 
              className="p-2 rounded-full hover:bg-zinc-200 transition-colors" 
              title="Maxfiylik rejimi"
            >
              {privacyMode ? <EyeOff className="w-5 h-5 text-emerald-600" /> : <Eye className="w-5 h-5" />}
            </button>
            <button 
              onClick={() => {
                setSettingsInitialTab('structure');
                setIsSettingsModalOpen(true);
              }}
              className="p-2 rounded-full hover:bg-zinc-200 transition-colors" 
              title="Sozlamalar"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Grid */}
      <main className="p-6 flex-1">
        {patientList.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-[60vh] text-zinc-500">
            <Activity className="w-12 h-12 mb-4 animate-pulse opacity-50" />
            <p className="text-lg font-medium">Telemetriya serveriga ulanmoqda...</p>
            <p className="text-sm font-mono mt-2">Ma'lumotlar oqimi kutilmoqda</p>
          </div>
        ) : filteredPatients.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-[60vh] text-zinc-500">
            <Users className="w-12 h-12 mb-4 opacity-50" />
            <p className="text-lg font-medium">Joriy filtrga mos bemorlar topilmadi.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[...filteredPatients].sort((a, b) => {
              if (a.isPinned !== b.isPinned) {
                return a.isPinned ? -1 : 1;
              }
              return a.room.localeCompare(b.room);
            }).map(patient => (
              <PatientMonitor key={patient.id} patient={patient} size="large" />
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-3 px-6 border-t border-zinc-200 bg-white/90 backdrop-blur-md flex flex-col items-center justify-center text-center gap-1 text-[11px] text-zinc-500 z-40 shrink-0">
        <span>&copy; {new Date().getFullYear()} ClinicMonitoring. Barcha huquqlar himoyalangan.</span>
        <span className="text-zinc-700 font-medium text-xs sm:text-[11px]">
          Muallif: Farg&apos;ona Jamoat Salomatlik Tibbiyot Instituti
        </span>
      </footer>
      </div>

      {/* Modals */}
      <PatientDetailsModal />
      {isAdmitModalOpen && <AdmitPatientModal onClose={() => setIsAdmitModalOpen(false)} />}
      {isSettingsModalOpen && (
        <SettingsModal
          initialTab={settingsInitialTab}
          onClose={() => {
            setIsSettingsModalOpen(false);
            setSettingsInitialTab('structure');
          }}
        />
      )}
    </div>
  );
}
