import { Inject, Injectable, signal } from '@angular/core';
import { Message, MessageGroup } from '../models/message.model';
import { LocalStorageService } from './local-storage.service';
import { v4 as uuidv4 } from 'uuid';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  messages = signal<Message[]>([]);
  messageGroups = signal<MessageGroup[]>([]);
  
  constructor(@Inject(LocalStorageService) private storageService: LocalStorageService) {}
  
  loadMessagesForProject(projectId: string): void {
    const storedMessages = this.storageService.getItem(`messages_${projectId}`) || '[]';
    try {
      const parsedMessages = JSON.parse(storedMessages) as Message[];
      // Convert string timestamps back to Date objects
      const messages = parsedMessages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }));
      this.messages.set(messages);
      this.updateMessageGroups();
    } catch (e) {
      console.error('Error parsing stored messages:', e);
      this.messages.set([]);
    }
  }
  
  addUserMessage(content: string): void {
    const newMessage: Message = {
      id: uuidv4(),
      content,
      role: 'user',
      timestamp: new Date(),
      projectId: this.getCurrentProjectId(),
      preview: this.createMessagePreview(content)
    };
    
    this.addMessage(newMessage);
  }
  
  addAssistantMessage(content: string): void {
    const newMessage: Message = {
      id: uuidv4(),
      content,
      role: 'assistant',
      timestamp: new Date(),
      projectId: this.getCurrentProjectId()
    };
    
    this.addMessage(newMessage);
  }
  
  private addMessage(message: Message): void {
    this.messages.update(msgs => [...msgs, message]);
    this.saveMessages();
    this.updateMessageGroups();
  }
  
  private saveMessages(): void {
    const projectId = this.getCurrentProjectId();
    this.storageService.setItem(`messages_${projectId}`, JSON.stringify(this.messages()));
  }
  
  getRecentMessages(limit = 10): Message[] {
    // Get all user messages across all projects, sorted by timestamp (newest first)
    const allMessages = this.getAllMessages().filter(msg => msg.role === 'user');
    return allMessages
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }
  
  getAllMessages(): Message[] {
    // This function would ideally get messages from all projects
    // For now, we'll just return the current project's messages
    return this.messages();
  }
  
  private getCurrentProjectId(): string {
    // In a real app, you might get this from a service or route
    const urlParts = window.location.pathname.split('/');
    const projectIdIndex = urlParts.indexOf('chat') + 1;
    return urlParts[projectIdIndex] || 'default';
  }
  
  private createMessagePreview(content: string, maxLength = 50): string {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  }
  
  deleteMessage(messageId: string): void {
    this.messages.update(msgs => msgs.filter(msg => msg.id !== messageId));
    this.saveMessages();
    this.updateMessageGroups();
  }
  
  markMessageAsRead(messageId: string): void {
    this.messages.update(msgs => 
      msgs.map(msg => 
        msg.id === messageId ? { ...msg, isRead: true } : msg
      )
    );
    this.saveMessages();
  }
  
  private updateMessageGroups(): void {
    const groups: Record<string, Message[]> = {};
    
    // Group messages by date (just the day, not time)
    this.messages().forEach(message => {
      const date = new Date(message.timestamp);
      const dateKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
      
      if (!groups[dateKey]) {
        groups[dateKey] = [];
      }
      
      groups[dateKey].push(message);
    });
    
    // Convert groups object to array of MessageGroup
    const messageGroups: MessageGroup[] = Object.keys(groups).map(dateKey => {
      const [year, month, day] = dateKey.split('-').map(Number);
      const date = new Date(year, month, day);
      
      return {
        date,
        formattedDate: this.formatDate(date),
        messages: groups[dateKey].sort((a, b) => 
          b.timestamp.getTime() - a.timestamp.getTime()
        )
      };
    });
    
    // Sort groups by date (newest first)
    messageGroups.sort((a, b) => b.date.getTime() - a.date.getTime());
    
    this.messageGroups.set(messageGroups);
  }
  
  private formatDate(date: Date): string {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (this.isSameDay(date, today)) {
      return 'Today';
    } else if (this.isSameDay(date, yesterday)) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
      });
    }
  }
  
  private isSameDay(date1: Date, date2: Date): boolean {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  }
}