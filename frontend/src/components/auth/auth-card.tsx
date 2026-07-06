import Link from "next/link";
import { Stethoscope } from "lucide-react";

interface AuthCardProps {
  title: string;
  description: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function AuthCard({ title, description, children, footer }: AuthCardProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4 py-16">
      <Link href="/" className="flex items-center gap-2 font-heading font-semibold">
        <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Stethoscope className="size-4" />
        </span>
        Rivet
      </Link>

      <div className="mt-8 w-full max-w-sm">
        <div className="text-center">
          <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">{description}</p>
        </div>

        <div className="mt-6 rounded-xl border bg-card p-6">{children}</div>

        {footer && <div className="mt-6 text-center text-sm text-muted-foreground">{footer}</div>}
      </div>
    </div>
  );
}
