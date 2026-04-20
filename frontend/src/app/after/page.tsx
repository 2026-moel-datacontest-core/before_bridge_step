'use client';

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';

import { Masthead } from '@/components/layout/Masthead';
import { Button } from '@/components/ui/Button';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { Notification } from '@/components/ui/Notification';
import { SkipLink } from '@/components/ui/SkipLink';
import { useFlow } from '@/context/FlowContext';
import { ApiError, fetchAnswer } from '@/lib/api';
import {
  SCENARIO_PRESETS,
  getScenarioPreset,
  type ScenarioPresetId,
} from '@/lib/scenarioPresets';
import type { AnswerRequest } from '@/types/api';

import styles from './page.module.css';

interface AnswerErrorState {
  message: string;
  retryable: boolean;
  payload: AnswerRequest;
}

export default function AfterPage() {
  const router = useRouter();
  const { state, dispatch } = useFlow();
  const mainRef = useRef<HTMLElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const answerSubmittingRef = useRef(false);
  const [statement, setStatement] = useState(state.user_statement);
  const [selectedPresetId, setSelectedPresetId] = useState<ScenarioPresetId | null>(
    state.selected_preset_id,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [errorState, setErrorState] = useState<AnswerErrorState | null>(null);

  const trimmedStatement = statement.trim();
  const characterCount = trimmedStatement.length;
  const isShort = characterCount > 0 && characterCount < 10;
  const canSubmit = characterCount >= 10 && !isLoading;
  const selectedPreset = getScenarioPreset(selectedPresetId);
  const isPresetTextUnchanged = selectedPreset !== null && statement === selectedPreset.query;

  useEffect(() => {
    const frameId = window.requestAnimationFrame(() => {
      const focusTarget = textareaRef.current ?? mainRef.current;
      focusTarget?.focus();
    });

    return () => window.cancelAnimationFrame(frameId);
  }, []);

  const helperText = useMemo(() => {
    if (isShort) {
      return '상황을 10자 이상 입력하면 법 조문 찾기를 시작할 수 있습니다.';
    }

    if (selectedPreset) {
      return isPresetTextUnchanged
        ? `${selectedPreset.label} 프리셋이 입력되었습니다.`
        : `${selectedPreset.label} 프리셋을 바탕으로 수정 중입니다.`;
    }

    return '해고, 임금, 퇴직금, 사업장 변경, 육아휴직처럼 핵심 사실을 함께 적어주세요.';
  }, [isPresetTextUnchanged, isShort, selectedPreset]);

  function buildAnswerPayload(): AnswerRequest | null {
    if (trimmedStatement.length < 10) {
      return null;
    }

    const preset = getScenarioPreset(selectedPresetId);

    return {
      query: trimmedStatement,
      top_k: preset ? preset.recommendedTopK : 5,
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
    const preset = getScenarioPreset(selectedPresetId);
    dispatch({
      type: 'SET_STATEMENT',
      payload: {
        statement: payload.query,
        is_preset: preset !== null,
        selected_preset_id: preset?.id ?? null,
      },
    });

    try {
      const answer =
        preset && statement === preset.query && payload.query === preset.query
          ? preset.fixedAnswer
          : await fetchAnswer(payload);

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
    setErrorState(null);
  }

  function handlePresetClick(presetId: ScenarioPresetId) {
    const preset = getScenarioPreset(presetId);

    if (!preset) {
      return;
    }

    setStatement(preset.query);
    setSelectedPresetId(preset.id);
    setErrorState(null);
    dispatch({
      type: 'SET_STATEMENT',
      payload: {
        statement: preset.query,
        is_preset: true,
        selected_preset_id: preset.id,
      },
    });
  }

  return (
    <>
      <SkipLink />
      <Masthead isLoading={isLoading} />
      <main id="main-content" ref={mainRef} tabIndex={-1} className={styles.main}>
        <section className={styles.intro} aria-labelledby="after-title">
          <div className={styles.introInner}>
            <p className={styles.eyebrow}>After flow · Scenario presets</p>
            <h1 id="after-title" className={styles.title}>
              상황에 맞는 노동권 조문 찾기
            </h1>
            <p className={styles.lead}>
              현재 상황을 적으면 관련 조문과 주의사항을 먼저 확인합니다.
            </p>
          </div>
        </section>

        <section className={styles.formBand} aria-labelledby="statement-title">
          <div className={styles.formShell}>
            <form
              className={styles.form}
              onSubmit={handleSubmit}
              aria-busy={isLoading || undefined}
            >
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
                ref={textareaRef}
                className={styles.textarea}
                value={statement}
                onChange={(event) => handleStatementChange(event.target.value)}
                disabled={isLoading}
                aria-label="노동권 상황 진술"
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
                {SCENARIO_PRESETS.map((preset) => (
                  <Button
                    key={preset.id}
                    type="button"
                    variant={selectedPresetId === preset.id ? 'secondary' : 'ghost'}
                    onClick={() => handlePresetClick(preset.id)}
                    disabled={isLoading}
                    aria-pressed={selectedPresetId === preset.id}
                  >
                    {preset.label}
                  </Button>
                ))}
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
