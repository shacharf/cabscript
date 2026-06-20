import { useRef, useState } from 'react';
import { useStore } from '../../store/useStore';
import { apiExportZip } from '../../api/client';
import { useSettings } from '../../store/useSettings';
import SettingsPopover from './SettingsPopover';
import styles from './MenuBar.module.css';

export default function MenuBar() {
  const fileName = useStore((s) => s.fileName);
  const dslText = useStore((s) => s.dslText);
  const isDirty = useStore((s) => s.isDirty);
  const compileStatus = useStore((s) => s.compileStatus);
  const version = useStore((s) => s.version);
  const loadFile = useStore((s) => s.loadFile);
  const newProject = useStore((s) => s.newProject);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [exporting, setExporting] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const { settings, setSettings } = useSettings();
  const settingsBtnRef = useRef<HTMLDivElement>(null);

  function handleSave() {
    const blob = new Blob([dslText], { type: 'text/yaml' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = fileName ?? 'cabinet.yaml';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  async function handleExport() {
    setExporting(true);
    try {
      const blob = await apiExportZip(dslText, settings);
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = (fileName?.replace(/\.ya?ml$/, '') ?? 'cabinet') + '-export.zip';
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (err) {
      alert(`Export failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setExporting(false);
    }
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
      {version && <span className={styles.version}>v{version}</span>}
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
      <button className="ghost" onClick={handleExport} disabled={exporting}>
        {exporting ? 'Exporting…' : 'Export'}
      </button>
      <div className={styles.sep} />
      <div ref={settingsBtnRef} className={styles.settingsWrap}>
        <button
          className={`ghost ${showSettings ? styles.settingsActive : ''}`}
          onClick={() => setShowSettings((v) => !v)}
          title="Export settings"
        >
          ⚙
        </button>
        {showSettings && (
          <SettingsPopover
            settings={settings}
            onChange={setSettings}
            onClose={() => setShowSettings(false)}
          />
        )}
      </div>
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
