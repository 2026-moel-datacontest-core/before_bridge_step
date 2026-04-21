'use client';

import { useMemo, useState } from 'react';

import { Button } from '@/components/ui/Button';
import type { BeforeReviewResult } from '@/types/before';

import styles from './ResultPanel.module.css';

interface ResultPanelProps {
  review: BeforeReviewResult;
  overviewCards: Array<{ label: string; value: string }>;
  onReset: () => void;
}

export function ResultPanel({ review, overviewCards, onReset }: ResultPanelProps) {
  const [openEvidenceIndex, setOpenEvidenceIndex] = useState<number | null>(0);

  const issueCards = useMemo(() => {
    if (review.important_points.length) {
      return review.important_points;
    }

    return Object.entries(review.rule_check ?? {})
      .filter(([, value]) => value.status !== 'PASS')
      .map(([key, value]) => ({
        title: key,
        status: value.status,
        severity: value.severity,
        law_ref: value.law_ref ?? '',
        description: value.message ?? '',
      }));
  }, [review.important_points, review.rule_check]);

  return (
    <div className={styles.stack}>
      <section className={styles.heroCard} aria-labelledby="before-result-title">
        <div className={styles.heroGlow} />
        <div className={styles.heroInner}>
          <div className={styles.heroCopy}>
            <span className={styles.badge}>Review result</span>
            <h2 id="before-result-title" className={styles.heroTitle}>
              {review.headline}
            </h2>
            <p className={styles.heroDescription}>{review.plain_language_summary}</p>
          </div>

          <div className={styles.heroActions}>
            <StatusBadge kind="status" value={review.overall_result} />
            <StatusBadge kind="severity" value={review.overall_severity} />
            <Button type="button" variant="ghost" onClick={onReset}>
              새 분석으로 돌아가기
            </Button>
          </div>
        </div>

        <div className={styles.overviewGrid}>
          {overviewCards.map((card) => (
            <div key={card.label} className={styles.overviewCard}>
              <p className={styles.overviewLabel}>{card.label}</p>
              <p className={styles.overviewValue}>{card.value}</p>
            </div>
          ))}
        </div>

        <div className={styles.contractInfo}>
          <InfoRow label="사업주" value={review.contract_info.employer} />
          <InfoRow label="근로자" value={review.contract_info.employee} />
          <InfoRow label="시작일" value={review.contract_info.start_date} />
          <InfoRow label="요약" value={review.summary} />
        </div>
      </section>

      <div className={styles.grid}>
        <div className={styles.mainColumn}>
          <section className={styles.card}>
            <div className={styles.sectionHeader}>
              <p className={styles.sectionEyebrow}>Issue cards</p>
              <h3 className={styles.sectionTitle}>핵심 문제 요약</h3>
            </div>

            <div className={styles.issueList}>
              {issueCards.length ? (
                issueCards.map((issue) => (
                  <article key={`${issue.title}-${issue.law_ref}`} className={styles.issueCard}>
                    <div className={styles.issueHeader}>
                      <div>
                        <h4 className={styles.issueTitle}>{issue.title}</h4>
                        {issue.law_ref ? <p className={styles.issueLawRef}>{issue.law_ref}</p> : null}
                      </div>
                      <div className={styles.issueBadges}>
                        <StatusBadge kind="status" value={issue.status} />
                        <StatusBadge kind="severity" value={issue.severity} />
                      </div>
                    </div>
                    <p className={styles.issueDescription}>{issue.description}</p>
                  </article>
                ))
              ) : (
                <div className={styles.emptyPositive}>
                  현재 결과 기준으로 바로 수정이 필요한 핵심 이슈는 없습니다.
                </div>
              )}
            </div>
          </section>

          <section className={styles.card}>
            <div className={styles.sectionHeader}>
              <p className={styles.sectionEyebrow}>Recommended actions</p>
              <h3 className={styles.sectionTitle}>권장 조치</h3>
            </div>

            <div className={styles.actionList}>
              {review.recommended_actions.map((action) => (
                <div key={action} className={styles.actionItem}>
                  {action}
                </div>
              ))}
            </div>
          </section>

          <section className={styles.card}>
            <div className={styles.sectionHeader}>
              <p className={styles.sectionEyebrow}>Evidence toggle</p>
              <h3 className={styles.sectionTitle}>근거와 원문</h3>
            </div>

            <div className={styles.evidenceList}>
              {review.evidence.map((evidence, index) => {
                const isOpen = openEvidenceIndex === index;

                return (
                  <div key={evidence.title} className={styles.evidenceCard}>
                    <button
                      type="button"
                      onClick={() => setOpenEvidenceIndex(isOpen ? null : index)}
                      className={styles.evidenceButton}
                    >
                      <div>
                        <p className={styles.evidenceIndex}>Evidence {index + 1}</p>
                        <h4 className={styles.evidenceTitle}>{evidence.title}</h4>
                      </div>
                      <span className={styles.evidenceToggle}>{isOpen ? '접기' : '열기'}</span>
                    </button>

                    {isOpen ? (
                      <div className={styles.evidenceBody}>
                        <pre className={styles.evidenceExcerpt}>{evidence.excerpt}</pre>
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        <aside className={styles.sideColumn}>
          <section className={styles.sideCard}>
            <div className={styles.sectionHeader}>
              <p className={styles.sectionEyebrow}>Summary notes</p>
              <h3 className={styles.sectionTitle}>전체 평가</h3>
            </div>

            <div className={styles.summaryList}>
              {review.overall_assessment.map((line) => (
                <div key={line} className={styles.summaryItem}>
                  {line}
                </div>
              ))}
            </div>
          </section>

          {review.ocr_warnings && review.ocr_warnings.length > 0 ? (
            <section className={styles.warningCard}>
              <div className={styles.sectionHeader}>
                <p className={styles.sectionEyebrow}>OCR warnings</p>
                <h3 className={styles.sectionTitle}>OCR 확인 필요</h3>
              </div>

              <div className={styles.warningList}>
                {review.ocr_warnings.map((warning) => (
                  <div key={warning.field} className={styles.warningItem}>
                    <p className={styles.warningField}>{warning.field}</p>
                    <p className={styles.warningNote}>{warning.note}</p>
                    <p className={styles.warningMeta}>
                      structured: {String(warning.structured)} / corrected:{' '}
                      {String(warning.corrected)}
                    </p>
                  </div>
                ))}
              </div>
            </section>
          ) : null}
        </aside>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.infoRow}>
      <p className={styles.infoLabel}>{label}</p>
      <p className={styles.infoValue}>{value}</p>
    </div>
  );
}

function StatusBadge({
  kind,
  value,
}: {
  kind: 'status' | 'severity';
  value: string;
}) {
  const className =
    kind === 'status'
      ? value === 'PASS'
        ? styles.statusPass
        : value === 'WARNING'
          ? styles.statusWarning
          : styles.statusViolation
      : value === 'NONE'
        ? styles.severityNone
        : value === 'LOW'
          ? styles.severityLow
          : value === 'MEDIUM'
            ? styles.severityMedium
            : value === 'HIGH'
              ? styles.severityHigh
              : styles.severityCritical;

  return <span className={[styles.badgeBase, className].join(' ')}>{value}</span>;
}
