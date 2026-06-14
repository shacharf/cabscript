import { useStore } from '../../store/useStore';
import styles from './GlobalProperties.module.css';

const CABINET_TYPES = ['built_in', 'standing', 'kitchen_base', 'kitchen_wall', 'wardrobe'];

function replaceLine(dsl: string, pattern: RegExp, replacement: string): string {
  if (pattern.test(dsl)) return dsl.replace(pattern, replacement);
  return dsl.trimEnd() + '\n' + replacement + '\n';
}

// Parse niche dimensions directly from DSL text — updated instantly, no compile lag.
function parseNiche(dsl: string): { w: number; h: number; d: number } | null {
  const m = dsl.match(/^space:\s*niche\s+(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)/m);
  if (!m) return null;
  return { w: Number(m[1]), h: Number(m[2]), d: Number(m[3]) };
}

function setNicheDim(dsl: string, w: number, h: number, d: number): string {
  return replaceLine(dsl, /^space:.*$/m, `space: niche ${w} x ${h} x ${d}`);
}

// Parse cabinet type from DSL text (more reliable than deriving from project state).
function parseCabinetType(dsl: string): string {
  const m = dsl.match(/^\s+type:\s*(\S+)/m);
  return m?.[1] ?? 'built_in';
}

export default function GlobalProperties() {
  const project = useStore((s) => s.project);
  const stdlib = useStore((s) => s.stdlib);
  const dslText = useStore((s) => s.dslText);
  const setDslText = useStore((s) => s.setDslText);

  const materials = stdlib?.materials ?? [];
  const niche = parseNiche(dslText);
  const cabinetType = parseCabinetType(dslText);
  const isBuiltIn = cabinetType === 'built_in';

  function setMaterial(val: string) {
    setDslText(replaceLine(dslText, /^material:.*$/m, `material: ${val}`));
  }

  function setStandard(val: string) {
    setDslText(replaceLine(dslText, /^use:.*$/m, `use: ${val}`));
  }

  function setCabinetType(val: string) {
    setDslText(replaceLine(dslText, /^\s+type:.*$/m, `  type: ${val}`));
  }

  function setDim(field: 'w' | 'h' | 'd', raw: string) {
    const val = parseFloat(raw);
    if (!niche || isNaN(val) || val <= 0) return;
    const next = { ...niche, [field]: val };
    setDslText(setNicheDim(dslText, next.w, next.h, next.d));
  }

  return (
    <div>
      <h3>Project</h3>

      {isBuiltIn && (
        <div className="field">
          <label>Niche (space)</label>
          <div className={styles.dimRow}>
            <DimInput label="W" value={niche?.w} onChange={(v) => setDim('w', v)} />
            <DimInput label="H" value={niche?.h} onChange={(v) => setDim('h', v)} />
            <DimInput label="D" value={niche?.d} onChange={(v) => setDim('d', v)} />
          </div>
          {project && (
            <div className={styles.dimNote}>
              cabinet: {Math.round(project.width)} × {Math.round(project.height)} × {Math.round(project.depth)} mm (after clearances)
            </div>
          )}
        </div>
      )}

      <div className="field">
        <label>Cabinet Type</label>
        <select value={cabinetType} onChange={(e) => setCabinetType(e.target.value)}>
          {CABINET_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      <div className="field">
        <label>Standard</label>
        <select
          value={project?.standard ?? 'euro_builtin_v1'}
          onChange={(e) => setStandard(e.target.value)}
        >
          {(stdlib?.standards ?? ['euro_builtin_v1']).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <div className="field">
        <label>Material</label>
        <select value={project?.material ?? ''} onChange={(e) => setMaterial(e.target.value)}>
          {materials.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

      {project && (
        <div className="field">
          <label>Summary</label>
          <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
            {project.parts.length} parts · {project.modules.length} module{project.modules.length !== 1 ? 's' : ''} · {project.bays.length} bays
          </div>
        </div>
      )}
    </div>
  );
}

function DimInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number | undefined;
  onChange: (v: string) => void;
}) {
  return (
    <label style={{ display: 'flex', alignItems: 'center', gap: 4, flex: 1 }}>
      <span style={{ fontSize: 10, color: 'var(--text-muted)', flexShrink: 0 }}>{label}</span>
      <input
        type="number"
        min={1}
        step={1}
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        style={{ width: '100%' }}
      />
    </label>
  );
}
