'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

import { AccessibilityPanel } from '@/components/before/AccessibilityPanel';
import { LoadingPanel } from '@/components/before/LoadingPanel';
import { ResultPanel } from '@/components/before/ResultPanel';
import { UploadPanel } from '@/components/before/UploadPanel';
import { Masthead } from '@/components/layout/Masthead';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { Notification } from '@/components/ui/Notification';
import { SkipLink } from '@/components/ui/SkipLink';
import {
  BeforeApiError,
  fetchBeforeAccessibility,
  getBeforeReviewJob,
  loadBeforeMockAccessibility,
  loadBeforeMockReview,
  startBeforeReviewJob,
} from '@/lib/before-api';
import type {
  BeforeAccessibilityRecommendation,
  BeforeDisabilityType,
  BeforeMockScenario,
  BeforeReviewJob,
  BeforeReviewResult,
  BeforeScreenState,
} from '@/types/before';

import styles from './page.module.css';

const mockLoadingSteps = [
  { key: 'file_validation', label: '파일 확인', message: '업로드 형식과 페이지 구성을 확인합니다.' },
  { key: 'ocr', label: 'OCR 추출', message: '계약서 본문을 구조화합니다.' },
  { key: 'section_compare', label: '계약 항목 비교', message: '표준 항목과 실제 조항을 대조합니다.' },
  { key: 'rule_validation', label: '수치 검증', message: '임금, 시간, 휴게 조건을 검토합니다.' },
  { key: 'explanation', label: '설명 생성', message: '사용자용 설명과 결과 요약을 만듭니다.' },
] as const;

function createMockJob(): BeforeReviewJob {
  const now = new Date().toISOString();

  return {
    job_id: 'before-mock-job',
    status: 'running',
    created_at: now,
    updated_at: now,
    steps: mockLoadingSteps.map((step, index) => ({
      key: step.key,
      label: step.label,
      order: index + 1,
      status: index === 0 ? 'running' : 'pending',
      message: index === 0 ? step.message : null,
    })),
    error: null,
  };
}

function advanceMockJob(job: BeforeReviewJob): BeforeReviewJob {
  const currentIndex = job.steps.findIndex((step) => step.status === 'running');

  if (currentIndex === -1) {
    return job;
  }

  return {
    ...job,
    updated_at: new Date().toISOString(),
    steps: job.steps.map((step, index) => {
      if (index < currentIndex) {
        return { ...step, status: 'completed', message: step.message ?? null };
      }

      if (index === currentIndex) {
        return { ...step, status: 'completed', message: step.message ?? null };
      }

      if (index === currentIndex + 1) {
        return { ...step, status: 'running', message: mockLoadingSteps[index].message };
      }

      return step;
    }),
  };
}

