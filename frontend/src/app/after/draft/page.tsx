'use client';

import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

import { Masthead } from '@/components/layout/Masthead';
import { CautionsPanel } from '@/components/draft/CautionsPanel';
import { DocumentPreview } from '@/components/draft/DocumentPreview';
import { EvidenceChecklist } from '@/components/draft/EvidenceChecklist';
import { LegalBasisPanel } from '@/components/draft/LegalBasisPanel';
import { MissingFieldsPanel } from '@/components/draft/MissingFieldsPanel';
import { Button } from '@/components/ui/Button';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { SkipLink } from '@/components/ui/SkipLink';
import { useFlow } from '@/context/FlowContext';
import type { DocumentType } from '@/types/api';

import styles from './page.module.css';

const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  labor_office_wage_complaint: '고용노동청 임금체불 진정서 초안',
  labor_commission_unfair_dismissal_brief: '노동위원회 부당해고 구제신청 이유서 초안',
};

export default function AfterDraftPage() {
  const router = useRouter();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const { state, dispatch } = useFlow();
  const draft = state.draft_response;

  useEffect(() => {
    if (!draft) {
      router.replace('/after');
    }
  }, [draft, router]);

  useEffect(() => {
    if (draft) {
      const frameId = window.requestAnimationFrame(() => {
        headingRef.current?.focus();
      });

      return () => window.cancelAnimationFrame(frameId);
    }
  }, [draft]);

  if (!draft) {
    return (
      <>
        <SkipLink />
        <Masthead />
        <main id="main-content" tabIndex={-1} className={styles.main}>
          <p className={styles.redirectMessage}>처음 단계로 이동합니다.</p>
        </main>
      </>
    );
  }

  function resetFlow() {
    dispatch({ type: 'RESET' });
    router.push('/after');
  }

  function returnToIntake() {
    dispatch({ type: 'CLEAR_DRAFT' });
    router.push('/after/intake');
  }

  function returnToDocumentTypeSelection() {
    dispatch({ type: 'CLEAR_DRAFT' });

    if (state.answer_response) {
      router.push('/after/result');
      return;
    }

    router.push('/after');
  }

  return (
    <>
      <SkipLink
        links={[
          { href: '#main-content', label: '본문으로 건너뛰기' },
          { href: '#document-draft', label: '문서 초안으로 건너뛰기' },
        ]}
      />
      <Masthead />
      <main id="main-content" tabIndex={-1} className={styles.main}>
        <section className={styles.headerBand} aria-labelledby="draft-title">
          <div className={styles.shell}>
            <p className={styles.eyebrow}>Step 4 · 문서 초안</p>
            <h1 id="draft-title" ref={headingRef} tabIndex={-1} className={styles.title}>
              생성된 초안을 검토하세요
            </h1>
            <div className={styles.metaGrid}>
              <span className={styles.documentBadge}>
                {DOCUMENT_TYPE_LABELS[draft.document_type]}
              </span>
              <span className={styles.metaItem}>제출 대상: {draft.recipient}</span>
            </div>
          </div>
        </section>

        <div className={styles.contentGrid}>
          <section className={styles.previewColumn} aria-label="문서 초안 본문">
            <DisclaimerBanner>
              <p>이 문서는 제출 전 검토용 초안입니다. 사실관계와 제출 기관 안내를 확인하세요.</p>
            </DisclaimerBanner>
            <DocumentPreview
              id="document-draft"
              title={draft.title}
              renderedText={draft.rendered_text}
            />
          </section>

          <aside className={styles.sideColumn} aria-label="초안 확인 항목">
            <MissingFieldsPanel missingFields={draft.missing_fields} />
            <CautionsPanel cautions={draft.cautions} />
            <EvidenceChecklist items={draft.evidence_checklist} />
            <LegalBasisPanel
              citedArticles={draft.cited_articles}
              legalBasis={draft.legal_basis}
              sourceContextIds={draft.source_context_ids}
              missingLegalBasis={draft.missing_legal_basis}
            />
          </aside>
        </div>

        <div className={styles.actionBar}>
          <div className={styles.actionInner}>
            <Button type="button" onClick={returnToDocumentTypeSelection}>
              다른 문서 타입으로 생성하기
            </Button>
            <Button type="button" variant="ghost" onClick={returnToIntake}>
              사건 정보 수정하기
            </Button>
            <Button type="button" variant="ghost" onClick={resetFlow}>
              처음으로 돌아가기
            </Button>
          </div>
        </div>
      </main>
    </>
  );
}
