import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import type { MarkdownData } from '../services/api';
import { Emulator } from '../components/Emulator';
import type { EmulatorHandle } from '../components/Emulator';
import './AdminView.css';

const DEFAULT_MD = `# TITULO GRANDE
## Subtitulo Centrado
### Encabezado pequeño
===
{ Hamburguesa : $12.50 }
{ Papas Fritas : $4.00 }
{ Refresco : $2.50 }
---
{ TOTAL : $19.00 }
===
[x] Pagado con Tarjeta
[ ] Facturado
---
FOLIO: !!AB-1234!!
---
!QR(https://example.com)
!BC(AB1234)
---
!IMG(https://raw.githubusercontent.com/python-escpos/python-escpos/master/escpos/resources/escpos-logo.png)
---
!HEART()
!MOON()
!STAR()
---
| ¡Gracias por tu visita!
> Atendido por: Bot`;

export const AdminView: React.FC = () => {
  const [markdown, setMarkdown] = useState(DEFAULT_MD);
  const [apiKey, setApiKey] = useState('mi_super_secreto_123');
  const [target, setTarget] = useState<'emulator' | 'physical'>('emulator');
  const [physicalKey, setPhysicalKey] = useState('');
  const [status, setStatus] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Estado para previsualización en vivo
  const [previewData, setPreviewData] = useState<{ paper: any[], logs: string[] } | null>(null);
  const [useLivePreview, setUseLivePreview] = useState(true);

  const emuRef = useRef<EmulatorHandle>(null);

  // Debounce para previsualización en vivo
  useEffect(() => {
    if (!useLivePreview) {
      setPreviewData(null);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const data = await api.getPreview(markdown);
        setPreviewData(data);
      } catch (e) {
        console.error("Live preview error", e);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [markdown, useLivePreview]);

  const handlePrint = async () => {
    setLoading(true);
    setStatus(null);
    try {
      const data: MarkdownData = {
        markdown,
        target,
        physical_key: physicalKey || undefined,
      };
      const res = await api.printMarkdown(apiKey, data);
      
      if (res.status === 'ok') {
        setStatus({ msg: 'Impresión enviada correctamente', type: 'success' });
        // Si no estamos en modo live, refrescamos el emulador TCP
        if (target === 'emulator' && !useLivePreview && emuRef.current) {
          emuRef.current.refresh();
        }
      } else {
        setStatus({ msg: `Error: ${res.detail || 'Fallo en la autenticación'}`, type: 'error' });
      }
    } catch (e) {
      setStatus({ msg: 'Error de conexión con el servidor', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    try {
      await api.clearEmulator(apiKey);
      if (emuRef.current) emuRef.current.refresh();
      if (useLivePreview) setPreviewData(null);
    } catch (e) {
      console.error('Error clearing emulator', e);
    }
  };

  return (
    <div className="admin-container">
      <div className="editor">
        <h2>POS Print Editor</h2>
        <div className="toolbar">
          <input
            type="password"
            placeholder="X-API-Key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <select value={target} onChange={(e) => setTarget(e.target.value as any)}>
            <option value="emulator">Emulador</option>
            <option value="physical">Impresora Física</option>
          </select>
          {target === 'physical' && (
            <input
              type="password"
              placeholder="Clave Física"
              value={physicalKey}
              onChange={(e) => setPhysicalKey(e.target.value)}
            />
          )}
          <button onClick={handlePrint} disabled={loading}>
            {loading ? 'Imprimiendo...' : 'Imprimir'}
          </button>
          <button 
            onClick={handleClear} 
            style={{ background: '#757575' }} 
            title="Limpiar Emulador"
          >
            🧹
          </button>
          {status && (
            <span className={`status-msg ${status.type}`}>
              {status.msg}
            </span>
          )}
        </div>
        <textarea
          value={markdown}
          onChange={(e) => setMarkdown(e.target.value)}
          placeholder="Escribe tu Markdown aquí..."
        />
      </div>
      <div className="preview">
        <div className="preview-header">
          <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
            <span>Previsualización</span>
            <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={useLivePreview} 
                onChange={e => setUseLivePreview(e.target.checked)} 
              />
              En Vivo
            </label>
          </div>
          {!useLivePreview && (
            <button onClick={() => { if(emuRef.current) emuRef.current.refresh(); }} style={{ padding: '2px 8px', fontSize: '12px' }}>
              Refrescar TCP
            </button>
          )}
        </div>
        <Emulator 
          ref={emuRef} 
          paper={previewData?.paper} 
          logs={previewData?.logs}
          autoRefresh={!useLivePreview}
        />
      </div>
    </div>
  );
};
