import { Component } from '@angular/core';
import { HeaderComponent } from "../../../components/header/header.component";
import { FooterComponent } from "../../../components/footer/footer.component";
import { ProjectState } from '../../../models/project.model';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule, DatePipe } from '@angular/common';
import { ProjectServiceV2 } from '../../../services/project-service-v2';
import { Subscription } from 'rxjs';

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
    currentUserId: string = ""

    private subscriptions: Subscription[] = [];
    projectId: any;
    loading: boolean = true;

    constructor(private router: Router, private route: ActivatedRoute,
         private projectService: ProjectServiceV2) { }

  handleLogout(): void {
    console.log("Clicked on logout button")
  }

  openProject(id: number | string): void {
    // Navigate to project details page
    this.router.navigate(['/project-details', id]);
  }

  openChat() {
    this.router.navigate(['/chat', this.currentUserId]);
  }

  ngOnInit(): void {
    this.subscriptions.push(
      this.route.paramMap.subscribe(params => {
        const id = params.get('id');
        if (id) {
          this.currentUserId = id;
          this.getAllProjectsForTheUser(this.currentUserId);
        } else {
          this.router.navigate(['/projects']);
        }
      })
    );
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
