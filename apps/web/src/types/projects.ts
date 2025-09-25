// ========================================
// PROJECT TYPES
// ========================================

export type OutputConfigType = {
  type: string;
  contents: string[];
};

export interface ProjectData {
  id: string;
  name: string;
  description: string;
  status: 'Active' | 'Planning' | 'On Hold' | 'Completed';
  progress: number;
  team: string[];
  dueDate: string;
  priority: 'High' | 'Medium' | 'Low';
  tags: string[];
}

export interface RequirementItem {
  id: string;
  title: string;
  description: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  status: 'Draft' | 'Review' | 'Approved' | 'Rejected';
  assignee?: string;
  dueDate?: string;
  tags: string[];
  comments: Array<{
    id: string;
    author: string;
    content: string;
    timestamp: string;
  }>;
}
