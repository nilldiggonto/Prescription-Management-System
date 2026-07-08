import { cn } from "@/lib/utils";
import type { PrescriptionTemplate } from "@/lib/types";

export interface LetterheadInfo {
  full_name: string;
  degrees: string;
  specialization?: string | null;
  registration_number: string;
  hospital_name?: string | null;
  chamber_address?: string | null;
  phone?: string | null;
  logo_url?: string | null;
  watermark_url?: string | null;
  template: PrescriptionTemplate;
}

interface TemplateStyle {
  container: string;
  header: string;
  logo: string;
  name: string;
  details: string;
  rule: string;
  rxLabel: string;
}

const TEMPLATE_STYLES: Record<PrescriptionTemplate, TemplateStyle> = {
  classic: {
    container: "border border-neutral-300 bg-white text-neutral-900",
    header: "flex flex-col items-center text-center gap-1",
    logo: "size-14 object-contain",
    name: "text-2xl font-bold tracking-wide uppercase",
    details: "text-sm text-neutral-600",
    rule: "mt-3 border-b-4 border-double border-neutral-800",
    rxLabel: "font-serif text-2xl font-bold",
  },
  modern: {
    container: "rounded-xl border-t-4 border-primary bg-white text-neutral-900 shadow-sm",
    header: "flex items-center justify-between gap-4",
    logo: "size-14 rounded-lg object-contain",
    name: "text-xl font-semibold text-primary",
    details: "text-sm text-neutral-500",
    rule: "mt-3 border-b border-primary/30",
    rxLabel: "text-xl font-bold text-primary",
  },
  minimal: {
    container: "bg-white text-neutral-900",
    header: "flex items-center justify-between gap-4",
    logo: "size-10 object-contain",
    name: "text-base font-medium",
    details: "text-xs text-neutral-500",
    rule: "mt-2 border-b border-neutral-200",
    rxLabel: "text-lg font-semibold",
  },
};

interface PrescriptionPadFrameProps {
  doctorProfile: LetterheadInfo;
  children: React.ReactNode;
  className?: string;
}

export function PrescriptionPadFrame({ doctorProfile, children, className }: PrescriptionPadFrameProps) {
  const style = TEMPLATE_STYLES[doctorProfile.template];

  const detailLine1 = [doctorProfile.degrees, doctorProfile.specialization, `Reg. No: ${doctorProfile.registration_number}`]
    .filter(Boolean)
    .join(" | ");
  const detailLine2 = [
    doctorProfile.hospital_name,
    doctorProfile.chamber_address,
    doctorProfile.phone && `Phone: ${doctorProfile.phone}`,
  ]
    .filter(Boolean)
    .join(" | ");

  return (
    <div className={cn("relative overflow-hidden p-8 print:p-0 print:shadow-none", style.container, className)}>
      {doctorProfile.watermark_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={doctorProfile.watermark_url}
          alt=""
          aria-hidden
          className="pointer-events-none absolute inset-0 m-auto size-64 object-contain opacity-[0.06]"
        />
      )}

      <div className="relative z-10">
        <div className={style.header}>
          {doctorProfile.logo_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={doctorProfile.logo_url} alt="" className={style.logo} />
          )}
          <div className={doctorProfile.template === "classic" ? "" : "flex-1"}>
            <h1 className={style.name}>{doctorProfile.full_name}</h1>
            <p className={style.details}>{detailLine1}</p>
            {detailLine2 && <p className={style.details}>{detailLine2}</p>}
          </div>
        </div>

        <div className={style.rule} />

        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
}

export function PrescriptionRxLabel({ template }: { template: PrescriptionTemplate }) {
  return <span className={TEMPLATE_STYLES[template].rxLabel}>℞</span>;
}
