import { Shield } from "lucide-react"

export function Header() {
  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 py-4 max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">AIMI</h1>
              <p className="text-sm text-muted-foreground">
                Automated Identification of Malicious Intent
              </p>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <a href="#upload" className="text-sm text-foreground hover:text-primary transition-colors">
              Upload
            </a>
            <a href="#methodology" className="text-sm text-foreground hover:text-primary transition-colors">
              Methodology
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}
