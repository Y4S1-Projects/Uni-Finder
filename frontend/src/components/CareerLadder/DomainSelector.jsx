import React from 'react';
import { FaChevronDown } from 'react-icons/fa';

export default function DomainSelector({ domains, selected, onChange }) {
  return (
    <div className="relative">
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Select Career Domain
      </label>
      <div className="relative">
        <select
          value={selected}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-4 py-3 pr-10 bg-white border-2 border-purple-200 rounded-xl appearance-none cursor-pointer focus:outline-none focus:border-purple-500 font-semibold text-gray-800"
        >
          {domains.map((domain) => (
            <option key={domain.domain_id} value={domain.domain_id}>
              {domain.domain_name} ({domain.total_levels} levels)
            </option>
          ))}
        </select>
        <FaChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
      </div>
    </div>
  );
}
