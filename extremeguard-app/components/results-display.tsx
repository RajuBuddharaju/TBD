"use client"

import { AlertTriangle, Clock, FileText, RotateCcw } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface Detection {
  timestamp: string
  content: string
  severity: "high" | "medium" | "low"
  category: string
}

interface ResultsDisplayProps {
  results: {
    fileName: string
    duration: number
    detections: Detection[]
  }
  onReset: () => void
}

export function ResultsDisplay({ results, onReset }: ResultsDisplayProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-destructive/10 text-destructive border-destructive/20"
      case "medium":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
      case "low":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  return (
    <section className="mb-16">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Analysis Results</h2>
          <p className="text-muted-foreground">Screening complete for {results.fileName}</p>
        </div>
        <Button onClick={onReset} variant="outline">
          <RotateCcw className="w-4 h-4 mr-2" />
          Analyze Another File
        </Button>
      </div>

      <div className="grid gap-6 mb-8 md:grid-cols-3">
        <Card className="p-6 bg-card border-border">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-foreground">File Name</h3>
          </div>
          <p className="text-sm text-muted-foreground truncate">{results.fileName}</p>
        </Card>

        <Card className="p-6 bg-card border-border">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-foreground">Duration</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            {Math.floor(results.duration / 60)}:{(results.duration % 60).toString().padStart(2, "0")}
          </p>
        </Card>

        <Card className="p-6 bg-card border-border">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-foreground">Detections</h3>
          </div>
          <p className="text-sm text-muted-foreground">{results.detections.length} issues found</p>
        </Card>
      </div>

      <Card className="p-6 bg-card border-border">
        <h3 className="text-xl font-semibold text-foreground mb-4">Detected Content</h3>
        <div className="space-y-4">
          {results.detections.map((detection, index) => (
            <div key={index} className="flex items-start gap-4 p-4 rounded-lg bg-accent/50 border border-border">
              <div className="flex-shrink-0 w-20 text-center">
                <Badge variant="outline" className="font-mono">
                  {detection.timestamp}
                </Badge>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className={getSeverityColor(detection.severity)}>{detection.severity.toUpperCase()}</Badge>
                  <span className="text-sm font-medium text-foreground">{detection.category}</span>
                </div>
                <p className="text-sm text-muted-foreground">{detection.content}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </section>
  )
}
