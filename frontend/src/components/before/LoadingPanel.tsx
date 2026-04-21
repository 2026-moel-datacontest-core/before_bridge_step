'use client';

import type { BeforeReviewJob, BeforeReviewJobStep } from '@/types/before';

import styles from './LoadingPanel.module.css';

interface LoadingPanelProps {
  fileCount: number;
  job: BeforeReviewJob | null;
}

function getStepIndicator(step: BeforeReviewJobStep): string {
  if (step.status === 'completed') {
    return '✓';
  }

  if (step.status === 'failed') {
    return '!';
  }

  if (step.status === 'running') {
    return '•';
  }

  return '○';
}

export function LoadingPanel({ fileCount, job }: LoadingPanelProps) {
  const steps = job?.steps ?? [];
  const activeStep = steps.find((step) => step.status === 'running') ?? null;

  return (
    <section className={styles.panel} aria-labelledby="before-loading-title">
      <div className={styles.grid}>
        <div className={styles.mainColumn}>
          <span className={styles.badge}>Analysis in progress</span>
          <h2 id="before-loading-title" className={styles.title}>
            계약서를 읽고 결과를 조립하는 중입니다
          </h2>
          <p className={styles.description}>
            업로드된 파일 {fileCount}개를 기준으로 OCR, 항목 비교, 수치 검증, 설명 생성 단계를
            순서대로 수행합니다. 실제 before API가 연결된 경우에는 작업 상태를 주기적으로 조회하고,
            연결되지 않은 경우에는 데모용 mock 흐름을 대신 표시합니다.
          </p>

          {job ? (
            <div className={styles.statusBox}>
              <p className={styles.statusTitle}>현재 상태: {job.status}</p>
              <p className={styles.statusText}>
                {activeStep
                  ? `${activeStep.order}단계 진행 중: ${activeStep.label}`
                  : '작업 상태를 불러오는 중입니다.'}
              </p>
              {activeStep?.message ? (
                <p className={styles.statusSubtext}>{activeStep.message}</p>
              ) : null}
            </div>
          ) : null}

          <div className={styles.stepList}>
            {steps.map((step, index) => (
              <div key={step.key} className={styles.stepRow}>
                <div
                  className={[
                    styles.stepIndicator,
                    step.status === 'running' ? styles.stepIndicatorRunning : '',
                    step.status === 'completed' ? styles.stepIndicatorCompleted : '',
                    step.status === 'failed' ? styles.stepIndicatorFailed : '',
                  ]
                    .filter(Boolean)
                    .join(' ')}
                  aria-hidden="true"
                >
                  {getStepIndicator(step)}
                </div>
                <div className={styles.stepBody}>
                  <p className={styles.stepLabel}>Step {index + 1}</p>
                  <p className={styles.stepTitle}>{step.label}</p>
                  {step.message ? <p className={styles.stepMessage}>{step.message}</p> : null}
                </div>
              </div>
            ))}
          </div>
        </div>

        <aside className={styles.sideColumn} aria-label="분석 흐름 안내">
          <p className={styles.sideEyebrow}>What happens next</p>
          <ul className={styles.sideList}>
            <li>OCR은 한 번만 수행하고 이후 단계는 같은 snapshot 기준으로 이어집니다.</li>
            <li>작업 상태는 review job 단계를 기준으로 다시 불러와 반영합니다.</li>
            <li>before API가 준비되지 않은 환경에서는 mock 시나리오 버튼으로 같은 화면 흐름을 볼 수 있습니다.</li>
          </ul>
        </aside>
      </div>
    </section>
  );
}
