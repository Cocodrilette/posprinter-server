import { useState, useEffect } from 'react';
import { AdminView } from './views/AdminView';
import { LuckyView } from './views/LuckyView';

function App() {
  const [view, setView] = useState<'admin' | 'lucky'>('admin');

  // Simple routing based on URL hash or path
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/lucky') setView('lucky');
      else setView('admin');
    };

    window.addEventListener('popstate', handlePopState);
    handlePopState(); // Initial check

    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (newView: 'admin' | 'lucky') => {
    const path = newView === 'lucky' ? '/lucky' : '/';
    window.history.pushState({}, '', path);
    setView(newView);
  };

  return (
    <>
      <div style={{ position: 'fixed', bottom: '10px', right: '10px', zIndex: 1000, display: 'flex', gap: '10px' }}>
        <button 
          onClick={() => navigate('admin')}
          style={{ opacity: 0.3, padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}
        >Admin</button>
        <button 
          onClick={() => navigate('lucky')}
          style={{ opacity: 0.3, padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}
        >Lucky</button>
      </div>

      {view === 'admin' ? <AdminView /> : <LuckyView />}
    </>
  );
}

export default App;
