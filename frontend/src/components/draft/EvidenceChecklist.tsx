import styles from './EvidenceChecklist.module.css';

interface EvidenceChecklistProps {
  items: string[];
}

export function EvidenceChecklist({ items }: EvidenceChecklistProps) {
  return (
    <section className={styles.panel} aria-labelledby="evidence-checklist-title">
      <h2 id="evidence-checklist-title" className={styles.title}>
        증거 체크리스트
      </h2>
      {items.length > 0 ? (
        <ul className={styles.list}>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className={styles.emptyText}>표시할 증거 체크리스트가 없습니다.</p>
      )}
    </section>
  );
}
