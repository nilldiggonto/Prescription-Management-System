import Link from "next/link";
import { CheckIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Reveal } from "@/components/reveal";
import { cn } from "@/lib/utils";

interface Tier {
  name: string;
  price: string;
  cadence: string;
  description: string;
  limit: string;
  features: string[];
  cta: string;
  href: string;
  highlighted?: boolean;
}

// Placeholder prices — swap these for real figures whenever pricing is finalized.
const TIERS: Tier[] = [
  {
    name: "Free",
    price: "$0",
    cadence: "/month",
    description: "Try Rivet with everything you need to get started.",
    limit: "20 prescriptions / day",
    features: [
      "1 doctor account",
      "Standard prescription theme",
      "Patient management",
      "Community support",
    ],
    cta: "Start Free",
    href: "/register",
  },
  {
    name: "Pro",
    price: "$29",
    cadence: "/month",
    description: "For busy practices that need more room to grow.",
    limit: "100 prescriptions / day",
    features: [
      "Everything in Free",
      "All prescription themes",
      "Patient history export",
      "Priority email support",
    ],
    cta: "Start Pro",
    href: "/register?plan=pro",
    highlighted: true,
  },
  {
    name: "Premium",
    price: "$79",
    cadence: "/month",
    description: "For high-volume clinics that never want to think about limits.",
    limit: "Unlimited prescriptions",
    features: [
      "Everything in Pro",
      "Custom clinic branding",
      "Multiple doctor seats",
      "Dedicated support",
    ],
    cta: "Get Premium",
    href: "/register?plan=premium",
  },
];

export function PricingSection() {
  return (
    <section id="pricing" className="border-y bg-muted/30">
      <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6 lg:px-8">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-muted-foreground">
            Start free, upgrade as your practice grows. No hidden fees.
          </p>
        </Reveal>

        <div className="mx-auto mt-16 grid max-w-5xl gap-6 lg:grid-cols-3">
          {TIERS.map((tier, index) => (
            <Reveal key={tier.name} delay={index * 100} className="h-full">
              <div
                className={cn(
                  "flex h-full flex-col rounded-xl border bg-card p-6",
                  tier.highlighted && "border-primary shadow-lg ring-1 ring-primary/20"
                )}
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-heading text-lg font-semibold">{tier.name}</h3>
                  {tier.highlighted && <Badge>Most Popular</Badge>}
                </div>

                <p className="mt-2 text-sm text-muted-foreground">{tier.description}</p>

                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-4xl font-semibold tracking-tight">{tier.price}</span>
                  <span className="text-sm text-muted-foreground">{tier.cadence}</span>
                </div>

                <p className="mt-1 text-sm font-medium text-primary">{tier.limit}</p>

                <ul className="mt-6 flex flex-1 flex-col gap-2.5">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm">
                      <CheckIcon className="mt-0.5 size-4 shrink-0 text-primary" />
                      <span className="text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  className="mt-8"
                  variant={tier.highlighted ? "default" : "outline"}
                  render={<Link href={tier.href} />}
                >
                  {tier.cta}
                </Button>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={300} className="mx-auto mt-10 max-w-5xl">
          <div className="flex flex-col items-center justify-between gap-4 rounded-xl border bg-card p-6 sm:flex-row">
            <div>
              <h3 className="font-heading text-base font-semibold">
                Need higher limits, a custom plan, or self-hosting?
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                We work with larger practices and hospitals on custom deployments.
              </p>
            </div>
            <Button variant="outline" className="shrink-0" render={<a href="#contact" />}>
              Contact us
            </Button>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
