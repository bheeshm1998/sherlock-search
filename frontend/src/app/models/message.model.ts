export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
}

export interface MessageGroup {
  date: Date;
  formattedDate: string;
  messages: Message[];
}