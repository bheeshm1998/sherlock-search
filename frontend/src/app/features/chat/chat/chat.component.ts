import { AfterViewChecked, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, Subscription } from 'rxjs';
import { Message } from '../../../models/message.model';
import { Project } from '../../../models/project.model';
import { LlmService } from '../../../services/llm.service';
import { MessageService } from '../../../services/message.service';
import { ProjectService } from '../../../services/project.services';
import { HeaderComponent } from '../../../components/header/header.component';
import { NgFor, NgIf, AsyncPipe, DatePipe, CommonModule } from '@angular/common';
import { InputFieldComponent } from '../../../components/input-field/input-field.component';
import { MessageBubbleComponent } from '../../../components/message-bubble/message-bubble.component';
import { ChatService } from '../../../services/chat.service';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [NgFor, NgIf, AsyncPipe, DatePipe, HeaderComponent, InputFieldComponent, MessageBubbleComponent, CommonModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('chatContainer') private chatContainer!: ElementRef;
  
  // messages = this.messageService.messages;
  // messageGroups = this.messageService.messageGroups;
  currentProject: Project | undefined;
  isLoading = false;
  // faqs!: Observable<{question: string, answer: string}[]>;

  messages: Message[] = [];

  userId: any = "";
  
  private projectId!: string;
  private subscriptions: Subscription[] = [];
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private messageService: MessageService,
    private projectService: ProjectService,
    private chatService: ChatService,
    private authService: AuthService
  ) {}
  
  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.projectId = params['projectId']; 
    });
    this.userId = this.authService.getCurrentUser();
    this.loadMessages();
    // this.faqs = this.chatService.getFAQs();
  }
  
  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }
  
  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
  
  private loadProject(): void {
    this.currentProject = this.projectService.getProject(this.projectId);
    
    // Load messages for this project
    this.messageService.loadMessagesForProject(this.projectId);
  }
  
  sendMessage(content: string): void {
    if (!content.trim()) return;
    
    // Add user message
    this.messageService.addUserMessage(content);
    this.isLoading = true;
    
    // Get response from LLM service
    this.subscriptions.push(
      this.chatService.generateResponse(content, this.projectId, this.userId).subscribe({
        next: (response) => {
          this.messageService.addAssistantMessage(response);
          this.isLoading = false;
          this.loadMessages();
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
    // Show the message content in the input field
    const inputField = document.querySelector('app-input-field textarea') as HTMLTextAreaElement;
    if (inputField) {
      inputField.value = message.content;
      inputField.focus();
    }
    
    // Alternatively, you could implement a "search" function to find and highlight 
    // this message in the conversation history
  }
  
  navigateToProjects(): void {
    this.router.navigate(['/admin-dashboard']);
  }
  
  private scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }
  loadMessages() {
    this.chatService.getMessages(this.projectId, this.userId).subscribe({
      next: (data) => {
        this.messages = data;
      },
      error: (err) => {
        console.error('Error fetching messages:', err);
      } 
    });
  }

}