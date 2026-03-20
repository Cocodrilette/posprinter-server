import React, { useEffect, useState, forwardRef, useImperativeHandle } from 'react';
import { api } from '../services/api';
import './Emulator.css';

interface PaperItem {
  type: 'text' | 'newline' | 'image' | 'barcode';
  text?: string;
  data?: string;
  align?: 'left' | 'center' | 'right';
  bold?: boolean;
  underline?: number;
  invert?: boolean;
  width?: number;
  height?: number;
}

export interface EmulatorHandle {
  refresh: () => void;
}

interface EmulatorProps {
  paper?: PaperItem[];
  logs?: string[];
  autoRefresh?: boolean;
}

export const Emulator = forwardRef<EmulatorHandle, EmulatorProps>((props, ref) => {
  const [internalPaper, setInternalPaper] = useState<PaperItem[]>([]);
  const [internalLogs, setInternalLogs] = useState<string[]>([]);
  const [showLogs, setShowLogs] = useState(false);

  const fetchData = async () => {
    // Solo hacemos fetch si no nos pasan los datos por props
    if (props.paper !== undefined) return;
    
    try {
      const data = await api.getEmulatorState();
      setInternalPaper(data.paper || []);
      setInternalLogs(data.logs || []);
    } catch (e) {
      console.error('Error fetching emulator state', e);
    }
  };

  useImperativeHandle(ref, () => ({
    refresh: fetchData
  }));

  useEffect(() => {
    fetchData();
    if (props.autoRefresh && props.paper === undefined) {
      const interval = setInterval(fetchData, 2000);
      return () => clearInterval(interval);
    }
  }, [props.autoRefresh, props.paper]);

  const paper = props.paper !== undefined ? props.paper : internalPaper;
  const logs = props.logs !== undefined ? props.logs : internalLogs;

  const renderItem = (item: PaperItem, index: number) => {
    switch (item.type) {
      case 'newline':
        return <div key={index} className="emu-newline" />;
      
      case 'image':
        return (
          <div key={index} className="emu-image-container" style={{ textAlign: item.align }}>
            <img 
              src={`data:image/png;base64,${item.data}`} 
              alt="print-raster" 
              className="emu-image"
              style={{ display: item.align === 'center' ? 'inline' : 'block' }}
            />
          </div>
        );
      
      case 'barcode':
        return (
          <div key={index} className="emu-barcode">
            [BC: {item.text}]
          </div>
        );
      
      case 'text':
      default:
        const style: React.CSSProperties = {
          textAlign: item.align,
          fontWeight: item.bold ? 'bold' : 'normal',
          textDecoration: item.underline ? 'underline' : 'none',
          background: item.invert ? 'black' : 'transparent',
          color: item.invert ? 'white' : 'inherit',
          display: 'block',
          width: '100%',
          minHeight: `${(item.height || 1) * 1.2}em`
        };

        const spanStyle: React.CSSProperties = {
          transform: `scale(${item.width || 1}, ${item.height || 1})`,
          transformOrigin: `${item.align} top`,
          display: 'inline-block',
          whiteSpace: 'pre'
        };

        const content = (item.text || '').replace(/ /g, '\u00A0');

        return (
          <div key={index} className="emu-line" style={style}>
            <span className="emu-text-span" style={spanStyle}>
              {content}
            </span>
          </div>
        );
    }
  };

  return (
    <div className="emulator-container">
      <div className="emulator-scroll">
        <div className="virtual-paper">
          {paper.length === 0 ? (
            <div style={{ color: '#ccc', textAlign: 'center', marginTop: '50px' }}>
              Bandeja de salida vacía
            </div>
          ) : (
            paper.map((item, i) => renderItem(item, i))
          )}
        </div>
      </div>

      <details className="hex-logs-section" open={showLogs} onToggle={(e) => setShowLogs((e.target as HTMLDetailsElement).open)}>
        <summary>🔍 HEX LOGS</summary>
        <div className="hex-logs-content">
          {logs.slice().reverse().map((log, i) => (
            <pre key={i} className="hex-entry">{log}</pre>
          ))}
        </div>
      </details>
    </div>
  );
});
