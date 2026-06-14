import { useEffect } from 'react';
import { useStore } from './store/useStore';
import StartScreen from './components/StartScreen/StartScreen';
import AppShell from './components/AppShell/AppShell';

export default function App() {
  const fileName = useStore((s) => s.fileName);
  const loadStdlib = useStore((s) => s.loadStdlib);

  useEffect(() => {
    loadStdlib();
  }, [loadStdlib]);

  if (fileName === null) {
    return <StartScreen />;
  }

  return <AppShell />;
}
