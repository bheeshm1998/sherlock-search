import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HeaderComponent } from '../../components/header/header.component';
import { FooterComponent } from "../../components/footer/footer.component";

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [CommonModule, HeaderComponent, FooterComponent],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss'
})
export class LandingPageComponent {
  userType: 'enduser' | 'admin' = 'admin';
  githubUrl = 'https://github.com/bheeshm1998/sherlock-search';
  
  constructor(private router: Router) {}

  setUserType(type: 'enduser' | 'admin'): void {
    this.userType = type;
  }

  openGithub() {
    window.open(this.githubUrl, '_blank');
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
