import { useEffect, useRef, useState } from 'react';
import Editor from '@monaco-editor/react';
import type Monaco from 'monaco-editor';
import { useStore } from '../../store/useStore';
import { registerDslCompletions } from './dslCompletions';
import styles from './DslEditor.module.css';

const DEBOUNCE_MS = 600;

export default function DslEditor() {
  const dslText = useStore((s) => s.dslText);
  const setDslText = useStore((s) => s.setDslText);
  const compile = useStore((s) => s.compile);
  const compileStatus = useStore((s) => s.compileStatus);
  const stdlib = useStore((s) => s.stdlib);
  const [copied, setCopied] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const stdlibRef = useRef(stdlib);
  useEffect(() => { stdlibRef.current = stdlib; }, [stdlib]);

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

  function handleBeforeMount(monaco: typeof Monaco) {
    registerDslCompletions(monaco, () => stdlibRef.current);
  }

  function handleCopy() {
    navigator.clipboard.writeText(dslText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
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
        <button className={styles.copyBtn} onClick={handleCopy}>
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <div className={styles.editor}>
        <Editor
          value={dslText}
          onChange={handleChange}
          beforeMount={handleBeforeMount}
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
            quickSuggestions: { other: true, comments: false, strings: true },
            suggestOnTriggerCharacters: true,
          }}
        />
      </div>
    </div>
  );
}
