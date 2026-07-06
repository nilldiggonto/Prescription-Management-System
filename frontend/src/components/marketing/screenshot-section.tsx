import { Reveal } from "@/components/reveal";

function Skeleton({ className }: { className?: string }) {
  return <div className={`rounded-md bg-muted-foreground/15 ${className ?? ""}`} />;
}

function DashboardMockup() {
  return (
    <div className="overflow-hidden rounded-xl border bg-card shadow-2xl">
      <div className="flex items-center gap-1.5 border-b bg-muted/40 px-4 py-3">
        <span className="size-2.5 rounded-full bg-red-400/70" />
        <span className="size-2.5 rounded-full bg-yellow-400/70" />
        <span className="size-2.5 rounded-full bg-green-400/70" />
        <div className="mx-auto flex w-64 items-center justify-center rounded-md bg-background/80 px-3 py-1 text-xs text-muted-foreground">
          app.rivet.health/dashboard
        </div>
      </div>

      <div className="flex">
        <div className="hidden w-48 shrink-0 flex-col gap-3 border-r bg-muted/20 p-4 sm:flex">
          <Skeleton className="h-6 w-24" />
          <div className="mt-4 flex flex-col gap-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className={`h-3 ${i === 0 ? "w-full bg-primary/30" : "w-5/6"}`} />
            ))}
          </div>
        </div>

        <div className="flex-1 p-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-8 w-28 bg-primary/30" />
          </div>

          <div className="mt-6 grid grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-lg border p-4">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="mt-3 h-6 w-12" />
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-lg border p-4">
            <Skeleton className="h-4 w-32" />
            <div className="mt-4 flex flex-col gap-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3">
                  <Skeleton className="size-8 shrink-0 rounded-full" />
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-16 shrink-0" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ScreenshotSection() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-24 sm:px-6 lg:px-8">
      <Reveal className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          A dashboard built for focus
        </h2>
        <p className="mt-4 text-muted-foreground">
          Everything about your practice, at a glance — patients, prescriptions, and activity.
        </p>
      </Reveal>

      <Reveal delay={100} className="mt-14">
        <DashboardMockup />
      </Reveal>
    </section>
  );
}
