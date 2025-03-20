import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { Project } from '../../../models/project.model';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-project-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './project-details.component.html',
  styleUrl: './project-details.component.scss'
})
export class ProjectDetailsComponent {
  
  @Input() project: Project = {
    id: "proj-12345",
    name: "Website Redesign",
    description: "A project to redesign the company website for better user experience.",
    createdAt: new Date("2023-10-01T09:00:00Z"),
    updatedAt: new Date("2023-10-15T14:30:00Z"),
    accessType: "private",
    documents: [
      {
        id: "doc-67890",
        name: "Design Mockups",
        description: "Initial design mockups for the homepage.",
        uploadedAt: new Date("2023-10-02T10:15:00Z"),
        documentType: "Design",
        fileExtension: ".pdf",
        size: "2.5MB",
      },
      {
        id: "doc-67891",
        name: "Project Scope",
        description: "Detailed project scope and deliverables.",
        uploadedAt: new Date("2023-10-03T11:00:00Z"),
        documentType: "Planning",
        fileExtension: ".docx",
        size: "1.2MB",
      },
      {
        id: "doc-67892",
        name: "User Research Findings",
        description: "Description for user research findings.",
        uploadedAt: new Date("2023-10-05T12:45:00Z"),
        documentType: "Research",
        fileExtension: ".pptx",
        size: "3.0MB",
      },
    ],
  };;

  constructor(private router: Router) {}

  editProject() {
    this.router.navigate(['/edit-project', this.project.id]);
  }

  deleteProject() {
    if (confirm('Are you sure you want to delete this project and all its documents?')) {
      console.log('Project deleted:', this.project.id);
    }
  }
}
