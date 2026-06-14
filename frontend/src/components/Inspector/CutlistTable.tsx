import { useStore } from '../../store/useStore';
import styles from './Table.module.css';

export default function CutlistTable() {
  const cutlist = useStore((s) => s.cutlist);

  if (cutlist.length === 0) {
    return <div className={styles.empty}>Compile a design to see the cut list</div>;
  }

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Qty</th>
          <th>Name</th>
          <th>L × W × T (mm)</th>
          <th>Material</th>
          <th>Grain</th>
        </tr>
      </thead>
      <tbody>
        {cutlist.map((item, i) => (
          <tr key={i}>
            <td>{item.quantity}</td>
            <td>{item.name}</td>
            <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>
              {Math.round(item.length)} × {Math.round(item.width)} × {Math.round(item.thickness)}
            </td>
            <td>{item.material}</td>
            <td>{item.grain_direction}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
