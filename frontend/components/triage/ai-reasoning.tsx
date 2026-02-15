"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Lightbulb, ChevronDown, ChevronUp } from "lucide-react";

interface AIReasoningProps {
  reasoning: string[];
  confidence: number;
  className?: string;
}

export function AIReasoning({ reasoning, confidence, className }: AIReasoningProps) {
  const [expanded, setExpanded] = useState(false);
  const visibleCount = 3;
  const hasMore = reasoning.length > visibleCount;
  const visibleReasons = expanded ? reasoning : reasoning.slice(0, visibleCount);

  // Highlight important keywords
  const highlightText = (text: string) => {
    const keywords = [
      "STEMI", "ST elevation", "critical", "high risk", "time-critical",
      "emergency", "immediate", "STAT", "urgent", "shock", "unstable",
      "hypotension", "tachycardia", "hypoxemia", "previous MI", "stroke",
      "hemorrhage", "abruption", "Door-to-balloon",
    ];

    let result = text;
    keywords.forEach((keyword) => {
      const regex = new RegExp(`(${keyword})`, "gi");
      result = result.replace(
        regex,
        '<mark class="bg-amber-100 text-amber-900 px-0.5 rounded font-medium">$1</mark>'
      );
    });
    return result;
  };

  return (
    <div className={cn("border border-slate-200 rounded overflow-hidden", className)}>
      {/* Header */}
      <div className="px-2.5 py-1 bg-sky-50 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Lightbulb className="w-3.5 h-3.5 text-sky-600" />
          <span className="text-[10px] font-medium text-sky-700 uppercase tracking-wider">
            AI Reasoning
          </span>
        </div>
        <span className="text-[10px] text-sky-600 font-medium">
          {confidence}% confidence
        </span>
      </div>
      {/* Content */}
      <div className="px-2.5 py-2">
        <ul className="space-y-1.5">
          {visibleReasons.map((reason, index) => (
            <li key={index} className="flex items-start gap-2 text-xs">
              <span className="text-sky-500 font-semibold mt-0.5">{index + 1}.</span>
              <p
                className="leading-snug text-slate-700"
                dangerouslySetInnerHTML={{ __html: highlightText(reason) }}
              />
            </li>
          ))}
        </ul>
        {hasMore && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-sky-600 hover:text-sky-800 mt-2 font-medium"
          >
            {expanded ? (
              <>
                <ChevronUp className="w-3 h-3" />
                Show less
              </>
            ) : (
              <>
                <ChevronDown className="w-3 h-3" />
                +{reasoning.length - visibleCount} more
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
