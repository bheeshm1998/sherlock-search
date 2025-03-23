import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { Project, ProjectState } from '../../../models/project.model';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from "../../../components/header/header.component";
import { FooterComponent } from "../../../components/footer/footer.component";

@Component({
  selector: 'app-project-details',
  standalone: true,
  imports: [CommonModule, HeaderComponent, FooterComponent],
  templateUrl: './project-details.component.html',
  styleUrl: './project-details.component.scss'
})
export class ProjectDetailsComponent {

  ProjectState = ProjectState;
  
  @Input() project: Project = {
    id: "proj-12345",
    name: "Website Redesign",
    description: "A project to redesign the company website for better user experience.",
    createdAt: new Date("2023-10-01T09:00:00Z"),
    updatedAt: new Date("2023-10-15T14:30:00Z"),
    accessType: "private",
    state: ProjectState.DRAFT,
    documents: [
      {
        "id": "1",
        "name": "Project Plan",
        "description": "Detailed project plan document",
        "uploadedAt": new Date("2025-03-01T10:00:00Z"),
        "documentType": "Planning",
        "fileExtension": "pdf",
        "size": 1024,
        "file": null
      },
      {
        "id": "2",
        "name": "Budget Report",
        "description": "Quarterly budget report",
        "uploadedAt": new Date("2025-02-15T14:30:00Z"),
        "documentType": "Finance",
        "fileExtension": "xlsx",
        "size": 2048,
        "file": null
      },
      {
        "id": "3",
        "name": "Meeting Notes",
        "description": "Notes from the project kickoff meeting",
        "uploadedAt": new Date("2025-01-20T09:15:00Z"),
        "documentType": "Notes",
        "fileExtension": "docx",
        "size": 512,
        "file": null
      }
    ]
  };;

  constructor(private router: Router) {}

  editProject() {
    this.router.navigate(['/edit-project', this.project.id]);
  }

  openChat() {
    console.log("Navigating to the chat component")
    this.router.navigate(['/chat', 1]);
  }

  deleteProject() {
    if (confirm('Are you sure you want to delete this project and all its documents?')) {
      console.log('Project deleted:', this.project.id);
    }
  }
}
