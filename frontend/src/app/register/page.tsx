import Link from "next/link";
import { Stethoscope } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function RegisterPage() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4 py-24 text-center">
      <span className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
        <Stethoscope className="size-6" />
      </span>
      <h1 className="mt-6 text-2xl font-semibold tracking-tight">Sign up coming soon</h1>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        The sign-up screen is being built next. In the meantime, head back to the homepage.
      </p>
      <Button className="mt-8" render={<Link href="/" />}>
        Back to homepage
      </Button>
    </div>
  );
}
