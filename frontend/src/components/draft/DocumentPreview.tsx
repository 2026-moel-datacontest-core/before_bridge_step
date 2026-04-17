import type { ReactNode } from 'react';

import styles from './DocumentPreview.module.css';

interface DocumentPreviewProps {
  id?: string;
  title: string;
  renderedText: string;
}

const CONFIRMATION_PLACEHOLDER_PATTERN = /(\[[^\]\n]*확인 필요[^\]\n]*\])/g;
const CONFIRMATION_PLACEHOLDER_SEGMENT = /^\[[^\]\n]*확인 필요[^\]\n]*\]$/;

function renderDocumentContent(content: string): ReactNode {
  return content.split(CONFIRMATION_PLACEHOLDER_PATTERN).map((part, index) => {
    if (part.length === 0) {
      return null;
    }

    if (CONFIRMATION_PLACEHOLDER_SEGMENT.test(part)) {
      return (
        <span key={`${part}-${index}`} className={styles.placeholder}>
          {part}
        </span>
      );
    }

    return part;
  });
}

export function DocumentPreview({ id, title, renderedText }: DocumentPreviewProps) {
  const content = renderedText.trim();

  return (
    <section className={styles.section} aria-labelledby="document-preview-title">
      <div className={styles.header}>
        <p className={styles.eyebrow}>초안 본문</p>
        <h2 id="document-preview-title" className={styles.title}>
          {title}
        </h2>
      </div>
      <article
        id={id}
        className={styles.paper}
        role="document"
        tabIndex={-1}
        aria-label="생성된 문서 초안"
      >
        {content.length > 0 ? renderDocumentContent(content) : '초안 본문을 생성하지 못했습니다.'}
        <p className={styles.printDisclaimer}>
          이 문서는 제출 전 검토용 초안입니다. 법률 판단이 아니며, 제출 전 전문가 확인을
          권장합니다.
        </p>
      </article>
    </section>
  );
}
