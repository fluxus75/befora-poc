import { useEffect, useMemo, useState } from 'react';

import type { SessionSlot } from '../types';

interface SlotEditorProps {
  slots: SessionSlot[];
  readOnly: boolean;
  onSave: (slots: Record<string, string | null>) => Promise<void>;
}

export default function SlotEditor({ slots, readOnly, onSave }: SlotEditorProps) {
  const initial = useMemo(() => {
    const map: Record<string, string | null> = {};
    slots.forEach((slot) => {
      map[slot.slot_key] = slot.slot_value ?? '';
    });
    return map;
  }, [slots]);

  const [drafts, setDrafts] = useState<Record<string, string | null>>(initial);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setDrafts(initial);
  }, [initial]);

  const handleChange = (key: string, value: string) => {
    setDrafts((state) => ({ ...state, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    await onSave(drafts);
    setSaving(false);
  };

  return (
    <div className="card">
      <h3>Slot Review</h3>
      <div className="grid">
        {slots.map((slot) => (
          <div className="slot-row" key={slot.slot_key}>
            <div>{slot.slot_key}</div>
            {readOnly ? (
              <div>{slot.slot_value ?? '-'}</div>
            ) : (
              <input
                className="input"
                value={drafts[slot.slot_key] ?? ''}
                onChange={(event) => handleChange(slot.slot_key, event.target.value)}
              />
            )}
          </div>
        ))}
      </div>
      {readOnly ? null : (
        <div style={{ marginTop: 16 }}>
          <button className="btn" type="button" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Slots'}
          </button>
        </div>
      )}
    </div>
  );
}
