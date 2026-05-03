import React from 'react';
import { FaNetworkWired, FaBalanceScale } from 'react-icons/fa';

export default function ViewModeSelector({ mode, onChange }) {
  const modes = [
    { id: 'network', label: 'Career Network', icon: <FaNetworkWired /> },
    { id: 'comparison', label: 'Compare Paths', icon: <FaBalanceScale /> }
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
                ? 'text-white bg-indigo-600 shadow-md' 
                : 'text-gray-600 bg-gray-100 hover:bg-gray-200'
              }
            `}
          >
            <span className="relative z-10 text-lg">{m.icon}</span>
            <span className="relative z-10 uppercase tracking-widest text-[10px]">{m.label}</span>
          </button>
        );
      })}
    </div>
  );
}
