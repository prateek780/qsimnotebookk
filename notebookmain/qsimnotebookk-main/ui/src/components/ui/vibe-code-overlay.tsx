"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle, BookOpen, Code, ExternalLink, X } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface VibeCodeOverlayProps {
  isVisible: boolean
  onClose: () => void
  onOpenNotebook?: () => void
}

export function VibeCodeOverlay({ isVisible, onClose, onOpenNotebook }: VibeCodeOverlayProps) {
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    if (isVisible) {
      setIsAnimating(true)
    }
  }, [isVisible])

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.8, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.8, y: 20 }}
            transition={{ type: "spring", damping: 20, stiffness: 300 }}
            className="relative max-w-2xl w-full mx-4"
          >
            <Card className="border-red-500/50 bg-slate-900/95 text-white shadow-2xl">
              <CardHeader className="text-center relative">
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-2 top-2 h-8 w-8 text-slate-400 hover:text-white"
                  onClick={onClose}
                >
                  <X className="h-4 w-4" />
                </Button>
                
                <div className="flex items-center justify-center mb-4">
                  <motion.div
                    animate={{ rotate: isAnimating ? [0, -10, 10, -10, 0] : 0 }}
                    transition={{ duration: 0.5, repeat: isAnimating ? Infinity : 0, repeatDelay: 2 }}
                    className="bg-red-500/20 p-3 rounded-full"
                  >
                    <AlertTriangle className="h-8 w-8 text-red-400" />
                  </motion.div>
                </div>
                
                <CardTitle className="text-2xl font-bold text-red-400 mb-2">
                  Simulation Blocked
                </CardTitle>
                
                <motion.div
                  animate={{ scale: isAnimating ? [1, 1.05, 1] : 1 }}
                  transition={{ duration: 1, repeat: isAnimating ? Infinity : 0, repeatDelay: 1 }}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg text-lg font-bold"
                >
                  🎓 VIBE CODE BB84 ALGORITHM USING THE HINTS PROVIDED TO RUN THE SIMULATION
                </motion.div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <div className="text-center">
                  <CardDescription className="text-slate-300 text-lg">
                    The quantum simulation requires your BB84 implementation to function.
                    <br />
                    <strong className="text-white">No hardcoded fallbacks available!</strong>
                  </CardDescription>
                </div>

                <div className="grid gap-4">
                  <div className="flex items-start gap-3 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                    <div className="bg-blue-500/20 p-2 rounded-full flex-shrink-0">
                      <BookOpen className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-blue-400 mb-1">Step 1: Open Jupyter Notebook</h4>
                      <p className="text-sm text-slate-300">
                        Launch <code className="bg-slate-700 px-1 rounded">quantum_networking_interactive.ipynb</code>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                    <div className="bg-green-500/20 p-2 rounded-full flex-shrink-0">
                      <Code className="h-5 w-5 text-green-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-green-400 mb-1">Step 2: Implement BB84 Protocol</h4>
                      <p className="text-sm text-slate-300">
                        Follow the provided hints to implement:
                      </p>
                      <ul className="text-xs text-slate-400 mt-1 space-y-1">
                        <li>• Qubit generation and sending</li>
                        <li>• Quantum measurement and basis reconciliation</li>
                        <li>• Error rate estimation for security</li>
                      </ul>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                    <div className="bg-purple-500/20 p-2 rounded-full flex-shrink-0">
                      <ExternalLink className="h-5 w-5 text-purple-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-purple-400 mb-1">Step 3: Connect to Simulation</h4>
                      <p className="text-sm text-slate-300">
                        Use the notebook bridge to connect your implementation
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  {onOpenNotebook && (
                    <Button 
                      onClick={onOpenNotebook}
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                    >
                      <BookOpen className="h-4 w-4 mr-2" />
                      Open Notebook
                    </Button>
                  )}
                  <Button 
                    variant="outline" 
                    onClick={onClose}
                    className="flex-1 border-slate-600 text-slate-300 hover:text-white"
                  >
                    I'll Implement Later
                  </Button>
                </div>

                <div className="text-center pt-2 border-t border-slate-700">
                  <p className="text-xs text-slate-500">
                    This is an educational simulation - students must "vibe code" to proceed! 🚀
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
