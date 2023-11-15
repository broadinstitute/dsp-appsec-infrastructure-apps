export interface CISfindings {
    benchmark: string;
    id: string;
    level: number;
    cvss: number;
    title: string;
    failures: string[];
    description: string;
    rationale: string;
    refs: string[];
  }