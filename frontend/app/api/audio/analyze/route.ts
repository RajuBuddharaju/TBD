import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 })
    }

    const backendUrl = process.env.FLASK_BACKEND_URL

    if (!backendUrl) {
      return NextResponse.json(
        { error: "Flask backend not configured (FLASK_BACKEND_URL missing)" },
        { status: 500 }
      )
    }

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
        console.error("[v0] Flask backend returned error:", response.status)
        return NextResponse.json(
          { error: `Flask backend returned status ${response.status}` },
          { status: response.status }
        )
      }
    } catch (error) {
      console.error("[v0] Flask backend unavailable:", error)
      return NextResponse.json(
        { error: "Failed to connect to Flask backend" },
        { status: 502 }
      )
    }
  } catch (error) {
    console.error("[v0] Error in analyze route:", error)
    return NextResponse.json({ error: "Failed to process file" }, { status: 500 })
  }
}

