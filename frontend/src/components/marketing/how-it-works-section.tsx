import { Reveal } from "@/components/reveal";

const STEPS = [
  {
    step: "01",
    title: "Sign up & verify your email",
    description: "Create your account in under a minute and confirm your email with a quick code.",
  },
  {
    step: "02",
    title: "Set up your doctor profile",
    description: "Add your clinic, degree, registration number, signature, and logo — once.",
  },
  {
    step: "03",
    title: "Add your patients",
    description: "Build patient profiles with history, allergies, and current medications.",
  },
  {
    step: "04",
    title: "Create & print in seconds",
    description: "Pick a theme, fill in the clinical details, and export a print-ready PDF instantly.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="border-y bg-muted/30">
      <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6 lg:px-8">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">How it works</h2>
          <p className="mt-4 text-muted-foreground">
            From sign-up to your first prescription in four simple steps.
          </p>
        </Reveal>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((item, index) => (
            <Reveal key={item.step} delay={index * 100} className="relative">
              <span className="font-heading text-4xl font-semibold text-primary/25">
                {item.step}
              </span>
              <h3 className="mt-3 font-heading text-base font-semibold">{item.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{item.description}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
