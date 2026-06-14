import { useStore } from '../../store/useStore';
import View2d from './View2d';
import View3d from './View3d';
import styles from './Viewer.module.css';

export default function Viewer() {
  const activeView = useStore((s) => s.activeView);
  const doorsVisible = useStore((s) => s.doorsVisible);
  const setActiveView = useStore((s) => s.setActiveView);
  const toggleDoors = useStore((s) => s.toggleDoors);
  const render3d = useStore((s) => s.render3d);

  function handleSwitch(v: '2d' | '3d') {
    setActiveView(v);
    if (v === '3d') {
      render3d();
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.tabs}>
        <button
          className={`ghost${activeView === '2d' ? ' active' : ''}`}
          onClick={() => handleSwitch('2d')}
        >
          Front View
        </button>
        <button
          className={`ghost${activeView === '3d' ? ' active' : ''}`}
          onClick={() => handleSwitch('3d')}
        >
          3D
        </button>
        <div className={styles.tabSpacer} />
        <button className={`ghost${!doorsVisible ? ` ${styles.doorsHidden}` : ''}`} onClick={toggleDoors}>
          {doorsVisible ? 'Hide Doors' : 'Show Doors'}
        </button>
      </div>
      <div className={styles.viewport}>
        <div style={{ display: activeView === '2d' ? 'contents' : 'none' }}>
          <View2d />
        </div>
        <div style={{ display: activeView === '3d' ? 'contents' : 'none' }}>
          <View3d />
        </div>
      </div>
    </div>
  );
}
