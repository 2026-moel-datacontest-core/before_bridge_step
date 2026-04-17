import styles from './DocumentPreview.module.css';

interface DocumentPreviewProps {
  title: string;
  renderedText: string;
}

export function DocumentPreview({ title, renderedText }: DocumentPreviewProps) {
  const content = renderedText.trim();

  return (
    <section className={styles.section} aria-labelledby="document-preview-title">
      <div className={styles.header}>
        <p className={styles.eyebrow}>초안 본문</p>
        <h2 id="document-preview-title" className={styles.title}>
          {title}
        </h2>
      </div>
      <article className={styles.paper} role="document" aria-label="생성된 문서 초안">
        {content.length > 0 ? content : '초안 본문을 생성하지 못했습니다.'}
      </article>
    </section>
  );
}
