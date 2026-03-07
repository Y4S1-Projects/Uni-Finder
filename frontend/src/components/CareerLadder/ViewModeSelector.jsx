import React from 'react';
import { FaStream, FaNetworkWired, FaBalanceScale } from 'react-icons/fa';

export default function ViewModeSelector({ mode, onChange }) {
  const modes = [
    { id: 'timeline', label: 'Timeline', icon: <FaStream /> },
    { id: 'network', label: 'Network Graph', icon: <FaNetworkWired /> },
    { id: 'comparison', label: 'Compare Paths', icon: <FaBalanceScale /> }
  ];
  
  return (
    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        View Mode
      </label>
      <div className="flex gap-2">
        {modes.map((m) => (
          <button
            key={m.id}
            onClick={() => onChange(m.id)}
            className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
              mode === m.id
                ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                : 'bg-white border-2 border-gray-200 text-gray-700 hover:border-purple-300'
            }`}
          >
            {m.icon}
            {m.label}
          </button>
        ))}
      </div>
    </div>
  );
}
