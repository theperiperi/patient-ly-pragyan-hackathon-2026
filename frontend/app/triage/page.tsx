"use client";

import { useState, useRef, useCallback, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { mockPatients } from "@/lib/mock-data";
import { Patient, AIDecision } from "@/lib/types";
import {
  SlideToApprove,
  AIDecisionSummary,
  AIReasoning,
  VitalsGrid,
  PatientAlerts,
  SBARHandoff,
  ABDMHistory,
  PatientHeader,
  ChiefComplaint,
  ModifyModal,
  ManualReviewModal,
} from "@/components/triage";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Users, ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

// Patient card content component
function PatientCard({ patient }: { patient: Patient }) {
  return (
    <div className="space-y-4">
      {/* Patient Header + Chief Complaint */}
      <div className="space-y-1.5">
        <PatientHeader patient={patient} />
        <ChiefComplaint complaint={patient.chiefComplaint} />
      </div>

      {/* AI Decision - Actions to execute */}
      <AIDecisionSummary decision={patient.aiDecision} />

      {/* AI Reasoning - Expandable, shows first 3 */}
      <AIReasoning
        reasoning={patient.aiDecision.reasoning}
        confidence={patient.aiDecision.confidence}
      />

      {/* Vitals - Compact grid */}
      <VitalsGrid vitals={patient.vitals} />

      {/* Alerts */}
      <PatientAlerts alerts={patient.alerts} />

      {/* Collapsible sections */}
      <div className="space-y-2">
        <SBARHandoff sbar={patient.aiDecision.sbar} />
        <ABDMHistory data={patient.abdmData} />
      </div>
    </div>
  );
}

function TriageReviewContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialIndex = parseInt(searchParams.get("patient") || "0", 10);

  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [approvedPatients, setApprovedPatients] = useState<string[]>([]);
  const [modifyModalOpen, setModifyModalOpen] = useState(false);
  const [manualReviewModalOpen, setManualReviewModalOpen] = useState(false);

  // Carousel state
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isSettling, setIsSettling] = useState(false); // Disable transition during index change
  const startXRef = useRef(0);
  const startYRef = useRef(0);
  const isHorizontalRef = useRef<boolean | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(0);

  const patient: Patient = mockPatients[currentIndex];
  const prevPatient: Patient | null = currentIndex > 0 ? mockPatients[currentIndex - 1] : null;
  const nextPatient: Patient | null = currentIndex < mockPatients.length - 1 ? mockPatients[currentIndex + 1] : null;
  const pendingCount = mockPatients.length - approvedPatients.length;

  const SWIPE_THRESHOLD = 0.2; // 20% of container width

  // Get container width on mount and resize
  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth);
      }
    };
    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  const handleApprove = () => {
    console.log(`Approving patient: ${patient.name}`);
  };

  const handleComplete = () => {
    setApprovedPatients((prev) => [...prev, patient.id]);
    // Auto-advance to next patient after approval
    setTimeout(() => {
      if (currentIndex < mockPatients.length - 1) {
        animateToIndex(currentIndex + 1);
      }
    }, 800);
  };

  const handleApproveModified = (modified: AIDecision) => {
    console.log(`Approving modified plan for: ${patient.name}`, modified);
    setModifyModalOpen(false);
    setApprovedPatients((prev) => [...prev, patient.id]);
    setTimeout(() => {
      if (currentIndex < mockPatients.length - 1) {
        animateToIndex(currentIndex + 1);
      }
    }, 500);
  };

  const handleManualReview = (reason: string, priority: "urgent" | "standard") => {
    console.log(`Manual review for: ${patient.name}`, { reason, priority });
    setManualReviewModalOpen(false);
    setTimeout(() => {
      if (currentIndex < mockPatients.length - 1) {
        animateToIndex(currentIndex + 1);
      }
    }, 500);
  };

  // Animate to a specific index with slide effect
  const animateToIndex = useCallback((newIndex: number) => {
    if (newIndex === currentIndex || isAnimating) return;

    const direction = newIndex > currentIndex ? -1 : 1;
    const slideWidth = containerWidth;
    setIsAnimating(true);
    setDragOffset(direction * slideWidth);

    // After animation completes, update index and reset offset
    setTimeout(() => {
      // Disable transition before state change to prevent flicker
      setIsSettling(true);
      setCurrentIndex(newIndex);
      setDragOffset(0);

      // Re-enable transition after React has rendered
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setIsSettling(false);
          setIsAnimating(false);
        });
      });
    }, 300);
  }, [currentIndex, containerWidth, isAnimating]);

  const goToPrevious = useCallback(() => {
    if (currentIndex > 0) {
      animateToIndex(currentIndex - 1);
    }
  }, [currentIndex, animateToIndex]);

  const goToNext = useCallback(() => {
    if (currentIndex < mockPatients.length - 1) {
      animateToIndex(currentIndex + 1);
    }
  }, [currentIndex, animateToIndex]);

  // Touch handlers
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (isAnimating) return;
    startXRef.current = e.touches[0].clientX;
    startYRef.current = e.touches[0].clientY;
    isHorizontalRef.current = null;
    setIsDragging(true);
  }, [isAnimating]);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!isDragging || isAnimating) return;

    const deltaX = e.touches[0].clientX - startXRef.current;
    const deltaY = e.touches[0].clientY - startYRef.current;

    // Determine swipe direction on first significant movement
    if (isHorizontalRef.current === null) {
      if (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10) {
        isHorizontalRef.current = Math.abs(deltaX) > Math.abs(deltaY);
      }
    }

    if (isHorizontalRef.current) {
      e.preventDefault();

      // Apply resistance at edges
      const canGoLeft = currentIndex < mockPatients.length - 1;
      const canGoRight = currentIndex > 0;

      let offset = deltaX;
      if ((deltaX < 0 && !canGoLeft) || (deltaX > 0 && !canGoRight)) {
        offset = deltaX * 0.2; // Strong resistance at edges
      }

      setDragOffset(offset);
    }
  }, [isDragging, isAnimating, currentIndex]);

  const handleTouchEnd = useCallback(() => {
    if (!isDragging || isAnimating) return;
    setIsDragging(false);

    const threshold = containerWidth * SWIPE_THRESHOLD;
    const slideWidth = containerWidth; // Each slide is the full container width

    if (dragOffset < -threshold && currentIndex < mockPatients.length - 1) {
      // Swiped left - go to next
      setIsAnimating(true);
      setDragOffset(-slideWidth);
      setTimeout(() => {
        setIsSettling(true);
        setCurrentIndex(prev => prev + 1);
        setDragOffset(0);
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            setIsSettling(false);
            setIsAnimating(false);
          });
        });
      }, 300);
    } else if (dragOffset > threshold && currentIndex > 0) {
      // Swiped right - go to previous
      setIsAnimating(true);
      setDragOffset(slideWidth);
      setTimeout(() => {
        setIsSettling(true);
        setCurrentIndex(prev => prev - 1);
        setDragOffset(0);
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            setIsSettling(false);
            setIsAnimating(false);
          });
        });
      }, 300);
    } else {
      // Snap back
      setDragOffset(0);
    }

    isHorizontalRef.current = null;
  }, [isDragging, isAnimating, dragOffset, containerWidth, currentIndex]);

  // Mouse handlers for desktop testing
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (isAnimating) return;
    startXRef.current = e.clientX;
    startYRef.current = e.clientY;
    isHorizontalRef.current = null;
    setIsDragging(true);
  }, [isAnimating]);

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (isAnimating) return;

      const deltaX = e.clientX - startXRef.current;
      const deltaY = e.clientY - startYRef.current;

      if (isHorizontalRef.current === null) {
        if (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10) {
          isHorizontalRef.current = Math.abs(deltaX) > Math.abs(deltaY);
        }
      }

      if (isHorizontalRef.current) {
        const canGoLeft = currentIndex < mockPatients.length - 1;
        const canGoRight = currentIndex > 0;

        let offset = deltaX;
        if ((deltaX < 0 && !canGoLeft) || (deltaX > 0 && !canGoRight)) {
          offset = deltaX * 0.2;
        }

        setDragOffset(offset);
      }
    };

    const handleMouseUp = () => {
      if (isAnimating) return;
      setIsDragging(false);

      const threshold = containerWidth * SWIPE_THRESHOLD;
      const slideWidth = containerWidth;

      if (dragOffset < -threshold && currentIndex < mockPatients.length - 1) {
        setIsAnimating(true);
        setDragOffset(-slideWidth);
        setTimeout(() => {
          setIsSettling(true);
          setCurrentIndex(prev => prev + 1);
          setDragOffset(0);
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              setIsSettling(false);
              setIsAnimating(false);
            });
          });
        }, 300);
      } else if (dragOffset > threshold && currentIndex > 0) {
        setIsAnimating(true);
        setDragOffset(slideWidth);
        setTimeout(() => {
          setIsSettling(true);
          setCurrentIndex(prev => prev - 1);
          setDragOffset(0);
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              setIsSettling(false);
              setIsAnimating(false);
            });
          });
        }, 300);
      } else {
        setDragOffset(0);
      }

      isHorizontalRef.current = null;
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging, isAnimating, dragOffset, containerWidth, currentIndex]);

  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Compact Header */}
      <header className="sticky top-0 z-50 bg-background/95 backdrop-blur border-b">
        <div className="max-w-2xl mx-auto px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => router.push("/queue")}
              className="p-1.5 -ml-1.5 rounded hover:bg-muted"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <span className="text-sm font-semibold">Review</span>
            <Badge variant="secondary" className="h-5 text-[10px]">
              <Users className="w-3 h-3 mr-1" />
              {pendingCount} pending
            </Badge>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={goToPrevious}
              disabled={currentIndex === 0 || isAnimating}
              className="p-1.5 rounded hover:bg-muted disabled:opacity-30"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-xs text-muted-foreground w-12 text-center">
              {currentIndex + 1}/{mockPatients.length}
            </span>
            <button
              onClick={goToNext}
              disabled={currentIndex === mockPatients.length - 1 || isAnimating}
              className="p-1.5 rounded hover:bg-muted disabled:opacity-30"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Carousel Container */}
      <div
        ref={containerRef}
        className="relative w-full overflow-x-hidden"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
        style={{ cursor: isDragging ? "grabbing" : "grab" }}
      >
        {/* Carousel Track - holds all slides side by side */}
        <div
          className={cn(
            "flex",
            !isDragging && !isSettling && "transition-transform duration-300 ease-out"
          )}
          style={{
            width: containerWidth > 0 ? `${containerWidth * 3}px` : "300vw",
            transform: containerWidth > 0
              ? `translateX(${-containerWidth + dragOffset}px)`
              : `translateX(calc(-100vw + ${dragOffset}px))`,
          }}
        >
          {/* Previous Patient (left) */}
          <div
            className="flex-shrink-0 overflow-y-auto"
            style={{ width: containerWidth > 0 ? `${containerWidth}px` : "100vw" }}
          >
            {prevPatient ? (
              <div className="max-w-2xl mx-auto px-4 py-4 pb-36">
                <PatientCard patient={prevPatient} />
              </div>
            ) : (
              <div className="max-w-2xl mx-auto px-4 py-4 pb-36" />
            )}
          </div>

          {/* Current Patient (center) */}
          <div
            className="flex-shrink-0 overflow-y-auto"
            style={{ width: containerWidth > 0 ? `${containerWidth}px` : "100vw" }}
          >
            <div className="max-w-2xl mx-auto px-4 py-4 pb-36">
              <PatientCard patient={patient} />
            </div>
          </div>

          {/* Next Patient (right) */}
          <div
            className="flex-shrink-0 overflow-y-auto"
            style={{ width: containerWidth > 0 ? `${containerWidth}px` : "100vw" }}
          >
            {nextPatient ? (
              <div className="max-w-2xl mx-auto px-4 py-4 pb-36">
                <PatientCard patient={nextPatient} />
              </div>
            ) : (
              <div className="max-w-2xl mx-auto px-4 py-4 pb-36" />
            )}
          </div>
        </div>
      </div>

      {/* Sticky Footer - Slide to Approve */}
      <footer className="fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur border-t z-40">
        <div className="max-w-2xl mx-auto px-4 pt-2 pb-3">
          <SlideToApprove
            key={patient.id}
            onApprove={handleApprove}
            onComplete={handleComplete}
            onModify={() => setModifyModalOpen(true)}
            onManualReview={() => setManualReviewModalOpen(true)}
          />
        </div>
      </footer>

      {/* Modals */}
      <ModifyModal
        open={modifyModalOpen}
        onClose={() => setModifyModalOpen(false)}
        decision={patient.aiDecision}
        onApproveModified={handleApproveModified}
      />

      <ManualReviewModal
        open={manualReviewModalOpen}
        onClose={() => setManualReviewModalOpen(false)}
        patientName={patient.name}
        onConfirmReview={handleManualReview}
      />
    </div>
  );
}

export default function TriageReviewPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <TriageReviewContent />
    </Suspense>
  );
}
