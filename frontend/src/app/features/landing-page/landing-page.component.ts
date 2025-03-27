import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HeaderComponent } from '../../components/header/header.component';
import { FooterComponent } from "../../components/footer/footer.component";
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { SnackbarService } from '../../services/snackbar.service';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [CommonModule, HeaderComponent, FooterComponent, ReactiveFormsModule],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss'
})
export class LandingPageComponent {
  userType: 'enduser' | 'admin' = 'admin';
  githubUrl = 'https://github.com/bheeshm1998/sherlock-search';

  loginForm: FormGroup;
  
  constructor(private router: Router, private fb: FormBuilder, private authService: AuthService, private snackbarService: SnackbarService) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

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
      this.router.navigate(['/user-dashboard', "1"]);
    }
  }

  onSubmit() {
    // if(this.userType == 'admin') {
    //   // if(this.loginForm.value.email == "admin@payoda.com")
    //   this.router.navigate(['/admin-dashboard']);
    //   return
    // }
    if (this.loginForm.valid) {
      const email = this.loginForm.value.email;
  
      // Simulated login API request
      this.authService.loginUser(email, this.userType).subscribe({
        next: (response) => {
          // Assuming the token is in response.token - adjust according to your API response structure
          this.snackbarService.showSnackbar("Login success", "success")
          this.authService.setCurrentUserType(this.userType);
          if(this.userType == "admin") {
            this.router.navigate(['/admin-dashboard']);
          } else {
            this.router.navigate(['/user-dashboard']);
          }
        },
        error: (err) => {
          console.error('Login failed:', err);
          this.snackbarService.showSnackbar(err.error.detail, "error")
        }
      });
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('authToken');
  }

  logout() {
    localStorage.removeItem('authToken');
    this.router.navigate(['/']); // Redirect to home
  }
}
