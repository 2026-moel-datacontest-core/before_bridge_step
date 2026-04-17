'use client';

import type { ReactNode } from 'react';

import styles from './Notification.module.css';

interface NotificationProps {
  variant?: 'info' | 'warning' | 'error' | 'success';
  title?: string;
  children: ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

const variantLabels = {
  info: '안내',
  warning: '주의',
  error: '오류',
  success: '완료',
} as const;

export function Notification({
  variant = 'info',
  title,
  children,
  actionLabel,
  onAction,
}: NotificationProps) {
  const role = variant === 'error' || variant === 'warning' ? 'alert' : 'status';

  return (
    <section className={`${styles.notification} ${styles[variant]}`} role={role}>
      <div className={styles.content}>
        <p className={styles.title}>{title ?? variantLabels[variant]}</p>
        <div className={styles.message}>{children}</div>
      </div>
      {actionLabel && onAction ? (
        <button className={styles.action} type="button" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </section>
  );
}
