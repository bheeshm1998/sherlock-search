import { Component, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Project, ProjectState } from '../../../models/project.model';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from "../../../components/header/header.component";
import { FooterComponent } from "../../../components/footer/footer.component";
import { ProjectServiceV2 } from '../../../services/project-service-v2';

import { AuthService } from '../../../services/auth.service';


@Component({
  selector: 'app-project-details',
  standalone: true,
  imports: [CommonModule, HeaderComponent, FooterComponent],
  templateUrl: './project-details.component.html',
  styleUrl: './project-details.component.scss'
})
export class ProjectDetailsComponent {

  ProjectState = ProjectState;

  constructor(private router: Router, private projectService: ProjectServiceV2,  private route: ActivatedRoute, private authService: AuthService ) {}


  ngOnInit() {
    this.route.params.subscribe(params => {
      this.projectId = params['projectId'];  // Get projectId from route parameters
      this.fetchProjectDetails();
    });

    this.loggedInUserType = this.authService.getCurrentUserType();

  }

  fetchProjectDetails() {
    this.projectService.getProjectById(this.projectId).subscribe({
      next: response => {

        this.project = response.project;
        this.groups = response.groups.map((group: any) => group.name);

        console.log('Project details fetched successfully:', response);
        this.router.navigate(['/project-details', this.projectId]);
      },
      error: error => {
        console.error('Error getting the details of the project', error);
      },
      complete: () => {
        console.log("Project details fetch completed");
      }
    });
  }

  editProject() {
    this.router.navigate(['/edit-project', this.project.id]);
  }

  gotoDashBoard() {
    this.router.navigate(['/admin-dashboard']);
  }

  openChat() {
    console.log("Navigating to the chat component")
    this.router.navigate(['/chat', this.projectId]);
  }

  deleteProject() {
    if (confirm('Are you sure you want to delete this project and all its documents?')) {
      this.projectService.deleteProject(this.project.id).subscribe({
        next: response => {
          console.log('Project deleted successfully:', response);
          this.router.navigate(['/admin-dashboard']);
        },
        error: error => {
          console.error('Error deleting the project', error);
        },
        complete: () => {
          console.log("Project delete completed");
        }
      });
    }
  }
}
