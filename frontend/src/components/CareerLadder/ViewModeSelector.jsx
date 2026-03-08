import React from 'react';
import { FaNetworkWired, FaBalanceScale } from 'react-icons/fa';

export default function ViewModeSelector({ mode, onChange }) {
  const modes = [
    { id: 'network', label: 'Ecosystem Map', icon: <FaNetworkWired /> },
    { id: 'comparison', label: 'Market Benchmark', icon: <FaBalanceScale /> }
  ];
  
  return (
    <div className="flex items-center gap-1">
      {modes.map((m) => {
        const isActive = mode === m.id;
        return (
          <button
            key={m.id}
            onClick={() => onChange(m.id)}
            className={`
              relative px-6 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 flex items-center gap-3 overflow-hidden
              ${isActive 
                ? 'text-white shadow-lg shadow-blue-500/20 bg-transparent' 
                : 'text-slate-600 bg-transparent hover:text-slate-900 hover:bg-slate-100/80 shadow-none hover:shadow-sm'
              }
            `}
            style={{
              background: isActive ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
              border: isActive ? 'none' : '1px solid transparent'
            }}
          >
            <span className="relative z-10 text-lg">{m.icon}</span>
            <span className="relative z-10 uppercase tracking-widest text-[10px]">{m.label}</span>
          </button>
        );
      })}
    </div>
  );
}
