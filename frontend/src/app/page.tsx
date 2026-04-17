import styles from './page.module.css';

export default function HomePage() {
  return (
    <main className={styles.main}>
      <section className={styles.content} aria-labelledby="home-title">
        <p className={styles.eyebrow}>SCN-004 Phase 1A</p>
        <h1 id="home-title" className={styles.title}>
          K-Labor Shield 프론트엔드 기반
        </h1>
        <p className={styles.body}>
          Next.js App Router, strict TypeScript, design tokens, flow state, API helper만 준비되어 있습니다.
        </p>
      </section>
    </main>
  );
}
