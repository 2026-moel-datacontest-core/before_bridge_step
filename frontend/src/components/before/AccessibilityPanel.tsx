'use client';

import type {
  BeforeAccessibilityRecommendation,
  BeforeDisabilityType,
} from '@/types/before';

import styles from './AccessibilityPanel.module.css';

const OPTIONS: Array<{ key: BeforeDisabilityType; label: string }> = [
  { key: 'visual', label: '시각' },
  { key: 'hearing', label: '청각' },
  { key: 'mobility', label: '지체/뇌병변' },
  { key: 'cognitive', label: '발달/인지' },
  { key: 'mental', label: '정신' },
  { key: 'complex', label: '기타/복합' },
];

interface AccessibilityPanelProps {
  selectedDisability: BeforeDisabilityType | null;
  recommendation: BeforeAccessibilityRecommendation | null;
  isLoading: boolean;
  errorMessage: string | null;
  onSelectDisability: (disabilityType: BeforeDisabilityType) => void;
}

export function AccessibilityPanel({
  selectedDisability,
  recommendation,
  isLoading,
  errorMessage,
  onSelectDisability,
}: AccessibilityPanelProps) {
  return (
    <section className={styles.panel} aria-labelledby="before-accessibility-title">
      <div className={styles.header}>
        <span className={styles.badge}>Accessibility extension</span>
        <h2 id="before-accessibility-title" className={styles.title}>
          장애 특성을 반영한 권리·지원 안내를 받으시겠어요?
        </h2>
        <p className={styles.description}>
          결과 화면 옆에서 함께 확인하는 보조 패널입니다. 장애 유형을 고르면 상황에 맞는 권리,
          지원, 확인 질문을 카드로 정리해서 보여줍니다.
        </p>
      </div>

      <div className={styles.selectorBlock}>
        <p className={styles.selectorLabel}>유형 선택</p>
        <div className={styles.optionRow}>
          {OPTIONS.map((option) => {
            const active = selectedDisability === option.key;

            return (
              <button
                key={option.key}
                type="button"
                onClick={() => onSelectDisability(option.key)}
                className={[styles.optionChip, active ? styles.optionChipActive : '']
                  .filter(Boolean)
                  .join(' ')}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </div>

      {isLoading ? (
        <div className={styles.infoBox}>선택한 유형에 맞는 안내 카드를 불러오는 중입니다.</div>
      ) : null}

      {errorMessage ? <div className={styles.warningBox}>{errorMessage}</div> : null}

      {recommendation ? (
        <div className={styles.cardStack}>
          <div className={styles.overviewCard}>
            <p className={styles.overviewEyebrow}>{recommendation.disability_label} 맞춤 개요</p>
            <p className={styles.overviewText}>{recommendation.overview}</p>
          </div>

          {recommendation.cards.map((card) => (
            <div
              key={card.id}
              className={[
                styles.recommendationCard,
                card.kind === 'right'
                  ? styles.recommendationRight
                  : card.kind === 'support'
                    ? styles.recommendationSupport
                    : card.kind === 'question'
                      ? styles.recommendationQuestion
                      : styles.recommendationLaw,
              ].join(' ')}
            >
              <div className={styles.recommendationHeader}>
                <div>
                  <p className={styles.cardKind}>{card.kind}</p>
                  <h3 className={styles.cardTitle}>{card.title}</h3>
                </div>
                <span className={styles.cardArrow}>›</span>
              </div>
              <p className={styles.cardDescription}>{card.description}</p>
              {card.action_hint ? <p className={styles.cardHint}>{card.action_hint}</p> : null}
              <div className={styles.lawRefRow}>
                {card.law_refs.map((lawRef) => (
                  <span key={`${card.id}-${lawRef}`} className={styles.lawRef}>
                    {lawRef}
                  </span>
                ))}
              </div>
            </div>
          ))}

          <div className={styles.nextStepCard}>
            <p className={styles.overviewEyebrow}>다음 단계</p>
            <p className={styles.overviewText}>
              필요한 경우 여기서 기관 링크, 신청 페이지, 준비 체크리스트 같은 후속 안내를 이어서
              확인할 수 있습니다.
            </p>
          </div>
        </div>
      ) : (
        <div className={styles.emptyState}>
          아직 선택된 유형이 없습니다. 위 토글에서 유형을 고르면 권리 안내 카드와 관련 법 조항 칩이
          여기에 표시됩니다.
        </div>
      )}
    </section>
  );
}
