"use client"

import { useRef, useEffect, useState, useCallback, forwardRef, useImperativeHandle, useLayoutEffect } from "react"
import { motion } from "framer-motion"
import { FabricJSCanvas, useFabricJSEditor } from 'fabricjs-react';
import { getLogger } from "@/helpers/simLogger"
import { SimulatorNode, SimulatorNodeOptions } from "../node/base/baseNode";
import { ConnectionManager } from "../node/connections/connectionManager";
import { KeyboardListener } from "./keyboard";
import { NetworkManager } from "../node/network/networkManager";
import { SimulationNodeType } from "../node/base/enums";
import { manager } from "../node/nodeManager";
import * as fabric from "fabric";
import "./canvas.scss";
import api from "@/services/api";
import { getNewNode } from "./utils";
import { WebSocketClient } from "@/services/socket";
import { importFromJSON } from "@/services/importService";
import { NetworkAnimationController } from "./animation";
import { networkStorage } from "@/services/storage";
import { toast } from "sonner";
import simulationState from "@/helpers/utils/simulationState";

import { debounce } from "lodash"; // Import debounce from lodash

interface NetworkCanvasProps {
  onNodeSelect: (node: any) => void
  isSimulationRunning: boolean
  simulationTime: number
  activeMessages?: any[]
}

