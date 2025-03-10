import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-input-field',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './input-field.component.html',
  styleUrl: './input-field.component.scss'
})
export class InputFieldComponent {

  @Output() send = new EventEmitter<string>();
  message = '';

  onEnterPress(event: any): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Prevent default behavior (e.g., new line in textarea)
      this.sendMessage();
    }
  }

  sendMessage(): void {
    if (this.message.trim()) {
      this.send.emit(this.message);
      this.message = '';
    }
  }
}
