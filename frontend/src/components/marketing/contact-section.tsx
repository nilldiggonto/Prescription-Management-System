import { MailIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/reveal";

export function ContactSection() {
  return (
    <section id="contact" className="mx-auto max-w-3xl px-4 py-24 text-center sm:px-6 lg:px-8">
      <Reveal>
        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Still have questions?
        </h2>
        <p className="mt-4 text-muted-foreground">
          Whether it&apos;s a custom plan, self-hosting, or anything else — we&apos;re happy to talk.
        </p>
        <Button
          size="lg"
          className="mt-8 h-11 px-6 text-base"
          render={<a href="mailto:hello@rivet.health" />}
        >
          <MailIcon />
          hello@rivet.health
        </Button>
      </Reveal>
    </section>
  );
}
