"use client"

import { AlertTriangle, Clock, FileText, RotateCcw } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface Sentence {
  text: string
  start: number
  end: number
  duration: number
  label?: string
  explanation?: string
}

interface ResultsDisplayProps {
  results: {
    fileName: string
    fullTranscript: string
    sentences: Sentence[]
  }
  onReset: () => void
}

export function ResultsDisplay({ results, onReset }: ResultsDisplayProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "hatespeech":
        return "bg-destructive/10 text-destructive border-destructive/20"
      case "potential hatespeech":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
      case "not hatespeech":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const formatTimestamp = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const totalDuration = results.sentences.length > 0 ? results.sentences[results.sentences.length - 1].end : 0

  const highSeverityCount = results.sentences.filter((s) => s.label === "hatespeech").length

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
          <p className="text-sm text-muted-foreground">{formatTimestamp(totalDuration)}</p>
        </Card>

        <Card className="p-6 bg-card border-border">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-foreground">High Severity</h3>
          </div>
          <p className="text-sm text-muted-foreground">{highSeverityCount} detected</p>
        </Card>
      </div>

      <Card className="p-6 bg-card border-border mb-6">
        <h3 className="text-xl font-semibold text-foreground mb-4">Full Transcript</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{results.fullTranscript}</p>
      </Card>

      <Card className="p-6 bg-card border-border">
        <h3 className="text-xl font-semibold text-foreground mb-4">Sentence Analysis</h3>
        <div className="space-y-4">
          {results.sentences.map((sentence, index) => {
            return (
              <div
                key={index}
                className="flex items-start gap-4 p-4 rounded-lg bg-accent/50 border border-border transition-all hover:bg-accent/70"
              >
                <div className="flex-shrink-0 w-20 text-center">
                  <Badge variant="outline" className="font-mono">
                    {formatTimestamp(sentence.start)}
                  </Badge>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {sentence.label && <Badge className={getSeverityColor(sentence.label)} variant="outline">{sentence.label}</Badge>}
                  </div>
                  <p className="text-sm text-foreground mb-2 font-medium">{sentence.text}</p>
                  {sentence.explanation && (
                    <p className="text-xs text-muted-foreground italic">{sentence.explanation}</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>
    </section>
  )
}
