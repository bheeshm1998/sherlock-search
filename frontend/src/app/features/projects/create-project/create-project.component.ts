import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
import { ProjectServiceV2 } from '../../../services/project-service-v2';

interface Document {
  id: number;
  name: string;
  type: string;
  description: string;
  size: number;
  file: File;
}

@Component({
  selector: 'app-create-project',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './create-project.component.html',
  styleUrls: ['./create-project.component.scss']
})
export class CreateProjectComponent {

  isSubmitting: boolean = false;
  projectForm!: FormGroup;

  documents: Document[] = [];
  pageTitle = 'Create Project';
  maxDocumentsPerUpload = 5;
  maxTotalDocuments = 20;
  documentTypes = ['PDF', 'DOCX', 'XLS', 'PPT', 'TXT', 'CSV', 'ZIP', 'Other'];
  accessTypes = ['Private', 'Restricted', 'Public'];

  constructor(private fb: FormBuilder, private router: Router, private route: ActivatedRoute, private projectService: ProjectServiceV2) { }

  ngOnInit() {
    this.initForm();

    this.route.paramMap.subscribe(params => {
      this.pageTitle = params.has('id') ? 'Edit Project' : 'Create New Project';
    });
  }

  initForm(): void {
    this.projectForm = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      accessType: ['private'],
    });
  }

  getFileExtension(filename: string): string {
    return filename.split('.').pop()?.toUpperCase() || 'Unknown';
  }

  getIconForFileType(fileType: string): string {
    const lowerType = fileType.toLowerCase();
    if (lowerType.includes('pdf')) return 'pdf';
    if (lowerType.includes('doc')) return 'word';
    if (lowerType.includes('xls')) return 'excel';
    if (lowerType.includes('ppt')) return 'powerpoint';
    if (lowerType.includes('txt')) return 'text';
    if (lowerType.includes('csv')) return 'csv';
    if (lowerType.includes('zip')) return 'archive';
    if (lowerType.includes('jpg') || lowerType.includes('png') || lowerType.includes('gif')) return 'image';
    return 'generic';
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;

    const files = Array.from(input.files);

    if (files.length > this.maxDocumentsPerUpload) {
      alert(`You can only upload ${this.maxDocumentsPerUpload} documents at a time.`);
      return;
    }

    if (this.documents.length + files.length > this.maxTotalDocuments) {
      alert(`You can only upload ${this.maxTotalDocuments} documents per project.`);
      return;
    }

    files.forEach(file => {
      const fileType = this.getFileExtension(file.name);
      const newDoc: Document = {
        id: Date.now() + Math.floor(Math.random() * 1000),
        name: file.name,
        type: fileType,
        description: file.name, // Default description is the file name
        size: file.size,
        file: file
      };
      this.documents.push(newDoc);
    });

    // Reset file input
    input.value = '';
  }

  removeDocument(index: number): void {
    this.documents.splice(index, 1);
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  createProject(): void {
    if (this.projectForm.valid) {

      // Prepare project data
      const projectData = {
        name: this.projectForm.get('name')?.value,
        description: this.projectForm.get('description')?.value,
        access_type: this.projectForm.get('accessType')?.value,
        state: 'DRAFT'
      };

      // Prepare files
      const files = this.documents.map(doc => doc.file);

      // Set isSubmitting flag
      this.isSubmitting = true;

      // Use the service to create the project
      this.projectService.createProject(projectData, files).subscribe({
        next: (response: any) => {
          console.log('Project created successfully:', response);
          this.router.navigate(['/admin-dashboard']);
        },
        error: (error: any) => {
          console.error('Error creating project:', error);
          this.isSubmitting = false;
        },
        complete: () => {
          this.isSubmitting = false;
        }
      });
    } else {
      return;
    }
  }

  cancel(): void {
    this.router.navigate(['/admin-dashboard']);
  }
}