export const NetworkCanvas = forwardRef(({ onNodeSelect, isSimulationRunning, simulationTime, activeMessages = [] }: NetworkCanvasProps, ref) => {
  // const canvasRef = useRef<HTMLCanvasElement>(null)
  const { editor, onReady } = useFabricJSEditor();
  const [nodes, setNodes] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);

  const logger = getLogger("Canvas");

  useLayoutEffect(() => {
    setTimeout(async () => {
      const socketHost = process.env.NODE_ENV === 'production' ? window.location.toString() : 'http://localhost:5174';
      const socketUrl = new URL(socketHost.replace("http", "ws"));
      socketUrl.pathname = "/api/ws";
      WebSocketClient.getInstance().connect(socketUrl.toString());

      NetworkAnimationController.getInstance(editor?.canvas as fabric.Canvas);
    }, 2500);
  }, [editor]);

  // useEffect(() => {
  //   debouncedCheckImport();
  // }, [editor])

  // For some unknown reason, two canvases are generated. So, we debounce the import check to avoid rending on unseen canvas.
  const debouncedCheckImport = debounce(async (canvas?: fabric.Canvas) => {
    const queryParams = new URLSearchParams(window.location.search);
    const lastOpenedTopologyID = queryParams.get("topologyID") || (await networkStorage.getLastOpenedTopologyID());

    let topologyID = null;
    console.log(lastOpenedTopologyID, simulationState.getWorldId());
    if (lastOpenedTopologyID) {
      if (lastOpenedTopologyID === simulationState.getWorldId()) {
        return;
      }
      topologyID = lastOpenedTopologyID;
    }

    if (topologyID) {
      try {
        const savedTopology = await api.getTopology(topologyID);
        if (savedTopology?.zones) {
          canvas = (editor?.canvas as fabric.Canvas) || canvas;
          if (!canvas) {
            logger.warn("Canvas not found in editor", editor);
            return;
          }
          importFromJSON(savedTopology, canvas);
          onFirstNodeAdded(canvas);
        }
      } catch (e) {
        toast("Topology not found!", {
          onAutoClose: (t) => {
            window.location.href = "/";
          },
        });
      }
    }
  }, 1300);

  // Update canvas when simulation state changes
  useEffect(() => {
    // Animate quantum states if simulation is running
    if (isSimulationRunning) {
      // Animation logic would go here
    }
  }, [isSimulationRunning, simulationTime, activeMessages])


  const drawMessagePacket = (ctx: CanvasRenderingContext2D, x: number, y: number, protocol: string) => {
    // Draw different packet styles based on protocol
    console.log("Draw Packet")
  }

  const animatePacket = async () => {
    // Draw active messages
    activeMessages.forEach((message) => {
      const sourceNode = nodes[message.source]
      const targetNode = nodes[message.target]

      if (sourceNode && targetNode) {
        // Calculate message position based on progress
        const progress = (simulationTime - message.startTime) / message.duration
      }
    })
  }

  const fabricRendered = async (canvas: fabric.Canvas) => {
    // Prevent multiple initializations
    // if (fabricInitialized.current) return;
    // fabricInitialized.current = true;

    if (editor?.canvas) {
      console.log("Canvas already initialized, skipping");
      return;
    }


    onReady(canvas);

    debouncedCheckImport(canvas);

    canvas.on('mouse:down', (e) => {
      const selectedNode = e.target;
      onNodeSelect(selectedNode);
    })
  }


  const onSimulatorEvent = (event: any) => {
    console.log(event)
  }

  const onFirstNodeAdded = (canvas?: fabric.Canvas) => {
    ConnectionManager.getInstance(editor?.canvas || canvas);
    KeyboardListener.getInstance(editor?.canvas || canvas);
    NetworkManager.getInstance(editor?.canvas || canvas);
    // api.startAutoUpdateNetworkTopology();
  };

  const addNodeToCanvas = (fabricObject: fabric.FabricObject) => {
    editor?.canvas.add(fabricObject);

    if (editor?.canvas.getObjects().length === 1) {
      onFirstNodeAdded();
    }
  };

  const createNewNode = async (type: SimulationNodeType, x: number, y: number) => {
    const nodeManager = manager;

    if (!nodeManager) {
      logger.error("NodeManager is not initialized.");
      return;
    }

    const newNode = getNewNode(type, x, y, editor?.canvas as fabric.Canvas)

    if (newNode) {
      addNodeToCanvas(newNode); // Add Fabric.js object to canvas
      setNodes((prevNodes): any => [...prevNodes, newNode.getNodeInfo()]);
    }
  }

  const createNodeCallback = useCallback(createNewNode, [editor]); // Dependency array includes editor and createNode

  // Handle drag and drop events
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    // Only set to false if we're leaving the canvas area entirely
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    try {
      const dragData = JSON.parse(e.dataTransfer.getData('application/json'));
      
      if (dragData.nodeType) {
        // Get the canvas bounds to calculate relative position
        const canvasRect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - canvasRect.left;
        const y = e.clientY - canvasRect.top;
        
        console.log(`Creating ${dragData.nodeName} at position (${x}, ${y})`);
        
        // Map the action type to the appropriate creation function
        const actionMap: any = {
          createClassicalHost: () => createNodeCallback(SimulationNodeType.CLASSICAL_HOST, x, y),
          createClassicalRouter: () => createNodeCallback(SimulationNodeType.CLASSICAL_ROUTER, x, y),
          createQuantumHost: () => createNodeCallback(SimulationNodeType.QUANTUM_HOST, x, y),
          createQuantumAdapter: () => createNodeCallback(SimulationNodeType.QUANTUM_ADAPTER, x, y),
          createQuantumRepeater: () => createNodeCallback(SimulationNodeType.QUANTUM_REPEATER, x, y),
          createInternetExchange: () => createNodeCallback(SimulationNodeType.INTERNET_EXCHANGE, x, y),
          createC2QConverter: () => createNodeCallback(SimulationNodeType.CLASSIC_TO_QUANTUM_CONVERTER, x, y),
          createQ2CConverter: () => createNodeCallback(SimulationNodeType.QUANTUM_TO_CLASSIC_CONVERTER, x, y),
          createZone: () => createNodeCallback(SimulationNodeType.ZONE, x, y),
          createNetwork: () => createNodeCallback(SimulationNodeType.CLASSICAL_NETWORK, x, y)
        };
        
        if (actionMap[dragData.nodeType]) {
          actionMap[dragData.nodeType]();
        } else {
          console.error(`No handler found for action: ${dragData.nodeType}`);
        }
      }
    } catch (error) {
      console.error('Error parsing drag data:', error);
    }
  };

  useImperativeHandle(ref, () => ({
    handleCreateClassicalHost: () => {
      createNodeCallback(SimulationNodeType.CLASSICAL_HOST, 50, 50);
    },
    handleCreateClassicalRouter: () => {
      createNodeCallback(SimulationNodeType.CLASSICAL_ROUTER, 150, 50);
    },
    handleCreateQuantumHost: () => {
      createNodeCallback(SimulationNodeType.QUANTUM_HOST, 250, 50);
    },
    handleCreateQuantumRepeater: () => {
      createNodeCallback(SimulationNodeType.QUANTUM_REPEATER, 350, 50);
    },
    handleCreateQuantumAdapter: () => {
      createNodeCallback(SimulationNodeType.QUANTUM_ADAPTER, 450, 50);
    },
    handleCreateInternetExchange: () => {
      createNodeCallback(SimulationNodeType.INTERNET_EXCHANGE, 550, 50);
    },
    handleCreateC2QConverter: () => {
      createNodeCallback(SimulationNodeType.CLASSIC_TO_QUANTUM_CONVERTER, 650, 50);
    },
    handleCreateQ2CConverter: () => {
      createNodeCallback(SimulationNodeType.QUANTUM_TO_CLASSIC_CONVERTER, 750, 50);
    },
    handleCreateZone: () => {
      createNodeCallback(SimulationNodeType.ZONE, 50, 200);
    },
    handleCreateNetwork: () => {
      createNodeCallback(SimulationNodeType.CLASSICAL_NETWORK, 50, 300);
    }
  }));

  return (
    <div 
      className={`w-full h-full bg-slate-900 relative transition-all duration-200 ${isDragOver ? 'bg-slate-800 ring-2 ring-blue-500 ring-opacity-50' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* <canvas
        ref={canvasRef}
        className="w-full h-full"
        onClick={(e) => {
          // Handle node selection logic here
          // For now, just a placeholder
          const rect = e.currentTarget.getBoundingClientRect()
          const x = e.clientX - rect.left
          const y = e.clientY - rect.top

          // Check if a node was clicked
          // This would be replaced with your actual node detection logic
          console.log(`Canvas clicked at (${x}, ${y})`)
        }}
      /> */}

      <FabricJSCanvas className="canvas-container w-full h-full" onReady={fabricRendered} />

      {/* Drag and Drop Overlay */}
      {isDragOver && (
        <div className="absolute inset-0 flex items-center justify-center bg-blue-900/20 backdrop-blur-sm pointer-events-none">
          <div className="bg-slate-800/90 px-6 py-4 rounded-lg border border-blue-500 shadow-lg">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-white font-medium">Drop component here to add to canvas</span>
            </div>
          </div>
        </div>
      )}

      {/* Overlay elements for interactive components */}
      <div className="absolute top-4 right-4 bg-slate-800/80 backdrop-blur-sm p-2 rounded-md">
        <div className="text-xs text-slate-400">Simulation Time</div>
        <div className="text-lg font-mono">{simulationTime.toFixed(2)}s</div>
      </div>

      {/* Visual indicator for simulation running state */}
      {isSimulationRunning && (
        <motion.div
          className="absolute top-4 left-4 bg-green-500 h-3 w-3 rounded-full"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY }}
        />
      )}

      {/* Message count indicator */}
      {activeMessages.length > 0 && (
        <div className="absolute bottom-20 right-4 bg-slate-800/80 backdrop-blur-sm p-2 rounded-md">
          <div className="text-xs text-slate-400">Active Messages</div>
          <div className="text-lg font-mono">{activeMessages.length}</div>
        </div>
      )}
    </div>
  )
});
