import { useEffect } from 'react';
import styles from './PreviewModal.module.css';

interface Props {
  html: string;
  onClose: () => void;
}

export default function PreviewModal({ html, onClose }: Props) {
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <div className={styles.overlay} onMouseDown={onClose}>
      <div className={styles.modal} onMouseDown={(e) => e.stopPropagation()}>
        <button className={styles.close} onClick={onClose} title="Close">×</button>
        <iframe
          className={styles.frame}
          srcDoc={html}
          sandbox="allow-scripts"
          title="Export Preview"
        />
      </div>
    </div>
  );
}
