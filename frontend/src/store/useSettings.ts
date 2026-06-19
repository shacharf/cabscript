import { useState, useCallback } from 'react';

export interface ExportSettings {
  ignore_grain: boolean;
}

const KEY = 'cabinet-export-settings';

function load(): ExportSettings {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { ignore_grain: false, ...JSON.parse(raw) };
  } catch {}
  return { ignore_grain: false };
}

function save(s: ExportSettings) {
  localStorage.setItem(KEY, JSON.stringify(s));
}

export function useSettings() {
  const [settings, setSettingsState] = useState<ExportSettings>(load);

  const setSettings = useCallback((patch: Partial<ExportSettings>) => {
    setSettingsState((prev) => {
      const next = { ...prev, ...patch };
      save(next);
      return next;
    });
  }, []);

  return { settings, setSettings };
}
