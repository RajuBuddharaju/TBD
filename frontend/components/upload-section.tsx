"use client"

import type React from "react"

import { useState, useCallback, useRef } from "react"
import { Upload, FileAudio, Loader2, Mic, Square } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ResultsDisplay } from "@/components/results-display"

interface AnalysisResult {
  fileName: string
  fullTranscript: string
  sentences: Array<{
    text: string
    start: number
    end: number
    duration: number
    label?: string
    explanation?: string
    toxicity?: number
  }>
}

const ALLOWED_TYPES = ["audio/mpeg", "audio/wav", "audio/mp3", "video/mp4", "audio/webm"]
const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB

export function UploadSection() {
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [results, setResults] = useState<AnalysisResult | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return "Invalid file type. Please upload MP3, WAV, MP4, or MOV files."
    }
    if (file.size > MAX_FILE_SIZE) {
      return "File too large. Maximum size is 100MB."
    }
    return null
  }

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
    setError(null)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const validationError = validateFile(files[0])
      if (validationError) {
        setError(validationError)
        return
      }
      setSelectedFile(files[0])
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null)
    const files = e.target.files
    if (files && files.length > 0) {
      const validationError = validateFile(files[0])
      if (validationError) {
        setError(validationError)
        return
      }
      setSelectedFile(files[0])
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" })
        const file = new File([blob], `recording-${Date.now()}.webm`, { type: "audio/webm" })
        setSelectedFile(file)
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)

      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1)
      }, 1000)
    } catch (err) {
      setError("Failed to access microphone. Please check permissions.")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append("file", selectedFile)

      const response = await fetch("/api/audio/analyze", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Analysis failed")
      }

      const data = await response.json()

      setResults({
        fileName: selectedFile.name,
        fullTranscript: data.full_transcript || data.fullTranscript,
        sentences: data.sentences || [],
      })
    } catch (err) {
      setError("Analysis failed. Please try again.")
      console.error(err)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setResults(null)
    setError(null)
    setRecordingTime(0)
  }

  if (results) {
    return <ResultsDisplay results={results} onReset={handleReset} />
  }

  return (
    <section id="upload" className="mb-16">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-foreground mb-3">Upload or Record Audio</h2>
        <p className="text-muted-foreground text-lg">
          Upload a file or record audio to screen for extremist views and inappropriate content
        </p>
      </div>

      <Card className="p-8 bg-card border-border">
        {error && (
          <div className="mb-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
            {error}
          </div>
        )}

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative border-2 border-dashed rounded-lg p-12 text-center transition-all duration-200
            ${isDragging ? "border-primary bg-primary/5 scale-[1.02]" : "border-border"}
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
              <Upload className="w-16 h-16 mx-auto mb-4 text-muted-foreground transition-transform duration-200 hover:scale-110" />
              <h3 className="text-xl font-semibold text-foreground mb-2">Drop your file here or click to browse</h3>
              <p className="text-muted-foreground mb-6">Supports MP3, WAV, MP4, and MOV formats (max 100MB)</p>
              <div className="flex gap-3 justify-center">
                <Button asChild>
                  <label htmlFor="file-upload" className="cursor-pointer">
                    Select File
                  </label>
                </Button>
                {!isRecording ? (
                  <Button variant="outline" onClick={startRecording}>
                    <Mic className="w-4 h-4 mr-2" />
                    Record Audio
                  </Button>
                ) : (
                  <Button variant="destructive" onClick={stopRecording}>
                    <Square className="w-4 h-4 mr-2" />
                    Stop Recording ({recordingTime}s)
                  </Button>
                )}
              </div>
            </>
          ) : (
            <>
              <FileAudio className="w-16 h-16 mx-auto mb-4 text-primary animate-pulse" />
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
