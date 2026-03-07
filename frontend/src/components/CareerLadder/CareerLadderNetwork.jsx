import React, { useState, useEffect } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { CareerDetailModal } from '../career/CareerDetailModal';
import { useCareerDetail } from '../../hooks/useCareerRecommendations';
import { FaStar, FaLock, FaCheckCircle, FaProjectDiagram, FaBolt } from 'react-icons/fa';

// 💠 Advanced Role Node for Light Ecosystem
function CustomRoleNode({ data }) {
  const { level, isCurrent, isAchievable, isLocked, roleTitle, expRange, readiness, onNodeClick } = data;

  let bgClass = "bg-white border-slate-200 hover:border-slate-300 hover:shadow-lg";
  let titleClass = "text-slate-900";
  let subTextClass = "text-slate-500";
  let glowClass = "";
  
  if (isCurrent) {
    bgClass = "bg-gradient-to-br from-blue-600 to-indigo-700 border-transparent shadow-[0_10px_30px_rgba(59,130,246,0.25)] scale-105 z-50";
    titleClass = "text-white";
    subTextClass = "text-blue-100/90";
    glowClass = "after:content-[''] after:absolute after:-inset-1 after:bg-blue-500/20 after:blur-xl after:rounded-3xl after:-z-10";
  } else if (isAchievable) {
    bgClass = "bg-white border-blue-200 hover:border-blue-400 shadow-md";
  } else if (isLocked) {
    bgClass = "bg-slate-50 border-slate-200 opacity-60 grayscale-[0.3]";
  }

  return (
    <div 
      className={`relative rounded-3xl p-6 w-[280px] cursor-pointer transition-all duration-300 border select-none group ${bgClass} ${glowClass}`}
      onClick={() => onNodeClick(data.rawLevel)}
    >
      <Handle type="target" position={Position.Top} className={`!w-4 !h-4 !bg-blue-500 !border-4 !opacity-100 ${isCurrent ? '!border-indigo-700' : '!border-white'}`} />
      
      <div className="flex justify-between items-start mb-4">
        <div className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-lg border shadow-sm ${
          isCurrent ? 'bg-white/20 border-white/20 text-white' : 'bg-slate-100 border-slate-200 text-slate-500'
        }`}>
          Tier {level}
        </div>
        {isCurrent && (
          <div className="flex items-center gap-1.5 bg-yellow-400/10 px-2 py-1 rounded-lg border border-yellow-400/20">
            <FaStar className="text-yellow-400 text-sm animate-pulse" />
            <span className="text-[9px] font-bold text-yellow-400 uppercase tracking-tighter">Current</span>
          </div>
        )}
        {isLocked && !isCurrent && <FaLock className="text-slate-400 text-sm" />}
        {isAchievable && !isCurrent && readiness >= 0.7 && (
          <div className="bg-emerald-50 px-2 py-1 rounded-lg border border-emerald-200 flex items-center gap-1">
            <FaCheckCircle className="text-emerald-500 text-sm" />
            <span className="text-[9px] font-bold text-emerald-600 uppercase tracking-tighter">Ready</span>
          </div>
        )}
      </div>
      
      <h3 className={`font-black text-xl leading-tight mb-2 tracking-tight transition-colors ${titleClass}`}>
        {roleTitle}
      </h3>
      
      <div className={`inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider py-1 px-3 rounded-md mb-4 ${isCurrent ? 'bg-black/20' : 'bg-slate-100'} ${subTextClass}`}>
        <FaBolt className={`${isCurrent ? 'text-yellow-400' : 'text-blue-500'} text-[10px]`} />
        {expRange}
      </div>

      {!isCurrent && (
         <div className="mt-4 pt-4 border-t border-slate-100">
           <div className="flex justify-between text-[10px] mb-2 font-black uppercase tracking-widest text-slate-400">
             <span>Progression Index</span>
             <span className={isLocked ? "text-slate-400" : "text-blue-600"}>
               {Math.round(readiness * 100)}%
             </span>
           </div>
           <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden shadow-inner border border-slate-200">
             <div 
               className={`h-full rounded-full transition-all duration-1000 ${isAchievable ? 'bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400' : 'bg-slate-300'}`} 
               style={{ width: `${readiness * 100}%` }} 
             />
           </div>
         </div>
      )}

      {isCurrent && (
        <div className="mt-4 pt-4 border-t border-white/20 text-[10px] font-black uppercase tracking-widest text-blue-100 flex items-center gap-2">
           <div className="w-2 h-2 rounded-full bg-blue-300 animate-ping" />
           Syncing with Profile
        </div>
      )}

      <Handle type="source" position={Position.Bottom} className={`!w-4 !h-4 !bg-indigo-500 !border-4 !opacity-100 ${isCurrent ? '!border-indigo-700' : '!border-white'}`} />
    </div>
  );
}

const nodeTypes = {
  customRole: CustomRoleNode
};

export default function CareerLadderNetwork({ allProgressions, userSkills }) {
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
    const Y_START = 200;
    const Y_SPACING = 420; // Increased spacing as requested

    allProgressions.forEach((progression, pIndex) => {
      const { domain, current_position, progression_path, alternate_paths } = progression;
      const currentX = X_START + (pIndex * X_SPACING);

      // 🏷️ Domain Header Label (Styled like a sector HUD)
      const domainNodeId = `domain-label-${domain}`;
      newNodes.push({
        id: domainNodeId,
        type: 'default',
        position: { x: currentX, y: 50 },
        data: { label: (
          <div className="relative group/domain">
            <div className="absolute -inset-4 bg-blue-500/10 blur-2xl rounded-full opacity-0 group-hover/domain:opacity-100 transition-opacity" />
            <div className="relative flex flex-col items-center gap-2">
               <div className="w-10 h-1 border-t-2 border-blue-500/30 mb-2" />
               <div className="text-[10px] font-black text-blue-600 uppercase tracking-[.3em] font-mono">Industry Sector</div>
               <div className="text-3xl font-black text-slate-800 tracking-tighter drop-shadow-sm">
                 {domain.replace(/_/g, ' ')}
               </div>
               <div className="w-2 h-2 rounded-full bg-blue-500/40 border border-blue-500/60 mt-1" />
            </div>
          </div>
        ) },
        style: { background: 'transparent', border: 'none', width: 320, textAlign: 'center' },
        draggable: false,
        selectable: false
      });

      const mainSequence = [
        { ...current_position, is_current: true, readiness_score: 1.0 },
        ...progression_path
      ];

      mainSequence.forEach((level, index) => {
        const isAchievable = level.readiness_score >= 0.4;
        const isCurrent = level.is_current;
        const isLocked = level.readiness_score < 0.2 && !isCurrent;

        const nodeId = `node-${domain}-${level.level}`;
        newNodes.push({
          id: nodeId,
          type: 'customRole',
          position: { x: currentX + 20, y: Y_START + (index * Y_SPACING) },
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
                role_id: level.role_id,
                role_title: level.role_title,
                domain: domain,
                match_score: level.readiness_score || 0,
                next_role: nextRole?.role_id,
                next_role_title: nextRole?.role_title,
                skill_gap: {
                  matched_skills: level.matched_skills || [],
                  missing_skills: level.missing_skills || [],
                  readiness_score: level.readiness_score || 0
                }
              };
              // Pass the formatted object to fetchJobDetail to show the CareerDetailModal
              fetchJobDetail(recommendationObj, userSkills);
            }
          }
        });

        if (index > 0) {
          const prevLevel = mainSequence[index - 1].level;
          newEdges.push({
            id: `edge-${domain}-${prevLevel}-${level.level}`,
            source: `node-${domain}-${prevLevel}`,
            target: nodeId,
            type: 'smoothstep',
            animated: true,
            style: { stroke: 'rgba(99, 102, 241, 0.4)', strokeWidth: 4 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#6366f1',
            },
          });
        }
      });

      if (alternate_paths && alternate_paths.length > 0) {
        alternate_paths.forEach((branch, bIndex) => {
          const fromNode = newNodes.find(n => n.id === `node-${domain}-${branch.from_level}`);
          if (fromNode) {
            const bId = `node-alt-${domain}-${branch.role_id}`;
            newNodes.push({
              id: bId,
              type: 'customRole',
              position: { 
                x: fromNode.position.x + 350, 
                y: fromNode.position.y + 160 + (bIndex * 200) 
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
                      readiness_score: 0
                    }
                  };
                  fetchJobDetail(recommendationObj, userSkills);
                }
              }
            });

            newEdges.push({
              id: `edge-branch-${domain}-${branch.from_level}-${branch.role_id}`,
              source: fromNode.id,
              target: bId,
              type: 'smoothstep',
              animated: false,
              style: { stroke: 'rgba(245, 158, 11, 0.3)', strokeWidth: 3, strokeDasharray: '8,8' },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: '#f59e0b',
              },
            });
          }
        });
      }
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [allProgressions, setNodes, setEdges]);

  return (
    <div className="relative w-full h-full bg-slate-50 overflow-hidden">
      {/* 🧩 HUD Elements */}
      <div className="absolute top-6 left-8 z-50 flex items-center gap-4 bg-white/80 backdrop-blur-md px-6 py-3 rounded-2xl border border-slate-200 shadow-md">
        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse shadow-[0_0_10px_rgba(59,130,246,0.6)]" />
        <div className="flex flex-col">
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none">Status</span>
          <span className="text-xs font-bold text-slate-800">System Live: Mapping Active Paths</span>
        </div>
        <div className="h-6 w-px bg-slate-200 mx-2" />
        <div className="flex items-center gap-2 text-xs font-bold text-slate-500">
           <FaProjectDiagram />
           <span>Ecosystem Map</span>
        </div>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.1 }}
        minZoom={0.1}
        maxZoom={1.5}
        defaultEdgeOptions={{ zIndex: 0 }}
      >
        <Background color="#cbd5e1" gap={40} size={1.5} />
        <Controls className="bg-white border-slate-200 !shadow-lg fill-slate-700" />
        <MiniMap 
          nodeColor={(n) => {
            if (n.data?.isCurrent) return '#3b82f6';
            if (n.data?.isAchievable) return '#cbd5e1';
            return '#f1f5f9';
          }}
          maskColor="rgba(248, 250, 252, 0.7)"
          className="!bg-white/80 !backdrop-blur-xl !rounded-3xl !border !border-slate-200 !shadow-xl !bottom-8 !right-8"
        />
      </ReactFlow>

      <CareerDetailModal
        isOpen={!!selectedJob}
        onClose={closeDetail}
        jobDetail={jobDetail}
        isLoading={detailLoading}
      />
    </div>
  );
}
