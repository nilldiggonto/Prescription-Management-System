import { Reveal } from "@/components/reveal";

// Illustrative placeholder quotes — swap for real testimonials before public launch.
const TESTIMONIALS = [
  {
    quote:
      "What used to take me ten minutes per patient now takes under a minute. My handwriting was never the problem — the paperwork was.",
    name: "Dr. A. Sharma",
    role: "Family Medicine",
  },
  {
    quote:
      "Having every patient's history and past prescriptions in one place changed how I run follow-up visits entirely.",
    name: "Dr. R. Chowdhury",
    role: "Internal Medicine",
  },
  {
    quote:
      "The printed prescriptions look genuinely professional. Patients notice, and pharmacists have fewer questions.",
    name: "Dr. M. Islam",
    role: "General Practitioner",
  },
];

export function TestimonialsSection() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-24 sm:px-6 lg:px-8">
      <Reveal className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">Loved by doctors</h2>
        <p className="mt-4 text-muted-foreground">
          Early feedback from doctors piloting Rivet in their practice.
        </p>
      </Reveal>

      <div className="mt-16 grid gap-6 md:grid-cols-3">
        {TESTIMONIALS.map((testimonial, index) => (
          <Reveal key={testimonial.name} delay={index * 100} className="h-full">
            <figure className="flex h-full flex-col justify-between rounded-xl border bg-card p-6">
              <blockquote className="text-sm leading-relaxed text-foreground">
                &ldquo;{testimonial.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-6 flex items-center gap-3">
                <span className="flex size-9 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                  {testimonial.name
                    .split(" ")
                    .map((part) => part[0])
                    .join("")}
                </span>
                <div>
                  <p className="text-sm font-medium">{testimonial.name}</p>
                  <p className="text-xs text-muted-foreground">{testimonial.role}</p>
                </div>
              </figcaption>
            </figure>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
