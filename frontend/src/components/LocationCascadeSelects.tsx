import { useMemo } from 'react';

/** Mavjud bedId dan ketma-ket tanlovlar boshlang‘ich qiymatlari. */
export function cascadeFromBedId(
  bedId: string | null | undefined,
  beds: any[],
  rooms: any[]
): { departmentId: string; roomId: string; bedId: string } {
  if (!bedId) return { departmentId: '', roomId: '', bedId: '' };
  const bed = beds.find((b) => b.id === bedId);
  if (!bed) return { departmentId: '', roomId: '', bedId: bedId };
  const room = rooms.find((r) => r.id === bed.roomId);
  if (!room) return { departmentId: '', roomId: '', bedId: bedId };
  return {
    departmentId: room.departmentId || '',
    roomId: room.id,
    bedId: bed.id,
  };
}

const selectClass =
  'w-full bg-white border border-zinc-300 rounded-lg px-3 py-2.5 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed';

type Props = {
  departments: any[];
  rooms: any[];
  beds: any[];
  departmentId: string;
  roomId: string;
  bedId: string;
  onDepartmentChange: (id: string) => void;
  onRoomChange: (id: string) => void;
  onBedChange: (id: string) => void;
  disabled?: boolean;
  /** Karavat majburiy bo‘lsa (bemor qabul) */
  bedRequired?: boolean;
  /** Yashil urg‘u (qurilma oynasi) */
  emphasize?: boolean;
};

export function LocationCascadeSelects({
  departments,
  rooms,
  beds,
  departmentId,
  roomId,
  bedId,
  onDepartmentChange,
  onRoomChange,
  onBedChange,
  disabled = false,
  bedRequired = false,
  emphasize = false,
}: Props) {
  const roomsInDept = useMemo(
    () => rooms.filter((r) => r.departmentId === departmentId),
    [rooms, departmentId]
  );
  const bedsInRoom = useMemo(
    () => beds.filter((b) => b.roomId === roomId),
    [beds, roomId]
  );

  const wrapClass = emphasize
    ? 'space-y-3 rounded-xl border-2 border-emerald-200 bg-white p-3'
    : 'space-y-3';

  const sel = emphasize
    ? `${selectClass} border-emerald-200`
    : selectClass;

  return (
    <div className={wrapClass}>
      <div>
        <label htmlFor="loc-dept" className="block text-sm font-medium text-zinc-700 mb-1">
          Bo‘lim
        </label>
        <select
          id="loc-dept"
          value={departmentId}
          disabled={disabled || departments.length === 0}
          className={sel}
          required={bedRequired}
          onChange={(e) => {
            const v = e.target.value;
            onDepartmentChange(v);
            onRoomChange('');
            onBedChange('');
          }}
        >
          <option value="">
            {departments.length === 0 ? 'Avval tuzilma yarating' : 'Bo‘limni tanlang...'}
          </option>
          {departments.map((d: any) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="loc-room" className="block text-sm font-medium text-zinc-700 mb-1">
          Palata (xona)
        </label>
        <select
          id="loc-room"
          value={roomId}
          disabled={disabled || !departmentId}
          className={sel}
          required={bedRequired}
          onChange={(e) => {
            const v = e.target.value;
            onRoomChange(v);
            onBedChange('');
          }}
        >
          <option value="">{departmentId ? 'Palatani tanlang...' : 'Avval bo‘limni tanlang'}</option>
          {roomsInDept.map((r: any) => (
            <option key={r.id} value={r.id}>
              {r.name}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="loc-bed" className="block text-sm font-medium text-zinc-700 mb-1">
          Karavat (joy)
        </label>
        <select
          id="loc-bed"
          value={bedId}
          disabled={disabled || !roomId}
          className={sel}
          required={bedRequired}
          onChange={(e) => onBedChange(e.target.value)}
        >
          <option value="">{roomId ? 'Karavatni tanlang...' : 'Avval palatani tanlang'}</option>
          {bedsInRoom.map((b: any) => (
            <option key={b.id} value={b.id}>
              {b.name} ({b.id})
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
