import { useStore } from '../../store/useStore';
import styles from './ColorPalette.module.css';

const ROLES = ['body', 'doors', 'shelves'] as const;
type Role = (typeof ROLES)[number];

function replaceLine(dsl: string, role: Role, color: string): string {
  const pattern = new RegExp(`^(\\s+${role}:).*$`, 'm');
  const replacement = `  ${role}: ${color}`;
  if (pattern.test(dsl)) {
    return dsl.replace(pattern, replacement);
  }
  // Try to insert under finish: block
  if (/^finish:/m.test(dsl)) {
    return dsl.replace(/^(finish:.*)$/m, `$1\n${replacement}`);
  }
  return dsl.trimEnd() + `\n\nfinish:\n${replacement}\n`;
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
    const match = dslText.match(new RegExp(`^\\s+${role}:\\s*(\\S+)`, 'm'));
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
