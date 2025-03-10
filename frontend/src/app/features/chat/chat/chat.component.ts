import { AfterViewChecked, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, Subscription } from 'rxjs';
import { Message } from '../../../models/message.model';
import { Project } from '../../../models/project.model';
import { LlmService } from '../../../services/llm.service';
import { MessageService } from '../../../services/message.service';
import { ProjectService } from '../../../services/project.services';
import { HeaderComponent } from '../../../components/header/header.component';
import { NgFor, NgIf, AsyncPipe } from '@angular/common';
import { InputFieldComponent } from '../../../components/input-field/input-field.component';
import { MessageBubbleComponent } from '../../../components/message-bubble/message-bubble.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [NgFor, NgIf, AsyncPipe,HeaderComponent, InputFieldComponent, MessageBubbleComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('chatContainer') private chatContainer!: ElementRef;
  
  messages = this.messageService.messages;
  currentProject: Project | undefined;
  recentUserMessages: Message[] = [];
  isLoading = false;
  faqs!: Observable<{question: string, answer: string}[]>;
  
  private projectId!: string;
  private subscriptions: Subscription[] = [];
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private messageService: MessageService,
    private projectService: ProjectService,
    private llmService: LlmService
  ) {}
  
  ngOnInit(): void {
    this.subscriptions.push(
      this.route.paramMap.subscribe(params => {
        const id = params.get('id');
        if (id) {
          this.projectId = id;
          this.loadProject();
        } else {
          this.router.navigate(['/projects']);
        }
      })
    );
    
    this.faqs = this.llmService.getFAQs();
    this.loadRecentMessages();
  }
  
  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }
  
  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
  
  private loadProject(): void {
    this.currentProject = this.projectService.getProject(this.projectId);
    if (!this.currentProject) {
      this.router.navigate(['/projects']);
      return;
    }
    
    this.messageService.loadMessagesForProject(this.projectId);
  }
  
  private loadRecentMessages(): void {
    // Get only user messages for the sidebar
    const messages = this.messageService.getRecentMessages()
      .filter(message => message.role === 'user');
    
    this.recentUserMessages = messages;
  }
  
  sendMessage(content: string): void {
    if (!content.trim()) return;
    
    // Add user message
    this.messageService.addUserMessage(content);
    this.isLoading = true;
    
    // Get response from LLM service
    this.subscriptions.push(
      this.llmService.generateResponse(content).subscribe({
        next: (response) => {
          this.messageService.addAssistantMessage(response);
          this.isLoading = false;
          this.loadRecentMessages(); // Refresh recent messages
        },
        error: (error) => {
          console.error('Error getting response:', error);
          this.messageService.addAssistantMessage('Sorry, I encountered an error processing your request.');
          this.isLoading = false;
        }
      })
    );
  }
  
  askQuestion(question: string): void {
    this.sendMessage(question);
  }
  
  jumpToMessage(message: Message): void {
    // This is a simplified implementation
    // In a real app, you might want to scroll to the actual message
    // or implement a search functionality
    // For now, we'll just add the message to the input
    this.sendMessage(message.content);
  }
  
  navigateToProjects(): void {
    this.router.navigate(['/projects']);
  }
  
  private scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }
}
