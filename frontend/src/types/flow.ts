import type {
  AnswerResponse,
  CaseIntake,
  CaseIntakeFormValues,
  DocumentDraftResponse,
  DocumentType,
  EvidenceUiStatus,
  LegalBasisInput,
} from './api';
import type { ScenarioPresetId } from '@/lib/scenarioPresets';

export interface KLaborShieldFlowState {
  user_statement: string;
  selected_preset_id: ScenarioPresetId | null;
  answer_response: AnswerResponse | null;
  selected_document_type: DocumentType | null;
  legal_basis: LegalBasisInput | null;
  case_intake_form: CaseIntakeFormValues | null;
  case_intake: CaseIntake | null;
  evidence_status_map: Record<string, EvidenceUiStatus>;
  draft_response: DocumentDraftResponse | null;
}

export type FlowAction =
  | {
      type: 'SET_STATEMENT';
      payload: {
        statement: string;
        selected_preset_id: ScenarioPresetId | null;
      };
    }
  | { type: 'SET_ANSWER'; payload: AnswerResponse }
  | { type: 'SET_LEGAL_BASIS'; payload: LegalBasisInput }
  | { type: 'SET_DOCUMENT_TYPE'; payload: DocumentType }
  | { type: 'SET_CASE_INTAKE_FORM'; payload: CaseIntakeFormValues }
  | { type: 'SET_CASE_INTAKE'; payload: CaseIntake }
  | { type: 'SET_EVIDENCE_STATUS'; payload: { key: string; status: EvidenceUiStatus } }
  | { type: 'SET_DRAFT'; payload: DocumentDraftResponse }
  | { type: 'CLEAR_DRAFT' }
  | { type: 'CLEAR_DRAFT_AND_CASE_INTAKE' }
  | { type: 'RESET' };
