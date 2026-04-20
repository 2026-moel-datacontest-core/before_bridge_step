'use client';

import {
  createContext,
  type Dispatch,
  type ReactNode,
  useContext,
  useMemo,
  useReducer,
} from 'react';

import type { FlowAction, KLaborShieldFlowState } from '@/types/flow';

export const initialFlowState: KLaborShieldFlowState = {
  user_statement: '',
  is_scn_demo_preset: false,
  selected_preset_id: null,
  answer_response: null,
  selected_document_type: null,
  legal_basis: null,
  case_intake_form: null,
  case_intake: null,
  evidence_status_map: {},
  draft_response: null,
};

export function flowReducer(
  state: KLaborShieldFlowState,
  action: FlowAction,
): KLaborShieldFlowState {
  switch (action.type) {
    case 'SET_STATEMENT':
      return {
        ...state,
        user_statement: action.payload.statement,
        is_scn_demo_preset: action.payload.is_preset,
        selected_preset_id: action.payload.selected_preset_id,
        answer_response: null,
        legal_basis: null,
        selected_document_type: null,
        case_intake_form: null,
        case_intake: null,
        draft_response: null,
      };
    case 'SET_ANSWER':
      return {
        ...state,
        answer_response: action.payload,
        legal_basis: null,
        selected_document_type: null,
        case_intake_form: null,
        case_intake: null,
        draft_response: null,
      };
    case 'SET_LEGAL_BASIS':
      return {
        ...state,
        legal_basis: action.payload,
      };
    case 'SET_DOCUMENT_TYPE':
      return {
        ...state,
        selected_document_type: action.payload,
        case_intake_form: null,
        case_intake: null,
        draft_response: null,
      };
    case 'SET_CASE_INTAKE_FORM':
      return {
        ...state,
        case_intake_form: action.payload,
      };
    case 'SET_CASE_INTAKE':
      return {
        ...state,
        case_intake: action.payload,
        draft_response: null,
      };
    case 'SET_EVIDENCE_STATUS':
      return {
        ...state,
        evidence_status_map: {
          ...state.evidence_status_map,
          [action.payload.key]: action.payload.status,
        },
      };
    case 'SET_DRAFT':
      return {
        ...state,
        draft_response: action.payload,
      };
    case 'CLEAR_DRAFT':
      return {
        ...state,
        draft_response: null,
      };
    case 'CLEAR_DRAFT_AND_CASE_INTAKE':
      return {
        ...state,
        case_intake_form: null,
        case_intake: null,
        draft_response: null,
      };
    case 'RESET':
      return initialFlowState;
    default:
      return state;
  }
}

interface FlowContextValue {
  state: KLaborShieldFlowState;
  dispatch: Dispatch<FlowAction>;
}

const FlowContext = createContext<FlowContextValue | null>(null);

interface FlowProviderProps {
  children: ReactNode;
}

export function FlowProvider({ children }: FlowProviderProps) {
  const [state, dispatch] = useReducer(flowReducer, initialFlowState);
  const value = useMemo(() => ({ state, dispatch }), [state]);

  return <FlowContext.Provider value={value}>{children}</FlowContext.Provider>;
}

export function useFlow() {
  const context = useContext(FlowContext);

  if (context === null) {
    throw new Error('useFlow must be used within FlowProvider');
  }

  return context;
}
