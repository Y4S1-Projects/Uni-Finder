import React, { useState, useEffect } from "react";
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
import {
  FaStar,
  FaLock,
  FaCheckCircle,
  FaProjectDiagram,
  FaBolt,
} from "react-icons/fa";

// 💠 Advanced Role Node for Light Ecosystem
function CustomRoleNode({ data }) {
  const {
    level,
    isCurrent,
    isAchievable,
    isLocked,
    roleTitle,
    expRange,
    readiness,
    onNodeClick,
  } = data;

  let bgClass = "border-2 hover:shadow-xl hover:scale-[1.02]";
  let nodeStyle = {
    background:
      "linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)",
    borderColor: "rgba(102, 126, 234, 0.3)",
  };
  let titleClass = "text-gray-800";
  let subTextClass = "text-gray-600";
  let glowClass = "";

  if (isCurrent) {
    bgClass =
      "bg-white border-2 border-indigo-400 shadow-[0_0_25px_rgba(99,102,241,0.3)] scale-105 z-50 ring-4 ring-indigo-500/10";
    titleClass = "text-indigo-900";
    subTextClass = "text-indigo-700";
    glowClass =
      "after:content-[''] after:absolute after:-inset-1 after:bg-indigo-500/10 after:blur-xl after:rounded-3xl after:-z-10";
    nodeStyle = {}; // reset style
  } else if (isLocked) {
    bgClass =
      "bg-slate-50 border-2 border-slate-200 opacity-60 grayscale-[0.3]";
    nodeStyle = {}; // reset style
  }

  return (
    <div
      className={`relative rounded-3xl p-6 w-[280px] transition-all duration-300 select-none group cursor-pointer ${bgClass} ${glowClass}`}
      style={nodeStyle}
      onClick={() => onNodeClick(data.rawLevel)}
    >
      <Handle
        type="target"
        position={Position.Top}
        className={`!w-4 !h-4 !bg-blue-500 !border-4 !opacity-100 ${isCurrent ? "!border-indigo-700" : "!border-white"}`}
      />

      <div className="flex justify-between items-start mb-4">
        <div
          className={`text-xs px-2 py-1 rounded-full font-semibold ${
            isCurrent
              ? "bg-indigo-50 border border-indigo-200 text-indigo-700"
              : "bg-purple-100 text-purple-700"
          }`}
        >
          TIER {level}
        </div>
        {isCurrent && (
          <div className="flex items-center gap-1.5 bg-yellow-100 px-2 py-1 rounded-full border border-yellow-300 shadow-sm">
            <FaStar className="text-yellow-500 text-xs animate-pulse" />
            <span className="text-[9px] font-bold text-yellow-700 uppercase tracking-tighter">
              Current
            </span>
          </div>
        )}
        {isLocked && !isCurrent && (
          <FaLock className="text-slate-400 text-sm" />
        )}
        {isAchievable && !isCurrent && readiness >= 0.7 && (
          <div className="bg-emerald-50 px-2 py-1 rounded-lg border border-emerald-200 flex items-center gap-1">
            <FaCheckCircle className="text-emerald-500 text-sm" />
            <span className="text-[9px] font-bold text-emerald-600 uppercase tracking-tighter">
              Ready
            </span>
          </div>
        )}
      </div>

      <h3
        className={`font-black text-xl leading-tight mb-2 tracking-tight transition-colors ${titleClass}`}
      >
        {roleTitle}
      </h3>

      <div
        className={`inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider py-1 px-3 rounded-md mb-4 ${isCurrent ? "bg-indigo-50" : "bg-slate-100"} ${subTextClass}`}
      >
        <FaBolt
          className={`${isCurrent ? "text-indigo-500" : "text-blue-500"} text-[10px]`}
        />
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
              className={`h-full rounded-full transition-all duration-1000 ${isAchievable ? "bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400" : "bg-slate-300"}`}
              style={{ width: `${readiness * 100}%` }}
            />
          </div>
        </div>
      )}

      {isCurrent && (
        <div className="mt-4 pt-4 border-t border-indigo-100 text-[10px] font-black uppercase tracking-widest text-indigo-500 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
          Syncing with Profile
        </div>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className={`!w-4 !h-4 !bg-indigo-500 !border-4 !opacity-100 ${isCurrent ? "!border-white bg-indigo-500" : "!border-white"}`}
      />
    </div>
  );
}

