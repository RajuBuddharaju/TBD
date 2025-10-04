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
    } else {
      console.log("Cannot connect to Flask backend with url:", backendUrl)
      throw new error("Cannot connect to backend.")
    }

    } catch (error) {
    console.error("[v0] Error in analyze route:", error)
    return NextResponse.json({ error: "Failed to process file" }, { status: 500 })
  }
}
