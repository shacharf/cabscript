import MenuBar from './MenuBar';
import DslEditor from '../DslEditor/DslEditor';
import Viewer from '../Viewer/Viewer';
import PropertiesPanel from '../PropertiesPanel/PropertiesPanel';
import Inspector from '../Inspector/Inspector';
import styles from './AppShell.module.css';

export default function AppShell() {
  return (
    <div className={styles.shell}>
      <MenuBar />
      <div className={styles.workspace}>
        <div className={styles.left}>
          <DslEditor />
        </div>
        <div className={styles.center}>
          <Viewer />
        </div>
        <div className={styles.right}>
          <PropertiesPanel />
        </div>
      </div>
      <div className={styles.bottom}>
        <Inspector />
      </div>
    </div>
  );
}
