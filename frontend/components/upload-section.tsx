"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Upload, FileAudio, Loader2 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ResultsDisplay } from "@/components/results-display"

interface AnalysisResult {
  fileName: string
  duration: number
  detections: Array<{
    timestamp: string
    content: string
    severity: "high" | "medium" | "low"
    category: string
  }>
}

export function UploadSection() {
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [results, setResults] = useState<AnalysisResult | null>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      setSelectedFile(files[0])
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      setSelectedFile(files[0])
    }
  }, [])

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setIsProcessing(true)

    // Simulate processing
    await new Promise((resolve) => setTimeout(resolve, 3000))

    // Mock results
    setResults({
      fileName: selectedFile.name,
      duration: 180,
      detections: [
        {
          timestamp: "00:00:45",
          content: "Detected potentially extremist rhetoric",
          severity: "high",
          category: "Extremist Content",
        },
        {
          timestamp: "00:01:23",
          content: "Inappropriate language detected",
          severity: "medium",
          category: "Profanity",
        },
        {
          timestamp: "00:02:15",
          content: "Hate speech indicators found",
          severity: "high",
          category: "Hate Speech",
        },
      ],
    })

    setIsProcessing(false)
  }

  const handleReset = () => {
    setSelectedFile(null)
    setResults(null)
  }

  if (results) {
    return <ResultsDisplay results={results} onReset={handleReset} />
  }

  return (
    <section id="upload" className="mb-16">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-foreground mb-3">Upload Audio/Video File</h2>
        <p className="text-muted-foreground text-lg">
          Upload a file to screen for extremist views and inappropriate content
        </p>
      </div>

      <Card className="p-8 bg-card border-border">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative border-2 border-dashed rounded-lg p-12 text-center transition-all
            ${isDragging ? "border-primary bg-primary/5" : "border-border"}
            ${selectedFile ? "bg-accent/50" : ""}
          `}
        >
          <input
            type="file"
            id="file-upload"
            className="sr-only"
            accept="audio/*,video/*"
            onChange={handleFileSelect}
          />

          {!selectedFile ? (
            <>
              <Upload className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-xl font-semibold text-foreground mb-2">Drop your file here or click to browse</h3>
              <p className="text-muted-foreground mb-6">Supports MP3, WAV, MP4, and other audio/video formats</p>
              <Button asChild>
                <label htmlFor="file-upload" className="cursor-pointer">
                  Select File
                </label>
              </Button>
            </>
          ) : (
            <>
              <FileAudio className="w-16 h-16 mx-auto mb-4 text-primary" />
              <h3 className="text-xl font-semibold text-foreground mb-2">{selectedFile.name}</h3>
              <p className="text-muted-foreground mb-6">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              <div className="flex gap-3 justify-center">
                <Button onClick={handleAnalyze} disabled={isProcessing}>
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    "Analyze Content"
                  )}
                </Button>
                <Button variant="outline" onClick={handleReset} disabled={isProcessing}>
                  Remove
                </Button>
              </div>
            </>
          )}
        </div>
      </Card>
    </section>
  )
}
