import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 })
    }

    // Try to connect to Flask backend if FLASK_BACKEND_URL is set
    const backendUrl = process.env.FLASK_BACKEND_URL

    if (backendUrl) {
      try {
        console.log("[v0] Attempting to connect to Flask backend:", backendUrl)

        const backendFormData = new FormData()
        backendFormData.append("file", file)

        const response = await fetch(`${backendUrl}/api/audio/analyze`, {
          method: "POST",
          body: backendFormData,
        })

        if (response.ok) {
          const data = await response.json()
          console.log("[v0] Successfully received data from Flask backend")
          return NextResponse.json(data)
        } else {
          console.log("[v0] Flask backend returned error:", response.status)
        }
      } catch (error) {
        console.log("[v0] Flask backend unavailable:", error)
      }
    }

    // Fallback to demo data
    console.log("[v0] Using demo data")
    return NextResponse.json({
      status: "success",
      full_transcript:
        "This is a demo transcript. To get real analysis results, please set up the Flask backend with the provided Python scripts in the /backend folder.",
      sentences: [
        {
          text: "This is a demo sentence showing how the analysis works.",
          start: 0,
          end: 3.5,
          duration: 3.5,
          label: "NOT Hatespeech",
          explanation: "This is demo data. Connect the Flask backend for real analysis.",
          toxicity: 5.2,
        },
        {
          text: "Another example sentence with moderate toxicity.",
          start: 3.5,
          end: 7.2,
          duration: 3.7,
          label: "NOT Hatespeech",
          explanation: "Demo explanation showing the analysis format.",
          toxicity: 42.8,
        },
        {
          text: "High toxicity example for demonstration purposes.",
          start: 7.2,
          end: 10.5,
          duration: 3.3,
          label: "Hatespeech",
          explanation: "This is flagged as an example of how hate speech detection works.",
          toxicity: 78.5,
        },
      ],
      metadata: {
        filename: file.name,
        note: "Demo data - Set up Flask backend for real analysis",
      },
    })
  } catch (error) {
    console.error("[v0] Error in analyze route:", error)
    return NextResponse.json({ error: "Failed to process file" }, { status: 500 })
  }
}
