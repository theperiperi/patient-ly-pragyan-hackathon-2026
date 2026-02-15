import { useState, useCallback } from "react";
import { AIDecision } from "./types";

interface TriageRequest {
  patient_id: string;
  chief_complaint: string;
  vitals?: {
    bp?: string;
    hr?: number;
    spo2?: number;
    temp?: number;
    rr?: number;
    pain?: string;
  };
}

interface UseTriageResult {
  triage: (request: TriageRequest) => Promise<AIDecision>;
  isLoading: boolean;
  error: string | null;
}

export function useTriage(): UseTriageResult {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const triage = useCallback(async (request: TriageRequest): Promise<AIDecision> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Triage failed: ${response.status}`);
      }

      const decision = await response.json();

      // Map API response to AIDecision format
      return {
        esi: decision.esi,
        acuityLabel: decision.acuityLabel,
        acuityColor: decision.acuityColor,
        confidence: decision.confidence,
        bay: decision.bay,
        queuePosition: decision.queuePosition,
        specialists: decision.specialists || [],
        protocols: decision.protocols || [],
        labs: decision.labs || [],
        imaging: decision.imaging || [],
        interventions: decision.interventions || [],
        isolation: decision.isolation,
        reasoning: decision.reasoning || [],
        sbar: decision.sbar || {
          situation: "",
          background: "",
          assessment: "",
          recommendation: ""
        }
      };
    } catch (err) {
      const message = err instanceof Error ? err.message : "Triage failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { triage, isLoading, error };
}
