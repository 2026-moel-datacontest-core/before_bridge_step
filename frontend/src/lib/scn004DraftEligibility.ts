import type { AnswerResponse, DocumentType, GroundedChunkResult } from '@/types/api';

type DraftDocumentEligibility = Record<DocumentType, boolean>;

export interface Scn004DraftEligibility {
  isEligible: boolean;
  documentTypes: DraftDocumentEligibility;
}

const wageCitationPatterns = [
  /근로기준법\s*제\s*36\s*조/,
  /근로기준법\s*제\s*37\s*조/,
  /근로자\s*퇴직\s*급여\s*보장법\s*제\s*9\s*조/,
];

const dismissalCitationPatterns = [
  /근로기준법\s*제\s*23\s*조/,
  /근로기준법\s*제\s*26\s*조/,
  /근로기준법\s*제\s*27\s*조/,
  /근로기준법\s*제\s*28\s*조/,
  /근로기준법\s*시행규칙\s*제\s*5\s*조/,
];

const wageKeywordPatterns = [
  /임금\s*체불/,
  /체불\s*임금/,
  /미지급\s*임금/,
  /임금\s*미지급/,
  /월급.{0,16}(못\s*받|받지\s*못|안\s*받|받지\s*않|미지급|체불)/,
  /(못\s*받|받지\s*못|안\s*받|받지\s*않|미지급|체불).{0,16}월급/,
  /퇴직금/,
  /금품\s*청산/,
];

const wageQueryOnlyKeywordPatterns = [
  /(퇴사|퇴직|해고|마지막\s*근무|금품|임금|월급|퇴직금).{0,24}(14\s*일|십사\s*일)/,
  /(14\s*일|십사\s*일).{0,24}(퇴사|퇴직|해고|마지막\s*근무|금품|임금|월급|퇴직금)/,
];

const dismissalKeywordPatterns = [
  /부당\s*해고/,
  /해고/,
  /서면\s*통지/,
  /해고\s*예고/,
  /노동\s*위원회/,
];

const dismissalChunkKeywordPatterns = [
  /부당\s*해고/,
  /해고\s*사유/,
  /서면\s*통지/,
  /해고\s*예고/,
  /노동\s*위원회/,
];

export function getScn004DraftEligibility(
  response: AnswerResponse,
): Scn004DraftEligibility {
  const citedArticleText = response.cited_articles.join('\n');
  const chunkText = getRelevantChunks(response).map(buildChunkRuleText).join('\n');
  const queryText = response.query;

  const hasWageMatch =
    matchesAny(queryText, [...wageKeywordPatterns, ...wageQueryOnlyKeywordPatterns]) ||
    matchesAny(citedArticleText, wageCitationPatterns) ||
    matchesAny(chunkText, [...wageCitationPatterns, ...wageKeywordPatterns]);

  const hasDismissalMatch =
    matchesAny(queryText, dismissalKeywordPatterns) ||
    matchesAny(citedArticleText, dismissalCitationPatterns) ||
    matchesAny(chunkText, [...dismissalCitationPatterns, ...dismissalChunkKeywordPatterns]);

  return {
    isEligible: hasWageMatch || hasDismissalMatch,
    documentTypes: {
      labor_office_wage_complaint: hasWageMatch,
      labor_commission_unfair_dismissal_brief: hasDismissalMatch,
    },
  };
}

function getRelevantChunks(response: AnswerResponse): GroundedChunkResult[] {
  if (response.grounded_context_ids.length === 0) {
    return response.retrieved_chunks;
  }

  const groundedIds = new Set(response.grounded_context_ids);
  const groundedChunks = response.retrieved_chunks.filter((chunk) =>
    groundedIds.has(chunk.context_id),
  );

  return groundedChunks.length > 0 ? groundedChunks : response.retrieved_chunks;
}

function buildChunkRuleText(chunk: GroundedChunkResult): string {
  return [
    chunk.citation_label,
    chunk.law_name,
    chunk.article_no,
    chunk.article_title,
    chunk.structure_path ?? '',
    chunk.content,
  ].join('\n');
}

function matchesAny(value: string, patterns: RegExp[]): boolean {
  return patterns.some((pattern) => pattern.test(value));
}
