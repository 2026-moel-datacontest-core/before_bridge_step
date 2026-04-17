import { CitationPill } from '@/components/ui/CitationPill';
import type { DraftLegalBasisSection } from '@/types/api';

import styles from './LegalBasisPanel.module.css';

interface LegalBasisPanelProps {
  citedArticles: string[];
  legalBasis: DraftLegalBasisSection[];
  sourceContextIds: number[];
  missingLegalBasis: string[];
}

export function LegalBasisPanel({
  citedArticles,
  legalBasis,
  sourceContextIds,
  missingLegalBasis,
}: LegalBasisPanelProps) {
  return (
    <section className={styles.panel} aria-labelledby="legal-basis-title">
      <h2 id="legal-basis-title" className={styles.title}>
        법적 근거
      </h2>

      {citedArticles.length > 0 ? (
        <div className={styles.citationList}>
          {citedArticles.map((article) => (
            <CitationPill key={article} label={article} />
          ))}
        </div>
      ) : (
        <p className={styles.emptyText}>표시할 인용 조문이 없습니다.</p>
      )}

      {legalBasis.length > 0 ? (
        <ul className={styles.basisList}>
          {legalBasis.map((basis) => (
            <li key={`${basis.citation_label}-${basis.summary}`} className={styles.basisItem}>
              <p className={styles.basisLabel}>{basis.citation_label}</p>
              <p className={styles.basisSummary}>{basis.summary}</p>
            </li>
          ))}
        </ul>
      ) : null}

      {missingLegalBasis.length > 0 ? (
        <div className={styles.missingLegalBasis}>
          <p className={styles.missingTitle}>추가 법적 근거 확인 필요</p>
          <ul className={styles.missingList}>
            {missingLegalBasis.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <details className={styles.debug}>
        <summary>디버그 정보</summary>
        <p className={styles.debugText}>
          source_context_ids: {sourceContextIds.length > 0 ? sourceContextIds.join(', ') : '없음'}
        </p>
      </details>
    </section>
  );
}
