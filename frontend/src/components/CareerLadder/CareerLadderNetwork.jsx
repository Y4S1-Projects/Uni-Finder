import React, { useEffect } from "react";
import {
	ReactFlow,
	MiniMap,
	Controls,
	Background,
	useNodesState,
	useEdgesState,
	Handle,
	Position,
	MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { CareerDetailModal } from "../career/CareerDetailModal";
import { useCareerDetail } from "../../hooks/useCareerRecommendations";
import { FaStar, FaLock, FaCheckCircle, FaBolt } from "react-icons/fa";

// 💠 Advanced Role Node for Light Ecosystem
function CustomRoleNode({ data }) {
	const { level, isCurrent, isAchievable, isLocked, roleTitle, expRange, readiness, onNodeClick } = data;

	let bgClass = "bg-white border border-gray-200 shadow-sm hover:shadow-md hover:-translate-y-0.5";
	let titleClass = "text-gray-900";
	let subTextClass = "text-gray-600";

	if (isCurrent) {
		bgClass =
			"bg-indigo-50 border-indigo-500 shadow-md scale-105 z-50 ring-4 ring-indigo-500/5";
		titleClass = "text-indigo-900";
		subTextClass = "text-indigo-700";
	} else if (isLocked) {
		bgClass = "bg-gray-50 border border-gray-200 opacity-60 grayscale-[0.3]";
	}

	return (
		<div
			className={`relative rounded-3xl p-6 w-[280px] transition-all duration-200 select-none group cursor-pointer ${bgClass}`}
			onClick={() => onNodeClick(data.rawLevel)}>
			<Handle
				type='target'
				position={Position.Top}
				className={`!w-4 !h-4 !bg-blue-500 !border-4 !opacity-100 ${isCurrent ? "!border-indigo-700" : "!border-white"}`}
			/>

			<div className='flex items-start justify-between mb-4'>
				<div
					className={`text-[10px] px-2 py-1 rounded-full font-bold tracking-wider ${
						isCurrent ? "bg-indigo-100 text-indigo-700 border border-indigo-200" : "bg-gray-100 text-gray-600 border border-gray-200"
					}`}>
					TIER {level}
				</div>
				{isCurrent && (
					<div className='flex items-center gap-1.5 bg-yellow-100 px-2 py-1 rounded-full border border-yellow-300 shadow-sm'>
						<FaStar className='text-xs text-yellow-500 animate-pulse' />
						<span className='text-[9px] font-bold text-yellow-700 uppercase tracking-tighter'>Current</span>
					</div>
				)}
				{isLocked && !isCurrent && <FaLock className='text-sm text-slate-400' />}
				{isAchievable && !isCurrent && readiness >= 0.7 && (
					<div className='flex items-center gap-1 px-2 py-1 border rounded-lg bg-emerald-50 border-emerald-200'>
						<FaCheckCircle className='text-sm text-emerald-500' />
						<span className='text-[9px] font-bold text-emerald-600 uppercase tracking-tighter'>Ready</span>
					</div>
				)}
			</div>

			<h3 className={`font-black text-xl leading-tight mb-2 tracking-tight transition-colors ${titleClass}`}>
				{roleTitle}
			</h3>

			<div
				className={`inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider py-1 px-3 rounded-md mb-4 ${isCurrent ? "bg-indigo-100/50" : "bg-gray-100"} ${subTextClass}`}>
				<FaBolt className={`${isCurrent ? "text-indigo-600" : "text-gray-400"} text-[10px]`} />
				{expRange}
			</div>

			{!isCurrent && (
				<div className='pt-4 mt-4 border-t border-slate-100'>
					<div className='flex justify-between text-[10px] mb-2 font-black uppercase tracking-widest text-slate-400'>
						<span>Progression Index</span>
						<span className={isLocked ? "text-slate-400" : "text-blue-600"}>{Math.round(readiness * 100)}%</span>
					</div>
					<div className='w-full h-1.5 bg-gray-100 rounded-full overflow-hidden border border-gray-200'>
						<div
							className={`h-full rounded-full transition-all duration-1000 ${isAchievable ? "bg-indigo-600" : "bg-gray-300"}`}
							style={{ width: `${readiness * 100}%` }}
						/>
					</div>
				</div>
			)}

			{isCurrent && (
				<div className='mt-4 pt-4 border-t border-indigo-100 text-[10px] font-black uppercase tracking-widest text-indigo-500 flex items-center gap-2'>
					<div className='w-2 h-2 bg-indigo-500 rounded-full animate-ping' />
					Syncing with Profile
				</div>
			)}

			<Handle
				type='source'
				position={Position.Bottom}
				className={`!w-4 !h-4 !bg-indigo-500 !border-4 !opacity-100 ${isCurrent ? "!border-white bg-indigo-500" : "!border-white"}`}
			/>
		</div>
	);
}

const nodeTypes = {
	customRole: CustomRoleNode,
};

export default function CareerLadderNetwork({ allProgressions, userSkills, userProfile }) {
	const [nodes, setNodes, onNodesChange] = useNodesState([]);
	const [edges, setEdges, onEdgesChange] = useEdgesState([]);

	const { selectedJob, jobDetail, detailLoading, fetchJobDetail, closeDetail } = useCareerDetail();

	useEffect(() => {
		if (!allProgressions || allProgressions.length === 0) return;

		const newNodes = [];
		const newEdges = [];

		// Layout configuration for Ecosystem Full-Screen
		const X_START = 100;
		const X_SPACING = 450;
		const Y_START = 260; // Increased spacing as requested
		const Y_SPACING = 420; // Increased spacing as requested

		allProgressions.forEach((progression, pIndex) => {
			const { domain, eligible_levels, alternate_paths } = progression;
			const currentX = X_START + pIndex * X_SPACING;

			// 🏷️ Top Tier Domain Cards
			const domainNodeId = `domain-label-${domain}`;
			newNodes.push({
				id: domainNodeId,
				type: "default",
				position: { x: currentX, y: 50 },
				sourcePosition: "bottom",
				targetPosition: "top",
				data: {
					label: (
						<div
							className='p-6 text-left transition-all duration-300 shadow-lg pointer-events-none select-none rounded-2xl bg-gradient-to-br from-indigo-600 to-indigo-700 text-white hover:scale-[1.02]'
						>
							<div className='flex items-center gap-2 mb-3'>
								<span className='px-3 py-1 text-[10px] font-black tracking-tight text-indigo-900 uppercase bg-white rounded-full'>
									DOMAIN
								</span>
							</div>

							<h3 className='mb-1 text-xl font-bold capitalize text-white/95'>{domain.replace(/_/g, " ")}</h3>
							<p className='text-sm text-white/80'>
								{progression.total_levels_in_domain || eligible_levels?.length || 0} career levels
							</p>
						</div>
					),
				},
				style: { background: "transparent", border: "none", width: 320 },
				draggable: false,
				selectable: false,
			});

			const mainSequence = (eligible_levels || []).map(level => ({
				...level,
				role_title: level.role_title || "Unknown Role"
			}));

			// Connect Domain Header to the first node
			if (mainSequence.length > 0) {
				newEdges.push({
					id: `edge-${domain}-to-${mainSequence[0].role_id}`,
					source: domainNodeId,
					target: `node-${domain}-${mainSequence[0].level}-${mainSequence[0].role_id}`,
					type: "smoothstep",
					animated: true,
					style: { stroke: "#d1d5db", strokeWidth: 3, strokeDasharray: "5,5" },
				});
			}

			mainSequence.forEach((level, index) => {
				const isAchievable = level.readiness_score >= 0.4;
				const isCurrent = level.is_current;
				const isLocked = level.readiness_score < 0.2 && !isCurrent;

				const nodeId = `node-${domain}-${level.level}-${level.role_id}`;
				newNodes.push({
					id: nodeId,
					type: "customRole",
					position: { x: currentX + 20, y: Y_START + index * Y_SPACING },
					data: {
						level: level.level,
						roleTitle: level.role_title,
						expRange: level.experience_range,
						readiness: level.readiness_score,
						isCurrent,
						isAchievable,
						isLocked,
						rawLevel: level,
						domain: domain,
						nextRole: index < mainSequence.length - 1 ? mainSequence[index + 1] : null,
						onNodeClick: () => {
							const nextRole = index < mainSequence.length - 1 ? mainSequence[index + 1] : null;
							const recommendationObj = {
								...level, // Spread enriched data from backend (scores, breakdown, clusters)
								role_id: level.role_id,
								role_title: level.role_title || level.role || "Unknown Role",
								domain: domain,
								next_role: nextRole?.role_id,
								next_role_title: nextRole?.role_title,
								skill_gap: {
									matched_skills: level.matched_skills ?? [],
									missing_skills: level.missing_skills ?? [],
									readiness_score: level.readiness_score ?? 0,
								},
								// Ensure top-level scores are mapped correctly for the modal
								match_score: level.match_score ?? level.readiness_score ?? 0,
								readiness_score: level.readiness_score ?? 0,
								confidence_score: level.confidence_score ?? 1.0,
								description: level.description ?? level.explanation ?? "",
								experience_range: level.experience_range ?? "",
							};
							// Pass the formatted object to fetchJobDetail to show the CareerDetailModal
							fetchJobDetail(recommendationObj, userSkills);
						},
					},
				});

				if (index > 0) {
					const prevNodeId = `node-${domain}-${mainSequence[index - 1].level}-${mainSequence[index - 1].role_id}`;
					newEdges.push({
						id: `edge-${domain}-${mainSequence[index - 1].role_id}-${level.role_id}`,
						source: prevNodeId,
						target: nodeId,
						type: "smoothstep",
						animated: true,
						style: { stroke: "#6366f1", strokeWidth: 4 },
						markerEnd: {
							type: MarkerType.ArrowClosed,
							color: "#6366f1",
						},
					});
				}
			});

			if (alternate_paths && alternate_paths.length > 0) {
				alternate_paths.forEach((branch, bIndex) => {
					const fromNode = newNodes.find((n) => n.id.startsWith(`node-${domain}-${branch.from_level}-`));
					if (fromNode) {
						const bId = `node-alt-${domain}-${branch.role_id}`;
						newNodes.push({
							id: bId,
							type: "customRole",
							position: {
								x: fromNode.position.x + 350,
								y: fromNode.position.y + 160 + bIndex * 200,
							},
							data: {
								level: `${branch.from_level} (Alt)`,
								roleTitle: branch.role_title,
								expRange: branch.description,
								readiness: 0,
								isCurrent: false,
								isAchievable: false,
								isLocked: true,
								rawLevel: branch,
								domain: domain,
								onNodeClick: () => {
									const recommendationObj = {
										role_id: branch.role_id,
										role_title: branch.role_title,
										domain: domain,
										match_score: 0,
										skill_gap: {
											matched_skills: [],
											missing_skills: branch.top_skills || [],
											readiness_score: 0,
										},
									};
									fetchJobDetail(recommendationObj, userSkills);
								},
							},
						});

						newEdges.push({
							id: `edge-branch-${domain}-${branch.from_level}-${branch.role_id}`,
							source: fromNode.id,
							target: bId,
							type: "smoothstep",
							animated: false,
							style: {
								stroke: "#d1d5db",
								strokeWidth: 3,
								strokeDasharray: "8,8",
							},
							markerEnd: {
								type: MarkerType.ArrowClosed,
								color: "#d1d5db",
							},
						});
					}
				});
			}
		});

		setNodes(newNodes);
		setEdges(newEdges);
	}, [allProgressions, fetchJobDetail, setEdges, setNodes, userSkills]);

	return (
		<div className='relative w-full h-[calc(100vh-140px)] min-h-[600px] bg-white overflow-hidden'>
			<ReactFlow
				nodes={nodes}
				edges={edges}
				onNodesChange={onNodesChange}
				onEdgesChange={onEdgesChange}
				nodeTypes={nodeTypes}
				nodesDraggable={false}
				nodesConnectable={false}
				elementsSelectable={true}
				nodesFocusable={true}
				panOnDrag={true}
				zoomOnScroll={true}
				fitView
				fitViewOptions={{ padding: 0.1 }}
				minZoom={0.1}
				maxZoom={1.5}
				defaultEdgeOptions={{ zIndex: 0 }}>
				<Background color='#e2e8f0' gap={40} size={1} />
				<Controls className='bg-white border-gray-200 !shadow-lg fill-gray-600' />
				<MiniMap
					nodeColor={(n) => {
						if (n.data?.isCurrent) return "#3b82f6";
						if (n.data?.isAchievable) return "#cbd5e1";
						return "#f1f5f9";
					}}
					maskColor='rgba(255, 255, 255, 0.7)'
					className='!bg-white/80 !backdrop-blur-xl !rounded-3xl !border !border-gray-200 !shadow-xl !bottom-8 !right-8'
				/>
			</ReactFlow>

			<CareerDetailModal
				isOpen={!!selectedJob}
				onClose={closeDetail}
				jobDetail={jobDetail}
				isLoading={detailLoading}
				userProfile={userProfile}
			/>
		</div>
	);
}
