// admin-dashboard.component.ts
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

interface Project {
  id: number;
  name: string;
  description: string;
  documentType: string;
  accessType: string;
  documentsCount: number;
  createdAt: Date;
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent {
  projects: Project[] = [
    {
      id: 1,
      name: 'Financial Reports 2023',
      description: 'Annual financial reporting documents',
      documentType: 'PDF',
      accessType: 'Restricted',
      documentsCount: 12,
      createdAt: new Date('2023-12-15')
    },
    {
      id: 2,
      name: 'Marketing Materials',
      description: 'Brochures and promotional content',
      documentType: 'Various',
      accessType: 'Public',
      documentsCount: 8,
      createdAt: new Date('2024-01-20')
    },
    {
      id: 3,
      name: 'Legal Contracts',
      description: 'Client agreements and legal documents',
      documentType: 'DOCX',
      accessType: 'Private',
      documentsCount: 15,
      createdAt: new Date('2024-02-10')
    }
  ];

  constructor(private router: Router) {}

  navigateToCreateProject(): void {
    this.router.navigate(['/create-project']);
  }

  openProject(id: number): void {
    // Navigate to project details page
    this.router.navigate(['/project-details', id]);
  }
}
