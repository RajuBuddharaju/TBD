import { Scale, Eye, Shield, BookOpen } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

export function MethodologySection() {
  return (
    <section id="methodology" className="mb-16">
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Scale className="w-8 h-8 text-primary" />
          <h2 className="text-3xl font-bold text-foreground">Methodology & Ethics</h2>
        </div>
        <p className="text-muted-foreground text-lg max-w-3xl mx-auto">Our responsible approach to content screening</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 mb-8">
        <Card className="p-6 bg-card border-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-foreground">Definition of Extremist Content</h3>
          </div>
          <p className="text-muted-foreground leading-relaxed">
            We define extremist content as speech that promotes violence, hatred, or discrimination against individuals
            or groups based on protected characteristics. Our definitions are informed by legal frameworks, academic
            research, and consultation with domain experts.
          </p>
        </Card>

        <Card className="p-6 bg-card border-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
              <Eye className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-foreground">Detection Methodology</h3>
          </div>
          <p className="text-muted-foreground leading-relaxed">
            Our system uses advanced speech recognition combined with natural language processing to identify
            potentially harmful content. We employ multiple detection layers including keyword analysis, contextual
            understanding, and sentiment analysis.
          </p>
        </Card>
      </div>

      <Card className="p-6 bg-card border-border">
        <div className="flex items-center gap-3 mb-6">
          <BookOpen className="w-6 h-6 text-primary" />
          <h3 className="text-xl font-semibold text-foreground">Ethical Considerations</h3>
        </div>

        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="item-1">
            <AccordionTrigger className="text-foreground hover:text-primary">
              Privacy & Data Protection
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              All uploaded files are processed locally and are not stored on our servers. We do not collect or retain
              any personal information from the audio content. Our system is designed with privacy-by-default
              principles.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-2">
            <AccordionTrigger className="text-foreground hover:text-primary">Bias Mitigation</AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              We actively work to reduce bias in our detection algorithms through diverse training data, regular audits,
              and continuous refinement. Our system is tested across multiple languages, dialects, and cultural contexts
              to ensure fair and accurate detection.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-3">
            <AccordionTrigger className="text-foreground hover:text-primary">
              Transparency & Accountability
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              We maintain transparency about our detection criteria and methodology. All detections include timestamps
              and explanations, allowing for human review and verification. We welcome feedback and continuously improve
              our system based on user input.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-4">
            <AccordionTrigger className="text-foreground hover:text-primary">
              Limitations & Human Oversight
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground">
              Automated systems have limitations and should not be the sole arbiter of content decisions. We recommend
              human review of all flagged content, especially in high-stakes contexts. Context, intent, and nuance are
              critical factors that require human judgment.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>
    </section>
  )
}
