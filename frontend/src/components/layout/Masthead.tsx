import Link from 'next/link';

import styles from './Masthead.module.css';

interface MastheadProps {
  isLoading?: boolean;
}

export function Masthead({ isLoading = false }: MastheadProps) {
  return (
    <header className={styles.masthead}>
      <div className={styles.inner}>
        <Link className={styles.brand} href="/">
          <span className={styles.mark} aria-hidden="true">
            KL
          </span>
          <span>K-Labor Shield</span>
        </Link>
        <nav className={styles.nav} aria-label="주요 화면">
          <Link href="/after">After</Link>
        </nav>
      </div>
      <div
        className={isLoading ? styles.progress : styles.progressHidden}
        aria-hidden={!isLoading}
      />
    </header>
  );
}
