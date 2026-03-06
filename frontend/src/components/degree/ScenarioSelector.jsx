import React from "react";

export default function ScenarioSelector({ scenarios, activeScenarioId, onChange }) {
	return (
		<div className='grid grid-cols-1 gap-3 mb-6 md:grid-cols-2'>
			{scenarios.map((scenario) => {
				const isActive = activeScenarioId === scenario.id;
				return (
					<button
						key={scenario.id}
						type='button'
						onClick={() => onChange(scenario)}
						className={`text-left p-4 rounded-xl border-2 transition-all ${
							isActive ? "border-purple-500 bg-purple-50 shadow-sm" : "border-gray-200 bg-white hover:border-purple-200"
						}`}>
						<div className='font-semibold text-gray-900'>{scenario.title}</div>
						<p className='mt-1 text-sm text-gray-600'>{scenario.description}</p>
					</button>
				);
			})}
		</div>
	);
}
