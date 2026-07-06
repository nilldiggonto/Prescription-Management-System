import {
  FileTextIcon,
  UsersIcon,
  PenToolIcon,
  ShieldCheckIcon,
  PrinterIcon,
  LayoutDashboardIcon,
  type LucideIcon,
} from "lucide-react";

import { Reveal } from "@/components/reveal";

interface Feature {
  icon: LucideIcon;
  title: string;
  description: string;
}

const FEATURES: Feature[] = [
  {
    icon: FileTextIcon,
    title: "Professional Prescription Templates",
    description:
      "Choose from 3-5 built-in themes — Minimal, Modern, Blue Medical, Elegant, and Classic Hospital — every one print-ready for clean A4 output.",
  },
  {
    icon: UsersIcon,
    title: "Patient Management & History",
    description:
      "Keep full patient profiles with medical history, allergies, and chronic conditions, plus every past prescription in one searchable place.",
  },
  {
    icon: PenToolIcon,
    title: "Digital Signature & Clinic Branding",
    description:
      "Upload your signature and clinic logo once — they show up automatically on every prescription you create from then on.",
  },
  {
    icon: ShieldCheckIcon,
    title: "Secure Authentication",
    description:
      "Email verification, encrypted sessions, and account protections keep your practice and patient data safe by default.",
  },
  {
    icon: PrinterIcon,
    title: "Instant PDF Export & Print",
    description:
      "Generate a clean, professional PDF with one click — ready to print or send directly to your patient.",
  },
  {
    icon: LayoutDashboardIcon,
    title: "Dashboard & Activity Tracking",
    description:
      "See total patients, recent prescriptions, and practice activity at a glance from a single, focused dashboard.",
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-4 py-24 sm:px-6 lg:px-8">
      <Reveal className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Everything you need to run your practice
        </h2>
        <p className="mt-4 text-muted-foreground">
          Built specifically for how doctors actually write and share prescriptions.
        </p>
      </Reveal>

      <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((feature, index) => (
          <Reveal key={feature.title} delay={index * 75}>
            <div className="h-full rounded-xl border bg-card p-6 transition-shadow hover:shadow-md">
              <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <feature.icon className="size-5" />
              </div>
              <h3 className="mt-4 font-heading text-base font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{feature.description}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
