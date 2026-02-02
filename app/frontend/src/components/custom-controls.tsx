import { ControlButton, Controls } from '@xyflow/react';
import { Redo2, Trash2, Undo2, XCircle } from 'lucide-react';

type CustomControlsProps = {
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  onDeleteSelected: () => void;
  hasSelection: boolean;
  onClearAll: () => void;
  hasNodes: boolean;
};

export function CustomControls({
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  onDeleteSelected,
  hasSelection,
  onClearAll,
  hasNodes,
}: CustomControlsProps) {
  return (
    <Controls
      position="bottom-center"
      orientation="horizontal"
      showZoom={false}
      showFitView={false}
      showInteractive={false}
      style={{ bottom: 20, borderRadius: 20, gap: 4 }}
      className="bg-ramp-grey-800 text-primary px-2 py-2 rounded-md [&_button]:border-0 [&_button]:outline-0 [&_button]:shadow-none"
    >
      <ControlButton
        onClick={onUndo}
        title="Undo (⌘Z)"
        disabled={!canUndo}
        className={!canUndo ? 'opacity-40 cursor-not-allowed' : ''}
      >
        <Undo2 className="w-4 h-4" />
      </ControlButton>
      <ControlButton
        onClick={onRedo}
        title="Redo (⌘⇧Z)"
        disabled={!canRedo}
        className={!canRedo ? 'opacity-40 cursor-not-allowed' : ''}
      >
        <Redo2 className="w-4 h-4" />
      </ControlButton>

      <div className="w-px h-6 bg-muted-foreground/30 mx-1" />

      <ControlButton
        onClick={onDeleteSelected}
        title="Delete Selected (⌫)"
        disabled={!hasSelection}
        className={!hasSelection ? 'opacity-40 cursor-not-allowed' : ''}
      >
        <Trash2 className="w-4 h-4" />
      </ControlButton>
      <ControlButton
        onClick={onClearAll}
        title="Clear All"
        disabled={!hasNodes}
        className={!hasNodes ? 'opacity-40 cursor-not-allowed' : ''}
      >
        <XCircle className="w-4 h-4" />
      </ControlButton>
    </Controls>
  );
}
