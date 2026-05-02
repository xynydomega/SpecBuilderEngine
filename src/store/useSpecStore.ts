import { create } from 'zustand';
import { ArchitectSpec, SpecNode, PRIORITY_ORDER } from '../types/spec';

interface SpecState {
  spec: ArchitectSpec;
  currentStep: SpecNode;
  isComplete: boolean;
  
  // Actions
  updateField: (node: SpecNode, value: any) => void;
  nextStep: () => void;
  reset: () => void;
}

const initialSpec: ArchitectSpec = {
  goal: '',
  type_hypothesis: [],
  inputs: [],
  outputs: [],
  ui: [],
  state: [],
  behavior: {
    validation: [],
    actions: [],
    api_calls: [],
    responses: {}
  }
};

export const useSpecStore = create<SpecState>((set, get) => ({
  spec: initialSpec,
  currentStep: 'goal',
  isComplete: false,

  updateField: (node, value) => {
    set((state) => {
      const newSpec = { ...state.spec };
      
      if (node === 'goal') {
        newSpec.goal = value as string;
      } else if (node === 'actions' || node === 'validation' || node === 'api') {
        const key = node === 'api' ? 'api_calls' : node;
        newSpec.behavior = {
          ...newSpec.behavior,
          [key]: value as string[]
        };
      } else if (node === 'responses') {
        newSpec.behavior = {
          ...newSpec.behavior,
          responses: value as Record<string, string>
        };
      } else if (node === 'type') {
        newSpec.type_hypothesis = value as string[];
      } else {
        (newSpec as any)[node] = value;
      }

      return { spec: newSpec };
    });
    
    // Automatically move to next step logic could go here or be called explicitly
    get().nextStep();
  },

  nextStep: () => {
    const { spec } = get();
    
    const findNext = () => {
      if (!spec.goal) return 'goal';
      if (spec.type_hypothesis.length === 0) return 'type';
      if (spec.inputs.length === 0) return 'inputs';
      if (spec.ui.length === 0) return 'ui';
      if (spec.behavior.actions.length === 0) return 'actions';
      if (spec.state.length === 0) return 'state';
      if (spec.behavior.validation.length === 0) return 'validation';
      if (spec.behavior.api_calls.length === 0) return 'api';
      if (Object.keys(spec.behavior.responses).length === 0) return 'responses';
      if (spec.outputs.length === 0) return 'outputs';
      return null;
    };

    const nextNode = findNext();
    if (nextNode) {
      set({ currentStep: nextNode, isComplete: false });
    } else {
      set({ isComplete: true });
    }
  },

  reset: () => set({ spec: initialSpec, currentStep: 'goal', isComplete: false })
}));
