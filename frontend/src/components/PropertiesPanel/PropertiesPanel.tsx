import GlobalProperties from './GlobalProperties';
import SelectedProperties from './SelectedProperties';
import ColorPalette from '../ColorPalette/ColorPalette';
import styles from './PropertiesPanel.module.css';

export default function PropertiesPanel() {
  return (
    <div className={styles.panel}>
      <div className={styles.section}>
        <GlobalProperties />
      </div>
      <div className={styles.divider} />
      <div className={styles.section}>
        <ColorPalette />
      </div>
      <div className={styles.divider} />
      <div className={styles.section}>
        <SelectedProperties />
      </div>
    </div>
  );
}
