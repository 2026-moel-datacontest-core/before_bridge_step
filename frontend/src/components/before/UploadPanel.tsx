'use client';

import type { ChangeEvent } from 'react';

import type { BeforeMockScenario } from '@/types/before';

import styles from './UploadPanel.module.css';

interface UploadPanelProps {
  files: File[];
  isSubmitting: boolean;
  errorMessage: string | null;
  onFilesChange: (files: File[]) => void;
  onAnalyze: () => void;
  onLoadMock: (scenario: BeforeMockScenario) => void;
}

const infoTiles = [
  {
    title: 'PDF 단일 업로드',
    description: 'PDF는 1개만 업로드할 수 있고, 파일당 최대 10MB까지 허용됩니다.',
  },
  {
    title: '다중 이미지 업로드',
    description: '이미지는 최대 5장까지 올릴 수 있고, 전체 업로드 용량은 20MB를 넘길 수 없습니다.',
  },
  {
    title: 'Mock review 고정',
    description: '이 단계에서는 고정 시나리오 결과로 UI 머지를 먼저 검증합니다.',
  },
];

const mockButtons: Array<{ scenario: BeforeMockScenario; label: string }> = [
  { scenario: 'sen0', label: '외국인 사례' },
  { scenario: 'sen1', label: '아르바이트 사례' },
  { scenario: 'sen2', label: '장애인 사례' },
];

export function UploadPanel({
  files,
  isSubmitting,
  errorMessage,
  onFilesChange,
  onAnalyze,
  onLoadMock,
}: UploadPanelProps) {
  function handleInput(event: ChangeEvent<HTMLInputElement>) {
    const nextFiles = Array.from(event.target.files ?? []);
    if (!nextFiles.length) {
      return;
    }

    onFilesChange([...files, ...nextFiles]);
    event.target.value = '';
  }

  function removeFile(index: number) {
    onFilesChange(files.filter((_, currentIndex) => currentIndex !== index));
  }

  return (
    <div className={styles.grid}>
      <section className={styles.primaryCard} aria-labelledby="before-upload-title">
        <div className={styles.header}>
          <div>
            <p className={styles.eyebrow}>Upload contract</p>
            <h2 id="before-upload-title" className={styles.title}>
              사진 여러 장이나 PDF 한 장을 올리고 분석 흐름을 시작하세요
            </h2>
            <p className={styles.description}>
              `jpg`, `png`, `pdf`를 지원합니다. 이미지 여러 장은 같은 계약서의 페이지
              순서대로 유지해 주세요. 이미지는 최대 5장, PDF는 1개만 업로드할 수 있으며
              파일당 최대 10MB, 전체 최대 20MB까지 허용됩니다. 예시 시나리오 버튼으로
              먼저 화면 흐름을 확인한 뒤 실제 업로드 방식으로 확장할 수 있습니다.
            </p>
          </div>
        </div>

        <label className={styles.dropzone}>
          <div className={styles.dropIcon}>+</div>
          <h3 className={styles.dropTitle}>파일을 드래그하거나 클릭해서 추가</h3>
          <p className={styles.dropDescription}>
            업로드 후 분석 시작을 누르면 `/before` 흐름에서 진행 상태와 결과 화면을 확인할 수 있습니다.
            이미지 5장 이하 또는 PDF 1개만 선택해 주세요.
          </p>
          <input
            type="file"
            multiple
            accept=".jpg,.jpeg,.png,.pdf"
            className={styles.hiddenInput}
            onChange={handleInput}
          />
        </label>

        <div className={styles.infoGrid}>
          {infoTiles.map((tile) => (
            <article key={tile.title} className={styles.infoTile}>
              <div className={styles.infoMark} />
              <h3 className={styles.infoTitle}>{tile.title}</h3>
              <p className={styles.infoDescription}>{tile.description}</p>
            </article>
          ))}
        </div>

        <div className={styles.fileSection}>
          <div className={styles.fileHeader}>
            <h3 className={styles.fileTitle}>Selected files</h3>
            <span className={styles.fileCount}>{files.length}개 선택됨</span>
          </div>

          <div className={styles.fileList}>
            {files.length ? (
              files.map((file, index) => (
                <div key={`${file.name}-${index}`} className={styles.fileRow}>
                  <div className={styles.fileMeta}>
                    <p className={styles.fileName}>{file.name}</p>
                    <p className={styles.fileSize}>
                      {Math.max(1, Math.round(file.size / 1024))} KB
                    </p>
                  </div>
                  <button
                    type="button"
                    className={styles.removeButton}
                    onClick={() => removeFile(index)}
                    disabled={isSubmitting}
                    aria-label={`${file.name} 삭제`}
                  >
                    x
                  </button>
                </div>
              ))
            ) : (
              <div className={styles.emptyState}>아직 선택된 파일이 없습니다.</div>
            )}
          </div>
        </div>

        {errorMessage ? <div className={styles.errorBox}>{errorMessage}</div> : null}

        <div className={styles.actionBar}>
          <button
            type="button"
            onClick={onAnalyze}
            disabled={isSubmitting}
            className={styles.primaryAction}
          >
            {isSubmitting ? '분석 중...' : '분석 시작'}
          </button>

          <div className={styles.mockActions}>
            {mockButtons.map((button) => (
              <button
                key={button.scenario}
                type="button"
                onClick={() => onLoadMock(button.scenario)}
                disabled={isSubmitting}
                className={styles.secondaryAction}
              >
                {button.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      <aside className={styles.sideCard} aria-label="before 로컬 모드 안내">
    <div className={styles.sideInner}>
      <div>
        <p className={styles.sideEyebrow}>Local server mode</p>
        <h3 className={styles.sideTitle}>같은 브랜드 안에서 계약서 분석 경험을 먼저 확인합니다</h3>
        <p className={styles.sideDescription}>
          업로드, 분석 진행, 결과 확인, 권리 안내가 한 서비스 안에서 자연스럽게 이어지도록
          구성했습니다. 실제 연동 전에도 전체 UX 리듬을 먼저 확인할 수 있습니다.
        </p>
      </div>

      <ol className={styles.sideList}>
        <li>1. 계약서 파일을 올리거나 예시 시나리오를 선택합니다.</li>
        <li>2. 분석 단계가 순서대로 진행되는 화면을 확인합니다.</li>
        <li>3. 결과 카드와 권리·지원 안내를 함께 검토합니다.</li>
      </ol>
    </div>
  </aside>
    </div>
  );
}
