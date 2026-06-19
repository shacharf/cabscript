import type Monaco from 'monaco-editor';
import type { StdLibData } from '../../types/cabinet';

type MonacoNS = typeof Monaco;

const TOP_LEVEL_KEYS = ['use', 'material', 'space', 'cabinet', 'layout', 'doors', 'finish'];

const LAYOUT_VALUES = [
  'drawers 2', 'drawers 3', 'drawers 4', 'drawers 5',
  'drawers 2 no_front', 'drawers 3 no_front', 'drawers 4 no_front',
  'shelves 2', 'shelves 3', 'shelves 4', 'shelves 5', 'shelves 5 adjustable',
  'hanging rod 900', 'hanging rod 1200', 'hanging rod 1800',
  'storage 300', 'storage 400', 'storage 500',
  'shoes 4', 'shoes 6',
  'open',
];

const DOOR_VALUES = ['none', 'auto', 'single', 'pair', 'folding'];
const DOOR_STYLES = ['slab', 'frame_panel_light'];
const HINGE_VALUES = ['concealed'];
const CABINET_TYPES = ['built_in', 'standing', 'kitchen_base', 'kitchen_wall', 'wardrobe'];
const CABINET_BASE = ['legs 80', 'legs 100', 'plinth 100'];

interface CompletionContext {
  type: 'key' | 'value';
  key?: string;
  parentKey?: string;
  indent?: number;
}

function getContext(model: Monaco.editor.ITextModel, position: Monaco.Position): CompletionContext {
  const line = model.getLineContent(position.lineNumber);
  const upToCursor = line.substring(0, position.column - 1);

  const valueMatch = upToCursor.match(/^(\s*)(\w[\w_-]*)\s*:\s*/);
  if (valueMatch) {
    const indent = valueMatch[1]!.length;
    const key = valueMatch[2]!;
    let parentKey: string | undefined;
    if (indent > 0) {
      for (let ln = position.lineNumber - 1; ln >= 1; ln--) {
        const prev = model.getLineContent(ln);
        const m = prev.match(/^(\s*)(\w[\w_-]*)\s*:/);
        if (m && m[1]!.length < indent) {
          parentKey = m[2];
          break;
        }
      }
    }
    return { type: 'value', key, parentKey, indent };
  }

  return { type: 'key', indent: upToCursor.match(/^(\s*)/)?.[1]?.length ?? 0 };
}

function makeItem(
  monaco: MonacoNS,
  range: Monaco.IRange,
  label: string,
  detail?: string,
): Monaco.languages.CompletionItem {
  return {
    label,
    kind: monaco.languages.CompletionItemKind.Value,
    insertText: label,
    detail,
    range,
  };
}

function makeKeyItem(
  monaco: MonacoNS,
  range: Monaco.IRange,
  label: string,
): Monaco.languages.CompletionItem {
  return {
    label,
    kind: monaco.languages.CompletionItemKind.Property,
    insertText: `${label}: `,
    range,
  };
}

export function registerDslCompletions(
  monaco: MonacoNS,
  getStdlib: () => StdLibData | null,
): Monaco.IDisposable {
  return monaco.languages.registerCompletionItemProvider('yaml', {
    triggerCharacters: [' ', ':'],
    provideCompletionItems(model, position) {
      const word = model.getWordUntilPosition(position);
      const range: Monaco.IRange = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn,
      };

      const ctx = getContext(model, position);
      const stdlib = getStdlib();

      if (ctx.type === 'key') {
        if ((ctx.indent ?? 0) === 0) {
          return { suggestions: TOP_LEVEL_KEYS.map((k) => makeKeyItem(monaco, range, k)) };
        }
        return { suggestions: [] };
      }

      const { key, parentKey } = ctx;

      if (key === 'use') {
        const values = stdlib?.standards ?? ['euro_builtin_v1'];
        return { suggestions: values.map((v) => makeItem(monaco, range, v, 'standard')) };
      }

      if (key === 'material' && (!parentKey || parentKey === 'cabinet')) {
        const values = stdlib?.materials ?? ['plywood_18', 'mdf_18'];
        return { suggestions: values.map((v) => makeItem(monaco, range, v, 'material')) };
      }

      if (parentKey === 'finish') {
        const colors = Object.keys(stdlib?.colors ?? {});
        return { suggestions: colors.map((v) => makeItem(monaco, range, v, 'color')) };
      }

      if (parentKey === 'layout') {
        return { suggestions: LAYOUT_VALUES.map((v) => makeItem(monaco, range, v, 'layout')) };
      }

      if (parentKey === 'doors') {
        if (key === 'style') {
          return { suggestions: DOOR_STYLES.map((v) => makeItem(monaco, range, v)) };
        }
        if (key === 'hinges') {
          return { suggestions: HINGE_VALUES.map((v) => makeItem(monaco, range, v)) };
        }
        return { suggestions: DOOR_VALUES.map((v) => makeItem(monaco, range, v, 'door config')) };
      }

      if (key === 'type' && parentKey === 'cabinet') {
        return { suggestions: CABINET_TYPES.map((v) => makeItem(monaco, range, v)) };
      }

      if (key === 'base' && parentKey === 'cabinet') {
        return { suggestions: CABINET_BASE.map((v) => makeItem(monaco, range, v)) };
      }

      return { suggestions: [] };
    },
  });
}
