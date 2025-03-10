import { Injectable, signal } from '@angular/core';
import { Message } from '../models/message.model';
import { v4 as uuidv4 } from 'uuid';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  private storageKeyPrefix = 'llm-app-messages-';
  private messagesSignal = signal<Message[]>([]);
  private currentProjectId: string | null = null;
  
  messages = this.messagesSignal.asReadonly();
  
  constructor() {}
  
  loadMessagesForProject(projectId: string): void {
    this.currentProjectId = projectId;
    const storageKey = this.storageKeyPrefix + projectId;
    const stored = localStorage.getItem(storageKey);
    
    if (stored) {
      const parsed = JSON.parse(stored);
      // Convert string dates back to Date objects
      const messages = parsed.map((m: any) => ({
        ...m,
        timestamp: new Date(m.timestamp)
      }));
      this.messagesSignal.set(messages);
    } else {
      this.messagesSignal.set([]);
    }
  }
  
  private saveMessages(): void {
    if (!this.currentProjectId) return;
    const storageKey = this.storageKeyPrefix + this.currentProjectId;
    localStorage.setItem(storageKey, JSON.stringify(this.messagesSignal()));
  }
  
  addUserMessage(content: string): Message {
    if (!this.currentProjectId) {
      throw new Error('No project selected');
    }
    
    const message: Message = {
      id: uuidv4(),
      content,
      role: 'user',
      timestamp: new Date(),
      projectId: this.currentProjectId
    };
    
    this.messagesSignal.update(messages => [...messages, message]);
    this.saveMessages();
    return message;
  }
  
  addAssistantMessage(content: string): Message {
    if (!this.currentProjectId) {
      throw new Error('No project selected');
    }
    
    const message: Message = {
      id: uuidv4(),
      content,
      role: 'assistant',
      timestamp: new Date(),
      projectId: this.currentProjectId
    };
    
    this.messagesSignal.update(messages => [...messages, message]);
    this.saveMessages();
    return message;
  }
  
  clearMessages(): void {
    this.messagesSignal.set([]);
    this.saveMessages();
  }
  
  getRecentMessages(limit: number = 10): Message[] {
    // Get recent messages across all projects
    const allMessages: Message[] = [];
    
    const projectIds = localStorage.getItem('llm-app-projects') 
      ? JSON.parse(localStorage.getItem('llm-app-projects') || '[]').map((p: any) => p.id) 
      : [];
    
    for (const projectId of projectIds) {
      const storageKey = this.storageKeyPrefix + projectId;
      const stored = localStorage.getItem(storageKey);
      
      if (stored) {
        const parsed = JSON.parse(stored);
        for (const message of parsed) {
          allMessages.push({
            ...message,
            timestamp: new Date(message.timestamp)
          });
        }
      }
    }
    
    return allMessages
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }
}
