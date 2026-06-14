import { useState } from 'react';
import WarningsTable from './WarningsTable';
import CutlistTable from './CutlistTable';
import { useStore } from '../../store/useStore';
import styles from './Inspector.module.css';

type Tab = 'warnings' | 'cutlist';

export default function Inspector() {
  const [activeTab, setActiveTab] = useState<Tab>('warnings');
  const warnings = useStore((s) => s.warnings);
  const errors = warnings.filter((w) => w.severity === 'error').length;
  const warns = warnings.filter((w) => w.severity === 'warning').length;

  return (
    <div className={styles.inspector}>
      <div className={styles.tabs}>
        <button
          className={`ghost${activeTab === 'warnings' ? ' active' : ''}`}
          onClick={() => setActiveTab('warnings')}
        >
          Messages
          {errors > 0 && <span className={styles.badge} style={{ background: 'var(--error)' }}>{errors}</span>}
          {warns > 0 && <span className={styles.badge} style={{ background: 'var(--warn)', color: '#111' }}>{warns}</span>}
        </button>
        <button
          className={`ghost${activeTab === 'cutlist' ? ' active' : ''}`}
          onClick={() => setActiveTab('cutlist')}
        >
          Cut List
        </button>
      </div>
      <div className={styles.content}>
        {activeTab === 'warnings' && <WarningsTable />}
        {activeTab === 'cutlist' && <CutlistTable />}
      </div>
    </div>
  );
}
