
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SnackbarService {

  constructor() { }
  private snackbarState = new BehaviorSubject<{ message: string; type: 'success' | 'error' } | null>(null);
  snackbarState$ = this.snackbarState.asObservable();

  showSnackbar(message: string, type: 'success' | 'error') {
    this.snackbarState.next({ message, type });
    setTimeout(() => this.snackbarState.next(null), 3000);
  }
}

