import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { UploadSection } from "@/components/upload-section"
import { MethodologySection } from "@/components/methodology-section"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <UploadSection />
        <MethodologySection />
      </main>
      <Footer />
    </div>
  )
}
