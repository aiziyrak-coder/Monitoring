/**
 * REST so'rovlar bazaviy URL.
 * Bo'sh bo'lsa — joriy origin (Vite devda proxy orqali Django).
 * Production: VITE_API_ORIGIN=https://api.kasalxona.uz
 */
const RAW = (import.meta.env.VITE_API_ORIGIN as string | undefined)?.trim() ?? '';

export function apiUrl(path: string): string {
  if (!path.startsWith('/')) {
    path = `/${path}`;
  }
  if (!RAW) {
    return path;
  }
  return `${RAW.replace(/\/$/, '')}${path}`;
}

export function socketIoUrl(): string {
  if (RAW) {
    return RAW.replace(/\/$/, '');
  }
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return '';
}
