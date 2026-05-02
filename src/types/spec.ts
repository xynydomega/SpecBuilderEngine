export type SpecNode = 'goal' | 'type' | 'inputs' | 'ui' | 'actions' | 'state' | 'validation' | 'api' | 'responses' | 'outputs';

export interface Behavior {
  validation: string[];
  actions: string[];
  api_calls: string[];
  responses: Record<string, string>;
}

export interface ArchitectSpec {
  goal: string;
  type_hypothesis: string[];
  inputs: string[];
  outputs: string[];
  ui: string[];
  state: string[];
  behavior: Behavior;
}

export const PRIORITY_ORDER: SpecNode[] = [
  'goal',
  'type',
  'inputs',
  'ui',
  'actions',
  'state',
  'validation',
  'api',
  'responses',
  'outputs'
];

export const NODE_LABELS: Record<SpecNode, string> = {
  goal: 'Goal',
  type: 'Type',
  inputs: 'Inputs',
  ui: 'User Interface',
  actions: 'Actions',
  state: 'System State',
  validation: 'Validation',
  api: 'API Calls',
  responses: 'Responses',
  outputs: 'Outputs'
};
