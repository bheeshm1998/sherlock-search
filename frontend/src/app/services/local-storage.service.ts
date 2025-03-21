import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class LocalStorageService {
  
  constructor() {}
  
  getItem(key: string): string | null {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      console.error('Error reading from localStorage', e);
      return null;
    }
  }
  
  setItem(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      console.error('Error writing to localStorage', e);
    }
  }
  
  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (e) {
      console.error('Error removing from localStorage', e);
    }
  }
  
  clear(): void {
    try {
      localStorage.clear();
    } catch (e) {
      console.error('Error clearing localStorage', e);
    }
  }
}