export default function BeforePage() {
  const uploadRef = useRef<HTMLElement | null>(null);
  const resultRef = useRef<HTMLElement | null>(null);
  const [screenState, setScreenState] = useState<BeforeScreenState>('home');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [loadingJob, setLoadingJob] = useState<BeforeReviewJob | null>(null);
  const [review, setReview] = useState<BeforeReviewResult | null>(null);
  const [selectedDisability, setSelectedDisability] = useState<BeforeDisabilityType | null>(null);
  const [accessibility, setAccessibility] = useState<BeforeAccessibilityRecommendation | null>(null);
  const [accessibilityError, setAccessibilityError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAccessibilityLoading, setIsAccessibilityLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const overviewCards = useMemo(() => {
    if (!review) {
      return [];
    }

    return [
      { label: '판정', value: review.overall_result },
      { label: '심각도', value: review.overall_severity },
      { label: '계약 유형', value: review.contract_info.type },
      { label: '검토 시각', value: new Date(review.reviewed_at).toLocaleString('ko-KR') },
    ];
  }, [review]);

  useEffect(() => {
    if (screenState === 'loading') {
      uploadRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    if (screenState === 'result') {
      resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [screenState]);

  useEffect(() => {
    if (!loadingJob) {
      return;
    }

    if (loadingJob.job_id === 'before-mock-job') {
      return;
    }

    if (loadingJob.status === 'completed') {
      if (loadingJob.result) {
        setReview(loadingJob.result);
        setScreenState('result');
      } else {
        setErrorMessage('분석은 완료되었지만 결과를 불러오지 못했습니다.');
        setScreenState('home');
      }
      setLoadingJob(null);
      setIsSubmitting(false);
      return;
    }

    if (loadingJob.status === 'failed') {
      setErrorMessage(loadingJob.error ?? '계약서 분석 중 문제가 발생했습니다.');
      setScreenState('home');
      setLoadingJob(null);
      setIsSubmitting(false);
      return;
    }

    let cancelled = false;
    const timerId = window.setTimeout(async () => {
      try {
        const nextJob = await getBeforeReviewJob(loadingJob.job_id);
        if (!cancelled) {
          setLoadingJob(nextJob);
        }
      } catch (error) {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof BeforeApiError
            ? error.message
            : '계약서 분석 상태를 불러오지 못했습니다.';
        setErrorMessage(message);
        setScreenState('home');
        setLoadingJob(null);
        setIsSubmitting(false);
      }
    }, 1000);

    return () => {
      cancelled = true;
      window.clearTimeout(timerId);
    };
  }, [loadingJob]);

  async function runMockReview(scenario: BeforeMockScenario) {
    setErrorMessage(null);
    setIsSubmitting(true);
    setScreenState('loading');
    setAccessibility(null);
    setAccessibilityError(null);
    setSelectedDisability(null);
    const initialJob = createMockJob();
    setLoadingJob(initialJob);

    const intervalId = window.setInterval(() => {
      setLoadingJob((currentJob) => {
        if (!currentJob) {
          return currentJob;
        }

        return advanceMockJob(currentJob);
      });
    }, 220);

    try {
      const nextReview = await loadBeforeMockReview(scenario);
      window.clearInterval(intervalId);
      setReview(nextReview);
      setScreenState('result');
    } catch {
      window.clearInterval(intervalId);
      setErrorMessage('before mock 결과를 불러오지 못했습니다.');
      setScreenState('home');
    } finally {
      setLoadingJob(null);
      setIsSubmitting(false);
    }
  }

  async function handleAnalyze() {
    if (!selectedFiles.length) {
      setErrorMessage('먼저 분석할 파일을 추가해 주세요.');
      return;
    }

    setErrorMessage(null);
    setIsSubmitting(true);
    setScreenState('loading');
    setAccessibility(null);
    setAccessibilityError(null);
    setSelectedDisability(null);
    setReview(null);

    try {
      const job = await startBeforeReviewJob(selectedFiles);
      setLoadingJob(job);
    } catch (error) {
      const message =
        error instanceof BeforeApiError
          ? error.message
          : '계약서 분석 작업 생성에 실패했습니다.';
      setErrorMessage(message);
      setScreenState('home');
      setLoadingJob(null);
      setIsSubmitting(false);
    }
  }

  async function handleLoadMock(scenario: BeforeMockScenario) {
    await runMockReview(scenario);
  }

  async function handleSelectDisability(option: BeforeDisabilityType) {
    setSelectedDisability(option);
    setAccessibilityError(null);
    setIsAccessibilityLoading(true);

    try {
      const recommendation = review
        ? await fetchBeforeAccessibility(option, [])
        : await loadBeforeMockAccessibility(option);
      setAccessibility(recommendation);
    } catch (error) {
      if (review) {
        try {
          const fallback = await loadBeforeMockAccessibility(option);
          setAccessibility(fallback);
          setAccessibilityError(
            error instanceof BeforeApiError
              ? `${error.message} mock 안내를 대신 표시합니다.`
              : '장애 특화 안내를 불러오지 못해 mock 안내를 대신 표시합니다.',
          );
        } catch {
          setAccessibilityError('장애 특화 안내를 불러오지 못했습니다.');
        }
      } else {
        setAccessibilityError('장애 특화 안내를 불러오지 못했습니다.');
      }
    } finally {
      setIsAccessibilityLoading(false);
    }
  }

  function handleReset() {
    setScreenState('home');
    setSelectedFiles([]);
    setLoadingJob(null);
    setReview(null);
    setAccessibility(null);
    setSelectedDisability(null);
    setErrorMessage(null);
    setAccessibilityError(null);
    setIsSubmitting(false);
    setIsAccessibilityLoading(false);
  }

  return (
    <>
      <SkipLink />
      <Masthead isLoading={isSubmitting} />
      <main id="main-content" tabIndex={-1} className={styles.main}>
        <section className={styles.heroSection} aria-labelledby="before-title">
          <div className={styles.heroGlowPrimary} />
          <div className={styles.heroGlowSecondary} />
          <div className={styles.heroInner}>
            <div className={styles.heroCopy}>
              <p className={styles.eyebrow}>Before service</p>
              <h1 id="before-title" className={styles.title}>
                근로계약서 업로드부터 법령 기반 설명까지 한 흐름으로 확인하세요
              </h1>
              <p className={styles.lead}>
                계약서를 올리면 먼저 업로드 패널에서 파일을 정리하고, 분석을 시작한 뒤에만 진행 상태와
                결과 섹션이 아래로 이어집니다. 현재 데모 단계에서는 고정 시나리오 기반 결과로 흐름을
                검증합니다.
              </p>

              <div className={styles.badgeRow}>
                <span className={styles.documentBadge}>contract analysis</span>
                <span className={styles.metaItem}>upload first</span>
                <span className={styles.metaItem}>result on demand</span>
              </div>

              <div className={styles.featureGrid}>
                <article className={styles.featureCard}>
                  <h2 className={styles.featureTitle}>업로드 단일 진입</h2>
                  <p className={styles.featureDescription}>
                    처음 화면에서는 계약서 파일 선택과 mock 시나리오 실행만 먼저 보여줍니다.
                  </p>
                </article>
                <article className={styles.featureCard}>
                  <h2 className={styles.featureTitle}>단계별 생성</h2>
                  <p className={styles.featureDescription}>
                    분석을 시작한 뒤에만 로딩 패널이 나타나고, 완료 후 결과 섹션이 생성됩니다.
                  </p>
                </article>
                <article className={styles.featureCard}>
                  <h2 className={styles.featureTitle}>결과 옆 권리 안내</h2>
                  <p className={styles.featureDescription}>
                    장애 특화 안내 패널은 결과를 읽는 시점에 맞춰 오른쪽에서 함께 확인합니다.
                  </p>
                </article>
              </div>
            </div>

            <aside className={styles.heroPanel} aria-label="현재 상태">
              <div className={styles.heroPanelCard}>
                <p className={styles.panelEyebrow}>Service focus</p>
                <h2 className={styles.panelTitle}>원본 before_web 흐름에 맞춘 구조</h2>
                <ul className={styles.panelList}>
                  <li>업로드 단계에서는 입력 패널만 먼저 노출</li>
                  <li>분석 시작 후 로딩 패널이 아래 섹션으로 생성</li>
                  <li>결과가 생기면 결과와 권리 안내가 함께 등장</li>
                  <li>초기 노출 정보는 업로드 판단에 필요한 내용만 유지</li>
                </ul>
              </div>
              <div className={styles.heroPanelStrip}>
                <span className={styles.stripLabel}>Flow summary</span>
                <p>Hero 이후에는 업로드만 먼저 보이고, 나머지 패널은 상태가 바뀌는 시점에 순차적으로 나타납니다.</p>
              </div>
            </aside>
          </div>
        </section>

        <section ref={uploadRef} className={styles.uploadSection} aria-label="before 업로드 섹션">
          <div className={styles.sectionInner}>
            {errorMessage ? (
              <Notification
                variant="error"
                title="before 서비스 준비 중 오류"
                onClose={() => setErrorMessage(null)}
              >
                <p>{errorMessage}</p>
              </Notification>
            ) : null}

            <UploadPanel
              files={selectedFiles}
              isSubmitting={isSubmitting}
              errorMessage={errorMessage}
              onFilesChange={setSelectedFiles}
              onAnalyze={() => void handleAnalyze()}
              onLoadMock={(scenario) => void handleLoadMock(scenario)}
            />

            <div className={styles.inlineInfoGrid}>
              <section className={styles.infoCard}>
                <p className={styles.infoEyebrow}>Upload step</p>
                <h2 className={styles.infoTitle}>처음에는 입력 패널 하나만 보입니다</h2>
                <p className={styles.infoBody}>
                  원본 `before_web`와 같은 방식으로, 파일을 고르고 분석을 시작하기 전까지는 보조 결과 패널을
                  먼저 열지 않습니다.
                </p>
              </section>

              <DisclaimerBanner>
                <p>
                  현재 화면은 계약서 분석 흐름을 미리 확인하는 데모 버전입니다. 실제 계약 문서를 업로드하기
                  전에는 예시 결과와 안내 카드를 먼저 살펴보세요.
                </p>
              </DisclaimerBanner>
            </div>
          </div>
        </section>

        {screenState === 'loading' ? (
          <section className={styles.loadingSection} aria-label="before 분석 진행">
            <div className={styles.sectionInner}>
              <LoadingPanel fileCount={selectedFiles.length || 1} job={loadingJob} />
            </div>
          </section>
        ) : null}

        {screenState === 'result' && review ? (
          <section ref={resultRef} className={styles.resultSection} aria-label="before 분석 결과">
            <div className={styles.sectionInner}>
              <div className={styles.resultGrid}>
                <div className={styles.resultPrimary}>
                  <ResultPanel review={review} overviewCards={overviewCards} onReset={handleReset} />
                </div>

                <aside className={styles.resultAside}>
                  <AccessibilityPanel
                    selectedDisability={selectedDisability}
                    recommendation={accessibility}
                    isLoading={isAccessibilityLoading}
                    errorMessage={accessibilityError}
                    onSelectDisability={(option) => void handleSelectDisability(option)}
                  />
                </aside>
              </div>
            </div>
          </section>
        ) : null}
      </main>
    </>
  );
}
