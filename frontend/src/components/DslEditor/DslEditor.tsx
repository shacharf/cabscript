import { useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { useStore } from '../../store/useStore';
import styles from './DslEditor.module.css';

const DEBOUNCE_MS = 600;

export default function DslEditor() {
  const dslText = useStore((s) => s.dslText);
  const setDslText = useStore((s) => s.setDslText);
  const compile = useStore((s) => s.compile);
  const compileStatus = useStore((s) => s.compileStatus);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Auto-compile on DSL change with debounce
  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      compile();
    }, DEBOUNCE_MS);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [dslText, compile]);

  function handleChange(value: string | undefined) {
    setDslText(value ?? '');
  }

  const indicator =
    compileStatus === 'compiling' ? '●' : compileStatus === 'ok' ? '✓' : compileStatus === 'error' ? '✗' : '○';

  const indicatorClass =
    compileStatus === 'ok' ? styles.ok : compileStatus === 'error' ? styles.err : styles.dim;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.label}>DSL Editor</span>
        <span className={`${styles.indicator} ${indicatorClass}`}>{indicator}</span>
      </div>
      <div className={styles.editor}>
        <Editor
          value={dslText}
          onChange={handleChange}
          language="yaml"
          theme="vs-dark"
          options={{
            automaticLayout: true,
            fontSize: 13,
            fontFamily: 'JetBrains Mono, Fira Code, Cascadia Code, monospace',
            lineNumbers: 'on',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: 'off',
            renderLineHighlight: 'line',
            padding: { top: 8, bottom: 8 },
          }}
        />
      </div>
    </div>
  );
}
