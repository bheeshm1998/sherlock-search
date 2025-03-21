import { Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-input-field',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './input-field.component.html',
  styleUrl: './input-field.component.scss'
})
export class InputFieldComponent {
  @ViewChild('messageInput') messageInput!: ElementRef<HTMLTextAreaElement>;
  @Output() send = new EventEmitter<string>();
  @Input() isLoading = false;
  
  message = '';
  
  sendMessage(): void {
    if (this.message.trim() && !this.isLoading) {
      this.send.emit(this.message);
      this.message = '';
      
      // Focus the input after sending
      setTimeout(() => {
        this.messageInput.nativeElement.focus();
      }, 0);
    }
  }
  
  handleEnter(event: any): void {
    // Send message on Enter (but allow Shift+Enter for new lines)
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}