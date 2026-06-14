import { useStore } from '../../store/useStore';

const CABINET_TYPES = ['built_in', 'standing', 'kitchen_base', 'kitchen_wall', 'wardrobe'];

function replaceLine(dsl: string, pattern: RegExp, replacement: string): string {
  if (pattern.test(dsl)) {
    return dsl.replace(pattern, replacement);
  }
  // Append at end if not found
  return dsl.trimEnd() + '\n' + replacement + '\n';
}

export default function GlobalProperties() {
  const project = useStore((s) => s.project);
  const stdlib = useStore((s) => s.stdlib);
  const dslText = useStore((s) => s.dslText);
  const setDslText = useStore((s) => s.setDslText);

  const materials = stdlib?.materials ?? [];

  function setMaterial(val: string) {
    const updated = replaceLine(dslText, /^material:.*$/m, `material: ${val}`);
    setDslText(updated);
  }

  function setStandard(val: string) {
    const updated = replaceLine(dslText, /^use:.*$/m, `use: ${val}`);
    setDslText(updated);
  }

  function setCabinetType(val: string) {
    const updated = replaceLine(dslText, /^(\s+type:).*$/m, `  type: ${val}`);
    setDslText(updated);
  }

  return (
    <div>
      <h3>Project</h3>

      {project && (
        <div className="field">
          <label>Dimensions</label>
          <div style={{ color: 'var(--text-secondary)', fontSize: 12, fontFamily: 'var(--font-mono)' }}>
            {Math.round(project.width)} × {Math.round(project.height)} × {Math.round(project.depth)} mm
          </div>
        </div>
      )}

      <div className="field">
        <label>Standard</label>
        <select
          value={project?.standard ?? 'euro_builtin_v1'}
          onChange={(e) => setStandard(e.target.value)}
        >
          {(stdlib?.standards ?? ['euro_builtin_v1']).map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label>Material</label>
        <select
          value={project?.material ?? ''}
          onChange={(e) => setMaterial(e.target.value)}
        >
          {materials.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>

      {project && (
        <div className="field">
          <label>Cabinet Type</label>
          <select
            value={project.modules[0] ? 'built_in' : ''}
            onChange={(e) => setCabinetType(e.target.value)}
          >
            {CABINET_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      )}

      {project && (
        <div className="field">
          <label>Parts</label>
          <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
            {project.parts.length} parts · {project.modules.length} module
            {project.modules.length !== 1 ? 's' : ''} · {project.bays.length} bays
          </div>
        </div>
      )}
    </div>
  );
}
