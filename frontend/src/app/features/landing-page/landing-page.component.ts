import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss'
})
export class LandingPageComponent {
  userType: 'enduser' | 'admin' = 'enduser';
  
  constructor(private router: Router) {}

  setUserType(type: 'enduser' | 'admin'): void {
    this.userType = type;
  }

  handleGoogleAuth(): void {
    // In a real app, you would implement actual Google Auth here
    console.log(`Signing in as ${this.userType}`);
    
    // Navigate based on user type
    if (this.userType === 'admin') {
      this.router.navigate(['/admin-dashboard']);
    } else {
      this.router.navigate(['/user-dashboard']);
    }
  }
}
