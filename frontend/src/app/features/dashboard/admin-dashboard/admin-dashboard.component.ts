// admin-dashboard.component.ts
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ProjectState } from '../../../models/project.model';
import { ProjectServiceV2 } from '../../../services/project-service-v2';


@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent {

  ProjectState: any = ProjectState;
  projects: any[] = [];
  constructor(private router: Router, private projectService: ProjectServiceV2) { }

  ngOnInit(): void {
    this.getAllProjects();
  }

  getAllProjects(): void {
    this.projectService.getAllProjects()
      .subscribe({
        next: (data) => {
          this.projects = data;
        },
        error: (err) => {
          console.error('Error fetching projects:', err);
        }
      });
  }

  navigateToCreateProject(): void {
    this.router.navigate(['/create-project']);
  }

  openProject(id: number | string): void {
    // Navigate to project details page
    this.router.navigate(['/project-details', id]);
  }

  publishProject(projectId: string | number) {
    this.projectService.publishProject(projectId)
    .subscribe({
      next: () => {
        this.projects = this.projects.map(project =>
          project.id === projectId ? { ...project, state: 'PUBLISHED' } : project
        );
      },
      error: (err) => {
        console.error('Error publishing project:', err);
      }
    });
  }

}
