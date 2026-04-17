'use client';

import { FormEvent, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';

import { Masthead } from '@/components/layout/Masthead';
import { Button } from '@/components/ui/Button';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { Notification } from '@/components/ui/Notification';
import { useFlow } from '@/context/FlowContext';
import { ApiError, fetchAnswer } from '@/lib/api';
import type { AnswerRequest } from '@/types/api';

import styles from './page.module.css';

const SCN_004_PRESET =
  '해고를 당했는데 서면통지는 없고 30일 전에 예고도 못 받았습니다. 퇴사 후 마지막 임금과 퇴직금도 14일 넘게 지급받지 못했습니다.';

interface AnswerErrorState {
  message: string;
  retryable: boolean;
  payload: AnswerRequest;
}

export default function AfterPage() {
  const router = useRouter();
  const { state, dispatch } = useFlow();
  const answerSubmittingRef = useRef(false);
  const [statement, setStatement] = useState(state.user_statement);
  const [isPreset, setIsPreset] = useState(state.is_scn_demo_preset);
  const [isLoading, setIsLoading] = useState(false);
  const [errorState, setErrorState] = useState<AnswerErrorState | null>(null);

  const trimmedStatement = statement.trim();
  const characterCount = trimmedStatement.length;
  const isShort = characterCount > 0 && characterCount < 10;
  const canSubmit = characterCount >= 10 && !isLoading;
  const isPresetTextUnchanged = statement === SCN_004_PRESET;

  const helperText = useMemo(() => {
    if (isShort) {
      return '상황을 10자 이상 입력하면 법 조문 찾기를 시작할 수 있습니다.';
    }

    if (isPreset) {
      return isPresetTextUnchanged
        ? 'SCN-004 데모 프리셋이 입력되었습니다.'
        : 'SCN-004 데모 프리셋을 바탕으로 수정 중입니다.';
    }

    return '해고, 임금, 퇴직금, 통지 방식처럼 핵심 사실을 함께 적어주세요.';
  }, [isPreset, isPresetTextUnchanged, isShort]);

  function buildAnswerPayload(): AnswerRequest | null {
    if (trimmedStatement.length < 10) {
      return null;
    }

    return {
      query: trimmedStatement,
      top_k: isPreset ? 10 : 5,
      ef_search: 100,
    };
  }

  async function submitStatement(payload = buildAnswerPayload()) {
    if (!payload || answerSubmittingRef.current) {
      return;
    }

    answerSubmittingRef.current = true;
    setIsLoading(true);
    setErrorState(null);
    dispatch({
      type: 'SET_STATEMENT',
      payload: { statement: payload.query, is_preset: payload.top_k === 10 },
    });

    try {
      const answer = await fetchAnswer(payload);

      dispatch({ type: 'SET_ANSWER', payload: answer });
      router.push('/after/result');
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : '연결을 확인하고 다시 시도해주세요.';
      const retryable = error instanceof ApiError ? error.retryable : true;

      setErrorState({ message, retryable, payload });
    } finally {
      setIsLoading(false);
      answerSubmittingRef.current = false;
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitStatement();
  }

  function handleStatementChange(value: string) {
    setStatement(value);
    setIsPreset((currentIsPreset) =>
      currentIsPreset && value.trim().length > 0,
    );
    setErrorState(null);
  }

  function handlePresetClick() {
    setStatement(SCN_004_PRESET);
    setIsPreset(true);
    setErrorState(null);
    dispatch({
      type: 'SET_STATEMENT',
      payload: { statement: SCN_004_PRESET, is_preset: true },
    });
  }

  return (
    <>
      <Masthead isLoading={isLoading} />
      <main className={styles.main}>
        <section className={styles.intro} aria-labelledby="after-title">
          <div className={styles.introInner}>
            <p className={styles.eyebrow}>After flow · SCN-004</p>
            <h1 id="after-title" className={styles.title}>
              해고와 미지급 임금 상황에 맞는 법 조문 찾기
            </h1>
            <p className={styles.lead}>
              현재 상황을 적으면 관련 조문과 주의사항을 먼저 확인합니다.
            </p>
          </div>
        </section>

        <section className={styles.formBand} aria-labelledby="statement-title">
          <div className={styles.formShell}>
            <form className={styles.form} onSubmit={handleSubmit} aria-busy={isLoading}>
              <div className={styles.formHeader}>
                <div>
                  <p className={styles.eyebrow}>Step 1</p>
                  <h2 id="statement-title" className={styles.sectionTitle}>
                    상황 입력
                  </h2>
                </div>
                <span className={styles.counter}>{characterCount}자</span>
              </div>

              <label className={styles.label} htmlFor="statement">
                한국어 진술
              </label>
              <textarea
                id="statement"
                className={styles.textarea}
                value={statement}
                onChange={(event) => handleStatementChange(event.target.value)}
                disabled={isLoading}
                aria-label="해고와 임금 상황 진술"
                aria-describedby="statement-helper"
                placeholder="예: 회사에서 갑자기 그만 나오라고 했고 서면통지는 받지 못했습니다. 마지막 임금과 퇴직금도 아직 받지 못했습니다."
              />
              <p
                id="statement-helper"
                className={isShort ? styles.warningText : styles.helperText}
              >
                {helperText}
              </p>

              <div className={styles.presetRow}>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={handlePresetClick}
                  disabled={isLoading}
                >
                  SCN-004 프리셋 입력
                </Button>
              </div>

              {errorState ? (
                <Notification
                  variant="error"
                  title="법 조문 검색 실패"
                  actionLabel={errorState.retryable ? '다시 시도하기' : undefined}
                  onAction={
                    errorState.retryable
                      ? () => void submitStatement(errorState.payload)
                      : undefined
                  }
                  onClose={() => setErrorState(null)}
                >
                  <p>{errorState.message}</p>
                </Notification>
              ) : null}

              <div className={styles.actionRow}>
                <Button type="submit" isLoading={isLoading} disabled={!canSubmit}>
                  법 조문 찾기 →
                </Button>
              </div>
            </form>
          </div>
        </section>

        <section className={styles.disclaimerBand}>
          <div className={styles.formShell}>
            <DisclaimerBanner />
          </div>
        </section>
      </main>
    </>
  );
}
