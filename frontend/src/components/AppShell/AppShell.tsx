import { useState, useEffect } from 'react';
import MenuBar from './MenuBar';
import DslEditor from '../DslEditor/DslEditor';
import Viewer from '../Viewer/Viewer';
import PropertiesPanel from '../PropertiesPanel/PropertiesPanel';
import Inspector from '../Inspector/Inspector';
import styles from './AppShell.module.css';

const MIN_LEFT = 220;
const MAX_LEFT = 600;
const MIN_RIGHT = 180;
const MAX_RIGHT = 480;

function readWidth(key: string, fallback: number): number {
  const v = localStorage.getItem(key);
  return v ? parseInt(v, 10) : fallback;
}

export default function AppShell() {
  const [leftWidth, setLeftWidth] = useState(() => readWidth('cabinet-left-width', 380));
  const [rightWidth, setRightWidth] = useState(() => readWidth('cabinet-right-width', 280));

  useEffect(() => { localStorage.setItem('cabinet-left-width', String(leftWidth)); }, [leftWidth]);
  useEffect(() => { localStorage.setItem('cabinet-right-width', String(rightWidth)); }, [rightWidth]);

  function startResizeLeft(e: React.MouseEvent) {
    e.preventDefault();
    const startX = e.clientX;
    const startW = leftWidth;
    function onMove(ev: MouseEvent) {
      setLeftWidth(Math.max(MIN_LEFT, Math.min(MAX_LEFT, startW + ev.clientX - startX)));
    }
    function onUp() {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  function startResizeRight(e: React.MouseEvent) {
    e.preventDefault();
    const startX = e.clientX;
    const startW = rightWidth;
    function onMove(ev: MouseEvent) {
      setRightWidth(Math.max(MIN_RIGHT, Math.min(MAX_RIGHT, startW - (ev.clientX - startX))));
    }
    function onUp() {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  return (
    <div className={styles.shell}>
      <MenuBar />
      <div className={styles.workspace}>
        <div className={styles.left} style={{ width: leftWidth }}>
          <DslEditor />
        </div>
        <div className={styles.resizeHandle} onMouseDown={startResizeLeft} />
        <div className={styles.center}>
          <Viewer />
        </div>
        <div className={styles.resizeHandle} onMouseDown={startResizeRight} />
        <div className={styles.right} style={{ width: rightWidth }}>
          <PropertiesPanel />
        </div>
      </div>
      <div className={styles.bottom}>
        <Inspector />
      </div>
    </div>
  );
}
