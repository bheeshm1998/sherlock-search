import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { catchError, map, Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatService {

  private apiUrl = environment.apiBaseUrl;
  
  constructor(private http: HttpClient) {}
  
  generateResponse(message: string, project_id: any, user_id: any): Observable<string> {
    return this.http.post<{ response: string }>(
      `${this.apiUrl}/chat/${project_id}/${user_id}`,
      {
        content: message,  // Changed from 'query' to 'content' to match Python model
        project_id: project_id,
        user_id: user_id
      }
    ).pipe(
      map(response => response.response),
      catchError(error => {
        console.error('API error:', error);
        return throwError(() => new Error('Failed to get response from the chat API'));
      })
    );
}
  
  getFAQs(): Observable<{question: string, answer: string}[]> {
    // This could be replaced with an actual API call if you have a FAQ endpoint
    return this.http.get<{question: string, answer: string}[]>(`${this.apiUrl}/faqs`).pipe(
      catchError((): Observable<{ question: string; answer: string }[]> => {
        // Return some default FAQs if the API call fails
        return new Observable(observer => {
          observer.next([
            {
              question: 'What can this assistant help with?',
              answer: 'I can answer questions about your projects and help with various tasks.'
            },
            {
              question: 'How do I create a new project?',
              answer: 'Go to the Projects page and click on "New Project" button.'
            },
            {
              question: 'Can I export my chat history?',
              answer: 'Yes, you can export your conversation from the options menu.'
            },
            {
              question: 'How do I share this conversation?',
              answer: 'Use the share button in the top-right corner of the chat.'
            }
          ]);
          observer.complete();
        });
      })
    );
  }
}
