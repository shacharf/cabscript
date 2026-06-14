import { useRef } from 'react';
import { useStore } from '../../store/useStore';
import styles from './StartScreen.module.css';

export default function StartScreen() {
  const newProject = useStore((s) => s.newProject);
  const loadFile = useStore((s) => s.loadFile);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleOpen() {
    fileInputRef.current?.click();
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      loadFile(file.name, text);
    };
    reader.readAsText(file);
    e.target.value = '';
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.logo}>⬛</div>
        <h1 className={styles.title}>Cabinet Designer</h1>
        <p className={styles.subtitle}>Design and visualise custom cabinetry</p>
        <div className={styles.actions}>
          <button className={styles.primary} onClick={newProject}>
            New Project
          </button>
          <button className={styles.secondary} onClick={handleOpen}>
            Open Project…
          </button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".yaml,.yml"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </div>
    </div>
  );
}
