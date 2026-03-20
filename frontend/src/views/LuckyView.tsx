import React, { useState } from 'react';
import { api } from '../services/api';
import type { LuckyData } from '../services/api';
import './LuckyView.css';

export const LuckyView: React.FC = () => {
  const [physicalKey, setPhysicalKey] = useState('');
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [fortune, setFortune] = useState<string | null>(null);
  const [isBallActive, setIsBallActive] = useState(false);
  const [tempKey, setTempKey] = useState('');

  const handleUnlock = () => {
    if (tempKey) {
      setPhysicalKey(tempKey);
      setIsUnlocked(true);
    } else {
      alert("La clave es necesaria para activar la magia.");
    }
  };

  const handleReveal = async () => {
    if (processing || !physicalKey) return;
    
    setProcessing(true);
    setFortune(null);
    setIsBallActive(true);

    try {
      const data: LuckyData = {
        target: 'physical',
        physical_key: physicalKey
      };
      
      const res = await api.luckyPrint('mi_super_secreto_123', data);

      if (res.status === 'ok') {
        setTimeout(() => {
          setIsBallActive(false);
          setFortune(res.frase);
          setProcessing(false);
        }, 1500);
      } else {
        throw new Error(res.detail || "Fallo");
      }
    } catch (e: any) {
      setIsBallActive(false);
      setFortune("La clave no parece correcta para este oráculo...");
      setProcessing(false);
      
      // Volver a bloquear si falla la clave
      setTimeout(() => {
        setIsUnlocked(false);
        setFortune(null);
      }, 2000);
    }
  };

  return (
    <div className="lucky-body">
      {!isUnlocked && (
        <div className="access-modal">
          <div className="modal-content">
            <h2>🔐 Acceso Requerido</h2>
            <p>Introduce la Clave de Impresión Física</p>
            <input 
              type="password" 
              className="lucky-input"
              placeholder="Clave Física..."
              value={tempKey}
              onChange={(e) => setTempKey(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleUnlock()}
            />
            <br />
            <button className="btn-access" onClick={handleUnlock}>ENTRAR AL ORÁCULO</button>
          </div>
        </div>
      )}

      <div 
        className={`crystal-ball ${isBallActive ? 'active' : ''}`} 
        onClick={handleReveal}
      >
        <span>🔮</span>
      </div>

      <div className={`fortune-display ${fortune ? 'visible' : ''}`}>
        {fortune ? `"${fortune}"` : ''}
      </div>
      
      <div className="lucky-instruction">Toca la esfera para ver tu destino</div>
    </div>
  );
};
