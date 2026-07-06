import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Reveal } from "@/components/reveal";

const FAQS = [
  {
    question: "Is my patient data secure?",
    answer:
      "Yes. Passwords are hashed with Argon2, sessions are protected against CSRF, and all data is stored in an isolated database. We never share patient data with third parties.",
  },
  {
    question: "Can I use Rivet on my phone or tablet?",
    answer:
      "Yes, Rivet is fully responsive and works well on phones, tablets, and desktops — so you can check patient history or review prescriptions on the go.",
  },
  {
    question: "Can I export prescriptions as a PDF?",
    answer:
      "Every prescription can be exported as a clean, print-ready A4 PDF with one click, using any of the built-in themes.",
  },
  {
    question: "Do you support multiple clinics or locations?",
    answer:
      "Pro and Premium plans support multiple doctor seats. If you need multi-location or multi-clinic support, reach out and we'll help set it up.",
  },
  {
    question: "What exactly is included in the free plan?",
    answer:
      "The Free plan includes 20 prescriptions per day, one doctor account, the standard prescription theme, and full patient management — no credit card required.",
  },
  {
    question: "Can I self-host Rivet or get a custom plan?",
    answer:
      "Yes. For larger practices, hospitals, or teams that need self-hosting or custom limits, contact us and we'll work out a plan that fits.",
  },
];

export function FaqSection() {
  return (
    <section id="faq" className="mx-auto max-w-3xl px-4 py-24 sm:px-6 lg:px-8">
      <Reveal className="text-center">
        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Frequently asked questions
        </h2>
        <p className="mt-4 text-muted-foreground">Can&apos;t find the answer you&apos;re looking for? Reach out below.</p>
      </Reveal>

      <Reveal delay={100} className="mt-12">
        <Accordion>
          {FAQS.map((faq, index) => (
            <AccordionItem key={faq.question} value={`item-${index}`}>
              <AccordionTrigger>{faq.question}</AccordionTrigger>
              <AccordionContent>{faq.answer}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </Reveal>
    </section>
  );
}
