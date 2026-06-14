import { useRef } from 'react';
import { useStore } from '../../store/useStore';
import styles from './MenuBar.module.css';

export default function MenuBar() {
  const fileName = useStore((s) => s.fileName);
  const dslText = useStore((s) => s.dslText);
  const isDirty = useStore((s) => s.isDirty);
  const compileStatus = useStore((s) => s.compileStatus);
  const loadFile = useStore((s) => s.loadFile);
  const newProject = useStore((s) => s.newProject);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleSave() {
    const blob = new Blob([dslText], { type: 'text/yaml' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = fileName ?? 'cabinet.yaml';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function handleOpen() {
    fileInputRef.current?.click();
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => loadFile(file.name, ev.target?.result as string);
    reader.readAsText(file);
    e.target.value = '';
  }

  const statusLabel =
    compileStatus === 'compiling'
      ? 'Compiling…'
      : compileStatus === 'ok'
        ? 'OK'
        : compileStatus === 'error'
          ? 'Error'
          : '';

  const statusClass =
    compileStatus === 'ok'
      ? styles.ok
      : compileStatus === 'error'
        ? styles.err
        : styles.dim;

  return (
    <div className={styles.bar}>
      <span className={styles.brand}>Cabinet</span>
      <div className={styles.sep} />
      <button className="ghost" onClick={newProject}>
        New
      </button>
      <button className="ghost" onClick={handleOpen}>
        Open
      </button>
      <button className="ghost" onClick={handleSave}>
        Save{isDirty ? ' *' : ''}
      </button>
      <div className={styles.spacer} />
      <span className={styles.filename}>{fileName}</span>
      {statusLabel && <span className={`${styles.status} ${statusClass}`}>{statusLabel}</span>}
      <input
        ref={fileInputRef}
        type="file"
        accept=".yaml,.yml"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
    </div>
  );
}
