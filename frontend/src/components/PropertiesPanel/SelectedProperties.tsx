import { useStore } from '../../store/useStore';

export default function SelectedProperties() {
  const project = useStore((s) => s.project);
  const selectedBayId = useStore((s) => s.selectedBayId);
  const selectedPartId = useStore((s) => s.selectedPartId);

  if (!project) return null;

  const bay = selectedBayId ? project.bays.find((b) => b.id === selectedBayId) : null;
  const part = selectedPartId ? project.parts.find((p) => p.id === selectedPartId) : null;

  if (!bay && !part) {
    return (
      <div>
        <h3>Selection</h3>
        <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Click a bay or panel in the 2D view</div>
      </div>
    );
  }

  if (bay) {
    return (
      <div>
        <h3>Bay</h3>
        <Row label="Function" value={bay.function.kind} />
        <Row label="Size" value={`${Math.round(bay.width)} × ${Math.round(bay.height)} mm`} />
        <Row label="Module" value={bay.module_id} />
        {Object.entries(bay.function.params).map(([k, v]) => (
          <Row key={k} label={k} value={String(v)} />
        ))}
      </div>
    );
  }

  if (part) {
    return (
      <div>
        <h3>Part</h3>
        <Row label="Name" value={part.name} />
        <Row label="Kind" value={part.kind} />
        <Row
          label="Dimensions"
          value={`${Math.round(part.length)} × ${Math.round(part.width)} × ${Math.round(part.thickness)} mm`}
        />
        <Row label="Material" value={part.material} />
        <Row label="Grain" value={part.grain_direction} />
        {part.edge_banding.length > 0 && (
          <Row label="Edge banding" value={part.edge_banding.join(', ')} />
        )}
      </div>
    );
  }

  return null;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="field">
      <label>{label}</label>
      <div style={{ color: 'var(--text-secondary)', fontSize: 12, fontFamily: 'var(--font-mono)' }}>
        {value}
      </div>
    </div>
  );
}
