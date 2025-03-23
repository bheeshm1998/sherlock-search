import { Component } from '@angular/core';
import { HeaderComponent } from "../../../components/header/header.component";
import { FooterComponent } from "../../../components/footer/footer.component";
import { ProjectState } from '../../../models/project.model';
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, DatePipe],
  templateUrl: './user-dashboard.component.html',
  styleUrl: './user-dashboard.component.scss'
})
export class UserDashboardComponent {

    ProjectState: any = ProjectState;
    projects: any[] = [];

    constructor(private router: Router) { }

  handleLogout(): void {
    console.log("Clicked on logout button")
  }

  openProject(id: number | string): void {
    // Navigate to project details page
    this.router.navigate(['/project-details', id]);
  }

  openChat() {
    this.router.navigate(['/chat']);
  }

}
