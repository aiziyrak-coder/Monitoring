/**
 * REST va Socket.IO uchun API bazaviy manzil.
 *
 * - Bo'sh (relative): joriy sahifa origin — production Nginx yoki Vite proxy.
 * - VITE_API_ORIGINS: vergul bilan tartib (birinchi ishlayotgani tanlanadi).
 * - Aks holda: VITE_API_ORIGIN → VITE_API_FALLBACK_ORIGINS → joriy origin → :8010 / :8000.
 * Muvaffaqiyatli manzil localStorage da saqlanadi; keyingi safar tezroq ulanish.
 */

const STORAGE_KEY = 'clinicmonitoring_api_origin';

function parseCommaEnv(v: string | undefined): string[] {
  if (!v) return [];
  return v
    .split(',')
    .map((s) => s.trim().replace(/\/$/, ''))
    .filter(Boolean);
}

const ENV_ORDER = parseCommaEnv(import.meta.env.VITE_API_ORIGINS as string | undefined);
const ENV_PRIMARY = ((import.meta.env.VITE_API_ORIGIN as string | undefined) ?? '').trim().replace(/\/$/, '');
const ENV_FALLBACKS = parseCommaEnv(import.meta.env.VITE_API_FALLBACK_ORIGINS as string | undefined);

/** '' = relative (joriy origin orqali /api) */
let activeApiBase = '';

export function getActiveApiBase(): string {
  return activeApiBase;
}

/** Tashqi to'g'ridan-to'g'ri API ishlatilayotgan bo'lsa (CORS), to'liq origin; aks holda bo'sh. */
export function configureApiBase(origin: string): void {
  activeApiBase = (origin || '').trim().replace(/\/$/, '');
}

function dedupe(urls: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const u of urls) {
    const n = u.trim().replace(/\/$/, '');
    if (!n || seen.has(n)) continue;
    seen.add(n);
    out.push(n);
  }
  return out;
}

function buildCandidateOrigins(): string[] {
  if (ENV_ORDER.length > 0) {
    return dedupe(ENV_ORDER);
  }

  const out: string[] = [];

  if (ENV_PRIMARY) out.push(ENV_PRIMARY);
  out.push(...ENV_FALLBACKS);

  if (typeof window !== 'undefined') {
    const { protocol, hostname, port, origin } = window.location;
    out.push(origin);

    const devPorts = new Set(['5173', '4173', '3000']);
    const hostPort = window.location.host.includes(':')
      ? window.location.host.split(':')[1]
      : '';
    if (devPorts.has(port) || devPorts.has(hostPort)) {
      out.push(`${protocol}//${hostname}:8010`);
      out.push(`${protocol}//${hostname}:8000`);
    }
  }

  try {
    const saved = typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null;
    if (saved) out.push(saved.trim().replace(/\/$/, ''));
  } catch {
    /* private mode */
  }

  return dedupe(out.filter(Boolean));
}

function healthUrlForOrigin(origin: string): string {
  const o = origin.replace(/\/$/, '');
  return `${o}/api/health`;
}

async function fetchWithTimeout(url: string, ms: number): Promise<Response> {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), ms);
  try {
    return await fetch(url, { method: 'GET', signal: ac.signal, cache: 'no-store' });
  } finally {
    clearTimeout(t);
  }
}

/**
 * Birinchi javob beradigan API origin ni tanlaydi.
 * @param forceNew - true bo'lsa localStorage dagi saqlangan tartibni e'tiborsiz qoldirmaymiz, lekin qayta sinaymiz.
 */
export async function selectBestApiOrigin(forceNew = false): Promise<string> {
  let candidates = buildCandidateOrigins();
  if (forceNew && ENV_ORDER.length === 0) {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* */
    }
    candidates = buildCandidateOrigins();
  }

  if (candidates.length === 0) {
    configureApiBase('');
    return typeof window !== 'undefined' ? window.location.origin : '';
  }

  for (const origin of candidates) {
    try {
      const url = healthUrlForOrigin(origin);
      const r = await fetchWithTimeout(url, 4500);
      if (r.ok) {
        const same =
          typeof window !== 'undefined' && origin.replace(/\/$/, '') === window.location.origin;
        configureApiBase(same ? '' : origin);
        try {
          localStorage.setItem(STORAGE_KEY, origin);
        } catch {
          /* */
        }
        return origin;
      }
    } catch {
      /* keyingi */
    }
  }

  configureApiBase('');
  return typeof window !== 'undefined' ? window.location.origin : '';
}

export function apiUrl(path: string): string {
  if (!path.startsWith('/')) {
    path = `/${path}`;
  }
  if (!activeApiBase) {
    return path;
  }
  return `${activeApiBase}${path}`;
}

export function socketIoUrl(): string {
  if (activeApiBase) {
    return activeApiBase;
  }
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return '';
}

/** UI: qisqa tavsif */
export function getApiConnectivityLabel(): string {
  if (!activeApiBase) {
    return typeof window !== 'undefined' && ['5173', '4173', '3000'].includes(window.location.port)
      ? 'Mahalliy (proxy)'
      : 'Mahalliy / bir xil server';
  }
  try {
    const u = new URL(activeApiBase);
    return `API: ${u.hostname}${u.port ? `:${u.port}` : ''}`;
  } catch {
    return 'API: maxsus';
  }
}

/** Mindray HL7 server IP:port — monitor «Интернет» menyusida ko'rsatish uchun. */
export function hl7ServerDisplay(): string {
  const explicit = (import.meta.env.VITE_HL7_HOST_PORT as string | undefined)?.trim();
  if (explicit) return explicit;
  if (activeApiBase) {
    try {
      return `${new URL(activeApiBase).hostname}:6006`;
    } catch {
      return 'server-host:6006';
    }
  }
  if (typeof window !== 'undefined') {
    return `${window.location.hostname}:6006`;
  }
  return 'server-IP:6006';
}
