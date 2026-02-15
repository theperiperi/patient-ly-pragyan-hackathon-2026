"use client";

import { cn } from "@/lib/utils";

interface ChiefComplaintProps {
  complaint: string;
  className?: string;
}

export function ChiefComplaint({ complaint, className }: ChiefComplaintProps) {
  return (
    <div className={cn("text-sm", className)}>
      <span className="text-muted-foreground">CC: </span>
      <span className="font-medium">{complaint}</span>
    </div>
  );
}
