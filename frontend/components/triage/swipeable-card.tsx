"use client";

import { useState, useRef, useCallback, useEffect, ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Check, ClipboardList } from "lucide-react";

interface SwipeableCardProps {
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onTap?: () => void;
  disabled?: boolean;
  className?: string;
}

const SWIPE_THRESHOLD = 80;

export function SwipeableCard({
  children,
  onSwipeLeft,
  onSwipeRight,
  onTap,
  disabled = false,
  className,
}: SwipeableCardProps) {
  const [offsetX, setOffsetX] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isComplete, setIsComplete] = useState<"left" | "right" | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const startXRef = useRef(0);
  const startYRef = useRef(0);
  const isHorizontalSwipeRef = useRef<boolean | null>(null);

  const handleStart = useCallback(
    (clientX: number, clientY: number) => {
      if (disabled || isComplete) return;
      setIsDragging(true);
      startXRef.current = clientX;
      startYRef.current = clientY;
      isHorizontalSwipeRef.current = null;
    },
    [disabled, isComplete]
  );

  const handleMove = useCallback(
    (clientX: number, clientY: number) => {
      if (!isDragging || disabled || isComplete) return;

      const deltaX = clientX - startXRef.current;
      const deltaY = clientY - startYRef.current;

      // Determine swipe direction on first significant movement
      if (isHorizontalSwipeRef.current === null) {
        if (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10) {
          isHorizontalSwipeRef.current = Math.abs(deltaX) > Math.abs(deltaY);
        }
      }

      // Only allow horizontal swipe
      if (isHorizontalSwipeRef.current) {
        setOffsetX(deltaX * 0.8); // Add some resistance
      }
    },
    [isDragging, disabled, isComplete]
  );

  const handleEnd = useCallback(() => {
    if (!isDragging) return;
    setIsDragging(false);

    if (offsetX > SWIPE_THRESHOLD && onSwipeRight) {
      setIsComplete("right");
      setOffsetX(300);
      setTimeout(() => {
        onSwipeRight();
        setIsComplete(null);
        setOffsetX(0);
      }, 300);
    } else if (offsetX < -SWIPE_THRESHOLD && onSwipeLeft) {
      setIsComplete("left");
      setOffsetX(-300);
      setTimeout(() => {
        onSwipeLeft();
        setIsComplete(null);
        setOffsetX(0);
      }, 300);
    } else if (Math.abs(offsetX) < 10 && isHorizontalSwipeRef.current !== true) {
      // It was a tap
      onTap?.();
      setOffsetX(0);
    } else {
      setOffsetX(0);
    }

    isHorizontalSwipeRef.current = null;
  }, [isDragging, offsetX, onSwipeLeft, onSwipeRight, onTap]);

  const handleTouchStart = (e: React.TouchEvent) => {
    handleStart(e.touches[0].clientX, e.touches[0].clientY);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    handleMove(e.touches[0].clientX, e.touches[0].clientY);
  };

  const handleTouchEnd = () => handleEnd();

  const handleMouseDown = (e: React.MouseEvent) => {
    handleStart(e.clientX, e.clientY);
  };

  const handleMouseMove = useCallback(
    (e: MouseEvent) => handleMove(e.clientX, e.clientY),
    [handleMove]
  );

  const handleMouseUp = useCallback(() => handleEnd(), [handleEnd]);

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

  const swipeProgress = Math.min(Math.abs(offsetX) / SWIPE_THRESHOLD, 1);
  const isSwipingRight = offsetX > 0;
  const isSwipingLeft = offsetX < 0;

  return (
    <div
      ref={containerRef}
      className={cn("relative overflow-hidden rounded-lg", className)}
    >
      {/* Background indicators */}
      <div className="absolute inset-0 flex">
        {/* Left side - Manual Review (shown when swiping left) */}
        <div
          className={cn(
            "absolute inset-y-0 right-0 w-24 flex items-center justify-center transition-opacity",
            isSwipingLeft ? "opacity-100" : "opacity-0"
          )}
          style={{
            background: `rgba(71, 85, 105, ${swipeProgress * 0.9})`,
          }}
        >
          <div className="text-white text-center">
            <ClipboardList className="w-5 h-5 mx-auto mb-0.5" />
            <span className="text-[10px] font-medium">Review</span>
          </div>
        </div>

        {/* Right side - Approve (shown when swiping right) */}
        <div
          className={cn(
            "absolute inset-y-0 left-0 w-24 flex items-center justify-center transition-opacity",
            isSwipingRight ? "opacity-100" : "opacity-0"
          )}
          style={{
            background: `rgba(22, 163, 74, ${swipeProgress * 0.9})`,
          }}
        >
          <div className="text-white text-center">
            <Check className="w-5 h-5 mx-auto mb-0.5" />
            <span className="text-[10px] font-medium">Approve</span>
          </div>
        </div>
      </div>

      {/* Card content */}
      <div
        className={cn(
          "relative bg-background transition-transform",
          isDragging ? "transition-none" : "duration-200"
        )}
        style={{
          transform: `translateX(${offsetX}px)`,
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
      >
        {children}
      </div>
    </div>
  );
}
