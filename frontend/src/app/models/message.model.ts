export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
  projectId: string;
  isRead?: boolean;
  reactionType?: string;
  // Add for better history view
  preview?: string;
}

export interface MessageGroup {
  date: Date;
  formattedDate: string;
  messages: Message[];
}