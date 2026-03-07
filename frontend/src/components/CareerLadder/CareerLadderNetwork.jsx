import React, { useState, useEffect, useCallback } from 'react';
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
import { FaStar, FaLock, FaCheckCircle, FaProjectDiagram } from 'react-icons/fa';
import LevelDetailModal from './LevelDetailModal';

// Custom Node Component to look beautiful
function CustomRoleNode({ data }) {
  const { level, isCurrent, isAchievable, isLocked, roleTitle, expRange, readiness, onNodeClick } = data;

  let bgClass = "bg-white border-2 border-purple-200";
  let textClass = "text-gray-800";
  let subTextClass = "text-gray-500";
  
  if (isCurrent) {
    bgClass = "bg-gradient-to-br from-purple-600 to-indigo-600 text-white border-2 border-indigo-300 shadow-xl scale-105 z-10";
    textClass = "text-white";
    subTextClass = "text-indigo-100";
  } else if (isAchievable) {
    bgClass = "bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-400 hover:shadow-lg transition-shadow";
  } else if (isLocked) {
    bgClass = "bg-gray-50 border-2 border-gray-300 opacity-80 hover:opacity-100 transition-opacity";
  }

  return (
    <div 
      className={`rounded-2xl p-5 w-64 cursor-pointer transition-transform hover:-translate-y-1 shadow-md ${bgClass}`}
      onClick={() => onNodeClick(data.rawLevel)}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3 bg-purple-500 border-2 border-white" />
      
      <div className="flex justify-between items-start mb-3">
        <span className={`text-xs font-bold px-3 py-1 rounded-full shadow-sm ${isCurrent ? 'bg-white/20 text-white backdrop-blur-sm' : 'bg-purple-100 text-purple-700'}`}>
          Level {level}
        </span>
        {isCurrent && <FaStar className="text-yellow-400 text-xl animate-pulse" title="Your Current Position" />}
        {isLocked && !isCurrent && <FaLock className="text-gray-400 text-lg" title="Locked" />}
        {isAchievable && !isCurrent && readiness >= 0.7 && <FaCheckCircle className="text-blue-500 text-lg" title="Ready to transition!" />}
      </div>
      
      <h3 className={`font-bold text-lg leading-tight mb-1 ${textClass}`}>
        {roleTitle}
      </h3>
      <p className={`text-xs font-medium ${subTextClass}`}>
        {expRange}
      </p>

      {!isCurrent && (
         <div className="mt-4 pt-4 border-t border-black/5">
           <div className="flex justify-between text-xs mb-1.5 font-medium">
             <span className={isLocked ? "text-gray-500" : "text-gray-700"}>Readiness:</span>
             <span className={`font-bold ${isLocked ? "text-gray-500" : "text-purple-700"}`}>
               {Math.round(readiness * 100)}%
             </span>
           </div>
           <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden shadow-inner">
             <div 
               className={`h-full rounded-full transition-all duration-1000 ${isAchievable ? 'bg-gradient-to-r from-blue-400 to-purple-500' : 'bg-gray-400'}`} 
               style={{ width: `${readiness * 100}%` }} 
             />
           </div>
         </div>
      )}

      {isCurrent && (
        <div className="mt-4 pt-3 border-t border-white/20 text-xs font-medium text-indigo-100 flex items-center gap-1.5">
           <span className="flex h-2 w-2 relative">
             <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
             <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-400"></span>
           </span>
           You are here
        </div>
      )}

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-purple-500 border-2 border-white" />
    </div>
  );
}

// Register custom node types
const nodeTypes = {
  customRole: CustomRoleNode
};

