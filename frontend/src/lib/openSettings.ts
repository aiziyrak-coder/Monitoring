export type ClinicSettingsTab = 'structure' | 'devices' | 'patients' | 'integration';

export const CLINIC_OPEN_SETTINGS_EVENT = 'clinic-open-settings';

/** Sozlamalar oynasini ochadi (Dashboard tinglovchisi). */
export function openClinicSettings(tab: ClinicSettingsTab) {
  window.dispatchEvent(
    new CustomEvent(CLINIC_OPEN_SETTINGS_EVENT, { detail: { tab } })
  );
}
