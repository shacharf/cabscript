import { useEffect, useRef } from 'react';
import type { ExportSettings } from '../../store/useSettings';
import styles from './SettingsPopover.module.css';

interface Props {
  settings: ExportSettings;
  onChange: (patch: Partial<ExportSettings>) => void;
  onClose: () => void;
}

export default function SettingsPopover({ settings, onChange, onClose }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [onClose]);

  return (
    <div className={styles.popover} ref={ref}>
      <div className={styles.title}>Export settings</div>
      <label className={styles.row}>
        <input
          type="checkbox"
          checked={settings.ignore_grain}
          onChange={(e) => onChange({ ignore_grain: e.target.checked })}
        />
        <span>
          <strong>Ignore grain direction</strong>
          <small>Allow parts to rotate freely for a tighter cut plan. Parts may end up cross-grain.</small>
        </span>
      </label>
      <label className={styles.row}>
        <input
          type="checkbox"
          checked={settings.dims_from_floor}
          onChange={(e) => onChange({ dims_from_floor: e.target.checked })}
        />
        <span>
          <strong>Dimensions from floor</strong>
          <small>Show cumulative heights from the floor on the left side of the 2D view.</small>
        </span>
      </label>
    </div>
  );
}