const nodeTypes = {
  customRole: CustomRoleNode,
};

export default function CareerLadderNetwork({ allProgressions, userSkills }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const { selectedJob, jobDetail, detailLoading, fetchJobDetail, closeDetail } =
    useCareerDetail();

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
      const { domain, current_position, eligible_levels, alternate_paths } =
        progression;
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
              className="p-6 rounded-xl text-white shadow-xl transition-all hover:shadow-2xl text-left pointer-events-none select-none"
              style={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              }}
            >
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs bg-white/20 px-3 py-1 rounded-full font-bold">
                  TIER 1
                </span>
                <span className="text-xs bg-yellow-400 px-3 py-1 rounded-full text-gray-900 font-bold uppercase tracking-tight">
                  DOMAIN
                </span>
              </div>

              <h3 className="text-xl font-bold mb-1 capitalize">
                {domain.replace(/_/g, " ")}
              </h3>
              <p className="text-sm text-white/80">
                {progression.total_levels_in_domain ||
                  eligible_levels?.length ||
                  0}{" "}
                career levels
              </p>
            </div>
          ),
        },
        style: { background: "transparent", border: "none", width: 320 },
        draggable: false,
        selectable: false,
      });

      const mainSequence = eligible_levels || [];

      // Connect Domain Header to the first node
      if (mainSequence.length > 0) {
        newEdges.push({
          id: `edge-${domain}-to-${mainSequence[0].level}`,
          source: domainNodeId,
          target: `node-${domain}-${mainSequence[0].level}`,
          type: "smoothstep",
          animated: true,
          style: { stroke: "#8b5cf6", strokeWidth: 3, strokeDasharray: "5,5" },
        });
      }

      mainSequence.forEach((level, index) => {
        const isAchievable = level.readiness_score >= 0.4;
        const isCurrent = level.is_current;
        const isLocked = level.readiness_score < 0.2 && !isCurrent;

        const nodeId = `node-${domain}-${level.level}`;
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
            nextRole:
              index < mainSequence.length - 1 ? mainSequence[index + 1] : null,
            onNodeClick: () => {
              const nextRole =
                index < mainSequence.length - 1
                  ? mainSequence[index + 1]
                  : null;
              const recommendationObj = {
                role_id: level.role_id,
                role_title: level.role_title,
                domain: domain,
                match_score: level.match_score || level.readiness_score || 0, // Use match_score from backend
                next_role: nextRole?.role_id,
                next_role_title: nextRole?.role_title,
                skill_gap: {
                  matched_skills: level.matched_skills || [],
                  missing_skills: level.missing_skills || [],
                  readiness_score: level.readiness_score || 0,
                },
              };
              // Pass the formatted object to fetchJobDetail to show the CareerDetailModal
              fetchJobDetail(recommendationObj, userSkills);
            },
          },
        });

        if (index > 0) {
          const prevLevel = mainSequence[index - 1].level;
          newEdges.push({
            id: `edge-${domain}-${prevLevel}-${level.level}`,
            source: `node-${domain}-${prevLevel}`,
            target: nodeId,
            type: "smoothstep",
            animated: true,
            style: { stroke: "rgba(99, 102, 241, 0.4)", strokeWidth: 4 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: "#6366f1",
            },
          });
        }
      });

      if (alternate_paths && alternate_paths.length > 0) {
        alternate_paths.forEach((branch, bIndex) => {
          const fromNode = newNodes.find(
            (n) => n.id === `node-${domain}-${branch.from_level}`,
          );
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
                stroke: "rgba(245, 158, 11, 0.3)",
                strokeWidth: 3,
                strokeDasharray: "8,8",
              },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: "#f59e0b",
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
    <div className="relative w-full h-[calc(100vh-140px)] min-h-[600px] bg-slate-50 overflow-hidden">
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
        defaultEdgeOptions={{ zIndex: 0 }}
      >
        <Background color="#cbd5e1" gap={40} size={1.5} />
        <Controls className="bg-white border-slate-200 !shadow-lg fill-slate-700" />
        <MiniMap
          nodeColor={(n) => {
            if (n.data?.isCurrent) return "#3b82f6";
            if (n.data?.isAchievable) return "#cbd5e1";
            return "#f1f5f9";
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
