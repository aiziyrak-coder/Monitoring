/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_ORIGIN?: string;
  /** Vergul bilan: birinchi ishlaydigan API tanlanadi (bulut + mahalliy tartib) */
  readonly VITE_API_ORIGINS?: string;
  /** Bulutdan keyin sinab ko'riladigan mahalliy / zaxira manzillar */
  readonly VITE_API_FALLBACK_ORIGINS?: string;
  /** Masalan: 192.168.1.10:6006 — bo'sh bo'lsa hostname:6006 */
  readonly VITE_HL7_HOST_PORT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
