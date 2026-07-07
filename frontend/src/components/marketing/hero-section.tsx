import { ArrowRightIcon, CheckIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/reveal";
import { AuthCtaButton } from "@/components/marketing/auth-cta-button";

const TRUST_POINTS = ["No credit card required", "Free forever plan", "Cancel anytime"];

export function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 -top-40 -z-10 flex justify-center"
      >
        <div className="h-96 w-[36rem] rounded-full bg-primary/20 blur-3xl dark:bg-primary/10" />
      </div>

      <div className="mx-auto max-w-4xl px-4 pt-20 pb-16 text-center sm:px-6 sm:pt-28 sm:pb-24 lg:px-8">
        <Reveal>
          <span className="inline-flex items-center rounded-full border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground">
            Built for modern medical practices
          </span>
        </Reveal>

        <Reveal delay={75}>
          <h1 className="mt-6 text-4xl font-semibold tracking-tight text-balance sm:text-5xl lg:text-6xl">
            Create beautiful, professional prescriptions in seconds
          </h1>
        </Reveal>

        <Reveal delay={150}>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground text-balance">
            Rivet helps doctors write, print, and share polished prescriptions — and
            communicate with patients efficiently — without the paperwork headache.
          </p>
        </Reveal>

        <Reveal delay={225}>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <AuthCtaButton size="lg" className="h-11 px-6 text-base">
              Get Started Free
              <ArrowRightIcon />
            </AuthCtaButton>
            <Button
              size="lg"
              variant="outline"
              className="h-11 px-6 text-base"
              render={<a href="#pricing" />}
            >
              See Pricing
            </Button>
          </div>
        </Reveal>

        <Reveal delay={300}>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
            {TRUST_POINTS.map((point) => (
              <span key={point} className="inline-flex items-center gap-1.5">
                <CheckIcon className="size-4 text-primary" />
                {point}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
