import { create } from 'zustand';
import type { ArchitectSpec, SpecNode } from '../types/spec';

interface SpecState {
  spec: ArchitectSpec;
  currentStep: SpecNode;
  currentQuestion: string;
  suggestions: string[];
  isComplete: boolean;
  isLoading: boolean;
  
  // Actions
  submitIntent: (text: string) => Promise<void>;
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

const API_URL = import.meta.env.VITE_API_URL || '/api';

export const useSpecStore = create<SpecState>((set, get) => ({
  spec: initialSpec,
  currentStep: 'goal',
  currentQuestion: 'What are you trying to build today?',
  suggestions: [],
  isComplete: false,
  isLoading: false,

  submitIntent: async (text: string) => {
    set({ isLoading: true });
    try {
      const response = await fetch(`${API_URL}/map`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: json.stringify({
          user_text: text,
          current_field: get().currentStep,
          current_spec: get().spec
        })
      });

      if (!response.ok) throw new Error('Network response was not ok');
      
      const data = await response.json();
      
      set({
        spec: data.updated_spec,
        currentStep: data.next_field,
        currentQuestion: data.next_question,
        suggestions: data.suggestions,
        isComplete: data.is_complete,
        isLoading: false
      });
    } catch (error) {
      console.error('Failed to map intent:', error);
      set({ isLoading: false });
    }
  },

  reset: () => set({ 
    spec: initialSpec, 
    currentStep: 'goal', 
    currentQuestion: 'What are you trying to build today?',
    suggestions: [],
    isComplete: false, 
    isLoading: false 
  })
}));
