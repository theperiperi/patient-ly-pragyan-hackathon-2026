"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Check, ArrowRight, Loader2 } from "lucide-react";

interface SlideToApproveProps {
  onApprove: () => void;
  onComplete?: () => void;
  onModify?: () => void;
  onManualReview?: () => void;
  disabled?: boolean;
  className?: string;
}

type SlideState = "idle" | "sliding" | "approving" | "complete";

const executionSteps = [
  "Assigning bay...",
  "Triggering protocols...",
  "Issuing lab orders...",
  "Requesting imaging...",
  "Paging specialists...",
  "Notifying care team...",
];

export function SlideToApprove({
  onApprove,
  onComplete,
  onModify,
  onManualReview,
  disabled = false,
  className,
}: SlideToApproveProps) {
  const [slideProgress, setSlideProgress] = useState(0);
  const [state, setState] = useState<SlideState>("idle");
  const [isDragging, setIsDragging] = useState(false);
  const [executionStep, setExecutionStep] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const startXRef = useRef(0);
  const containerWidthRef = useRef(0);

  // Cycle through execution steps when approving
  useEffect(() => {
    if (state !== "approving") {
      setExecutionStep(0);
      return;
    }

    const interval = setInterval(() => {
      setExecutionStep((prev) => (prev + 1) % executionSteps.length);
    }, 350);

    return () => clearInterval(interval);
  }, [state]);

  const getSlideText = useCallback(() => {
    if (state === "complete") return "Approved";
    if (state === "approving") return executionSteps[executionStep];
    if (slideProgress < 25) return "Slide to approve";
    if (slideProgress < 50) return "Keep sliding...";
    if (slideProgress < 75) return "Almost there...";
    return "Release to confirm";
  }, [slideProgress, state, executionStep]);

  const handleStart = useCallback(
    (clientX: number) => {
      if (disabled || state !== "idle") return;
      const container = containerRef.current;
      if (!container) return;
      setIsDragging(true);
      startXRef.current = clientX;
      containerWidthRef.current = container.offsetWidth - 56;
    },
    [disabled, state]
  );

  const handleMove = useCallback(
    (clientX: number) => {
      if (!isDragging || state !== "idle") return;
      const deltaX = clientX - startXRef.current;
      const progress = Math.max(0, Math.min(100, (deltaX / containerWidthRef.current) * 100));
      setSlideProgress(progress);
    },
    [isDragging, state]
  );

  const handleEnd = useCallback(() => {
    if (!isDragging) return;
    setIsDragging(false);

    if (slideProgress >= 90) {
      setState("approving");
      setSlideProgress(100);
      onApprove();
      setTimeout(() => {
        setState("complete");
        onComplete?.();
      }, 2000);
    } else {
      setSlideProgress(0);
    }
  }, [isDragging, slideProgress, onApprove, onComplete]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    handleStart(e.clientX);
  };

  const handleMouseMove = useCallback(
    (e: MouseEvent) => handleMove(e.clientX),
    [handleMove]
  );

  const handleMouseUp = useCallback(() => handleEnd(), [handleEnd]);

  const handleTouchStart = (e: React.TouchEvent) => handleStart(e.touches[0].clientX);
  const handleTouchMove = (e: React.TouchEvent) => handleMove(e.touches[0].clientX);
  const handleTouchEnd = () => handleEnd();

  useEffect(() => {
    if (isDragging) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      return () => {
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div className={cn("w-full", className)}>
      <div
        ref={containerRef}
        className={cn(
          "relative h-14 rounded-lg overflow-hidden border transition-colors duration-200",
          state === "idle" && "bg-slate-100 border-slate-200",
          state === "approving" && "bg-emerald-100 border-emerald-300",
          state === "complete" && "bg-emerald-600 border-emerald-600",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        {/* Progress fill */}
        {state === "idle" && (
          <div
            className="absolute inset-y-0 left-0 bg-emerald-200 transition-all duration-75"
            style={{ width: `${slideProgress}%` }}
          />
        )}

        {/* Slider knob */}
        <div
          className={cn(
            "absolute top-1 bottom-1 left-1 w-12 rounded flex items-center justify-center cursor-grab active:cursor-grabbing transition-all duration-75",
            state === "idle" && "bg-emerald-600",
            state === "approving" && "bg-emerald-600",
            state === "complete" && "bg-white left-[calc(100%-3.25rem)]",
            isDragging && "scale-105"
          )}
          style={{
            transform:
              state === "idle"
                ? `translateX(${(slideProgress / 100) * (containerWidthRef.current || 0)}px)`
                : undefined,
          }}
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          {state === "complete" ? (
            <Check className="w-5 h-5 text-emerald-600" />
          ) : state === "approving" ? (
            <Loader2 className="w-5 h-5 text-white animate-spin" />
          ) : (
            <ArrowRight className="w-5 h-5 text-white" />
          )}
        </div>

        {/* Text label */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <span
            className={cn(
              "font-medium text-sm transition-colors duration-200",
              state === "complete" && "text-white",
              state === "approving" && "text-emerald-800",
              state === "idle" && slideProgress > 30 ? "text-emerald-800" : "text-slate-600"
            )}
          >
            {getSlideText()}
          </span>
        </div>
      </div>

      {/* Alternative actions - wide touch-friendly buttons */}
      {state === "idle" && (
        <div className="grid grid-cols-2 gap-2 mt-2">
          <button
            onClick={onModify}
            className="h-10 px-4 rounded border border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100 hover:border-amber-300 font-medium text-sm transition-colors active:scale-[0.98]"
          >
            Modify
          </button>
          <button
            onClick={onManualReview}
            className="h-10 px-4 rounded border border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100 hover:border-slate-300 font-medium text-sm transition-colors active:scale-[0.98]"
          >
            Manual Review
          </button>
        </div>
      )}
    </div>
  );
}
