import { useStore } from '../../store/useStore';
import styles from './ColorPalette.module.css';

const ROLES = ['body', 'doors', 'shelves'] as const;
type Role = (typeof ROLES)[number];

function replaceLine(dsl: string, role: Role, color: string): string {
  const line = `  ${role}: ${color}`;

  const finishIdx = dsl.search(/^finish:/m);
  if (finishIdx === -1) {
    return dsl.trimEnd() + `\n\nfinish:\n${line}\n`;
  }

  // Determine the extent of the finish block (up to next top-level key or EOF)
  const afterHeader = dsl.indexOf('\n', finishIdx);
  const rest = dsl.slice(afterHeader + 1);
  const nextTopLevel = rest.search(/^[^\s#]/m);
  const finishBlockEnd = nextTopLevel === -1 ? dsl.length : afterHeader + 1 + nextTopLevel;

  const finishBlock = dsl.slice(finishIdx, finishBlockEnd);
  const rolePattern = new RegExp(`^([ \\t]+${role}:).*$`, 'm');

  const newFinishBlock = rolePattern.test(finishBlock)
    ? finishBlock.replace(rolePattern, line)
    : finishBlock.replace(/^(finish:[^\n]*)$/m, `$1\n${line}`);

  return dsl.slice(0, finishIdx) + newFinishBlock + dsl.slice(finishBlockEnd);
}

export default function ColorPalette() {
  const stdlib = useStore((s) => s.stdlib);
  const dslText = useStore((s) => s.dslText);
  const setDslText = useStore((s) => s.setDslText);
  const project = useStore((s) => s.project);

  const colors = stdlib?.colors ?? {};
  const colorNames = Object.keys(colors);

  function handleColorClick(role: Role, colorName: string) {
    setDslText(replaceLine(dslText, role, colorName));
  }

  function currentColor(role: Role): string {
    const finishIdx = dslText.search(/^finish:/m);
    if (finishIdx === -1) return '';
    const afterHeader = dslText.indexOf('\n', finishIdx);
    const rest = dslText.slice(afterHeader + 1);
    const nextTopLevel = rest.search(/^[^\s#]/m);
    const finishBlock = nextTopLevel === -1 ? rest : rest.slice(0, nextTopLevel);
    const match = finishBlock.match(new RegExp(`^[ \\t]+${role}:\\s*(\\S+)`, 'm'));
    return match?.[1] ?? '';
  }

  if (colorNames.length === 0 && !project) return null;

  return (
    <div>
      <h3>Finish Colors</h3>
      {ROLES.map((role) => {
        const active = currentColor(role);
        return (
          <div key={role} className="field">
            <label>{role}</label>
            <div className={styles.swatches}>
              {colorNames.map((name) => {
                const entry = colors[name];
                if (!entry) return null;
                const [r, g, b] = entry.rgba;
                return (
                  <button
                    key={name}
                    title={`${name} — ${entry.description}`}
                    className={`${styles.swatch}${name === active ? ` ${styles.active}` : ''}`}
                    style={{ background: `rgb(${r},${g},${b})` }}
                    onClick={() => handleColorClick(role, name)}
                  />
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
