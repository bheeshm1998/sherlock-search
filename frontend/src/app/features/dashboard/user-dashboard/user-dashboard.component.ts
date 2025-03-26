import { Component } from '@angular/core';
import { HeaderComponent } from "../../../components/header/header.component";
import { FooterComponent } from "../../../components/footer/footer.component";
import { ProjectState } from '../../../models/project.model';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule, DatePipe } from '@angular/common';
import { ProjectServiceV2 } from '../../../services/project-service-v2';
import { Subscription } from 'rxjs';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, DatePipe, CommonModule],
  templateUrl: './user-dashboard.component.html',
  styleUrl: './user-dashboard.component.scss'
})
export class UserDashboardComponent {

    ProjectState: any = ProjectState;
    projects: any[] = [];
    currentUserId: string | any = ""

    // private subscriptions: Subscription[] = [];
    projectId: any;
    loading: boolean = true;

    constructor(private router: Router, private route: ActivatedRoute,
         private projectService: ProjectServiceV2, private authService: AuthService) { }

  handleLogout(): void {
    console.log("Clicked on logout button")
  }

  openProject(id: number | string): void {
    // Navigate to project details page
    this.router.navigate(['/project-details', id]);
  }

  openChat() {
    this.router.navigate(['/chat', this.projectId]);
  }

  ngOnInit(): void {
    this.currentUserId = this.authService.getCurrentUser();
    this.getAllProjectsForTheUser(this.currentUserId);
  }

  loadProject() {
    throw new Error('Method not implemented.');
  }

  getAllProjectsForTheUser(userId: string): void {
    this.projectService.getAllProjectsForAUser(userId)
      .subscribe({
        next: (data) => {
          this.projects = data;
          this.loading = false
        },
        error: (err) => {
          this.loading = false;
          console.error('Error fetching projects:', err);
        }
      });
  }

}
