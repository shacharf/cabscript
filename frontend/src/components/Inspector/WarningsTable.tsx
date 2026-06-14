import { useStore } from '../../store/useStore';
import styles from './Table.module.css';

const COLOR: Record<string, string> = {
  error: 'var(--error)',
  warning: 'var(--warn)',
  info: 'var(--info)',
};

export default function WarningsTable() {
  const warnings = useStore((s) => s.warnings);
  const compileError = useStore((s) => s.compileError);

  if (warnings.length === 0 && !compileError) {
    return <div className={styles.empty}>No messages</div>;
  }

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Severity</th>
          <th>Code</th>
          <th>Message</th>
        </tr>
      </thead>
      <tbody>
        {warnings.map((w, i) => (
          <tr key={i}>
            <td style={{ color: COLOR[w.severity] ?? 'inherit', fontWeight: 600 }}>{w.severity}</td>
            <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>{w.code}</td>
            <td>{w.message}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