export default function CareerLadderNetwork({ allProgressions, userSkills }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!allProgressions || allProgressions.length === 0) return;

    const newNodes = [];
    const newEdges = [];

    // Layout configuration
    const X_START = 50;
    const X_SPACING = 380; // horizontal spacing between paths
    const Y_START = 120;
    const Y_SPACING = 250;

    // Build the grid mapping all progressions alongside one another
    allProgressions.forEach((progression, pIndex) => {
      const { domain, current_position, progression_path, alternate_paths } = progression;
      
      const currentX = X_START + (pIndex * X_SPACING);

      // Heading label node for each domain
      const domainNodeId = `domain-label-${domain}`;
      newNodes.push({
        id: domainNodeId,
        type: 'default',
        position: { x: currentX, y: 20 },
        data: { label: <div className="text-xl font-extrabold bg-gradient-to-r from-purple-700 to-indigo-700 bg-clip-text text-transparent">{domain.replace(/_/g, ' ')}</div> },
        style: { background: 'transparent', border: 'none', width: 256, textAlign: 'center' },
        draggable: false,
        selectable: false
      });

      // Construct single flat array for the main sequence
      const mainSequence = [
        { ...current_position, is_current: true, readiness_score: 1.0 },
        ...progression_path
      ];

      // Build main nodes & sequence edges
      mainSequence.forEach((level, index) => {
        const isAchievable = level.readiness_score >= 0.4;
        const isCurrent = level.is_current;
        const isLocked = level.readiness_score < 0.2 && !isCurrent;

        const nodeId = `node-${domain}-${level.level}`;
        newNodes.push({
          id: nodeId,
          type: 'customRole',
          position: { x: currentX, y: Y_START + (index * Y_SPACING) },
          data: {
            level: level.level,
            roleTitle: level.role_title,
            expRange: level.experience_range,
            readiness: level.readiness_score,
            isCurrent,
            isAchievable,
            isLocked,
            rawLevel: level,
            onNodeClick: (nodeData) => {
              setSelectedLevel(nodeData);
              setShowModal(true);
            }
          }
        });

        // Link to the previous node
        if (index > 0) {
          const prevLevel = mainSequence[index - 1].level;
          newEdges.push({
            id: `edge-${domain}-${prevLevel}-${level.level}`,
            source: `node-${domain}-${prevLevel}`,
            target: nodeId,
            type: 'smoothstep',
            animated: true,
            style: { stroke: '#8b5cf6', strokeWidth: 3 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#8b5cf6',
            },
          });
        }
      });

      // Handle Alternate Paths branching out
      if (alternate_paths && alternate_paths.length > 0) {
        alternate_paths.forEach((branch, bIndex) => {
          // Find node to branch from
          const fromNode = newNodes.find(n => n.id === `node-${domain}-${branch.from_level}`);
          if (fromNode) {
            const bId = `node-alt-${domain}-${branch.role_id}`;
            newNodes.push({
              id: bId,
              type: 'customRole',
              position: { 
                // Branch off slightly to the right, but overlapping somewhat into space
                x: fromNode.position.x + 300, 
                y: fromNode.position.y + 110 + (bIndex * 150) 
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
                onNodeClick: (nodeData) => {
                  const mappedData = {
                    ...nodeData,
                    level: branch.from_level,
                    matched_skills: [],
                    missing_skills: branch.top_skills || [],
                    readiness_score: 0,
                    estimated_time: '18-24 months',
                    difficulty: 'Hard'
                  };
                  setSelectedLevel(mappedData);
                  setShowModal(true);
                }
              }
            });

            // Draw dotted branching edge
            newEdges.push({
              id: `edge-branch-${domain}-${branch.from_level}-${branch.role_id}`,
              source: fromNode.id,
              target: bId,
              type: 'smoothstep',
              animated: false,
              style: { stroke: '#f59e0b', strokeWidth: 2, strokeDasharray: '5,5' },
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
    <div className="relative w-full h-[700px] border-2 border-gray-100 rounded-3xl bg-gray-50 overflow-hidden shadow-2xl">
      <div className="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-xl shadow-sm border border-gray-100 flex items-center gap-2">
        <FaProjectDiagram className="text-purple-600" />
        <span className="text-sm font-semibold text-gray-700">Interactive Network Map</span>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={2}
        defaultEdgeOptions={{ zIndex: 0 }}
      >
        <Background color="#cbd5e1" gap={24} size={2} />
        <Controls className="bg-white shadow-lg border-none rounded-xl overflow-hidden" />
        <MiniMap 
          nodeColor={(n) => {
            if (n.data?.isCurrent) return '#4f46e5';
            if (n.data?.isAchievable) return '#60a5fa';
            return '#e2e8f0';
          }}
          maskColor="rgba(250, 250, 250, 0.7)"
          className="rounded-xl shadow-lg border-2 border-white bg-white/50"
        />
      </ReactFlow>

      {/* Detail Modal shared with corresponding nodes */}
      {showModal && selectedLevel && (
        <LevelDetailModal
          level={selectedLevel}
          userSkills={userSkills}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}
