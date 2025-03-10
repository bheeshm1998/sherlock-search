import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LlmService {
  constructor() {}
  
  // Mock service for demo purposes
  // Replace with actual LLM API integration
  generateResponse(prompt: string): Observable<string> {
    // Sample responses for demonstration
    const responses = [
      "I'm your LLM assistant. How can I help you with your question?",
      "That's an interesting question. Based on my knowledge, I would say...",
      "Let me think about that for a moment. There are several ways to approach this problem.",
      "Thanks for your question. From my analysis, the key points to consider are...",
      "I understand what you're asking. Here's what I know about this topic..."
    ];
    
    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    // Simulate API delay
    return of(randomResponse).pipe(delay(1000));
  }
  
  getFAQs(): Observable<{question: string, answer: string}[]> {
    // Sample FAQs for demonstration
    const faqs = [
      {
        question: "How does this LLM work?",
        answer: "This LLM processes your questions using natural language processing and provides relevant answers based on its training data."
      },
      {
        question: "Can I save my conversations?",
        answer: "Yes, all conversations are automatically saved to your project."
      },
      {
        question: "How do I create a new project?",
        answer: "Go to the Projects page and click on the 'New Project' button."
      },
      {
        question: "Is my data secure?",
        answer: "All data is stored locally in your browser. No data is sent to external servers except for processing queries through the LLM API."
      }
    ];
    
    return of(faqs).pipe(delay(500));
  }
}