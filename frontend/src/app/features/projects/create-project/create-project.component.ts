import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
import { ProjectServiceV2 } from '../../../services/project-service-v2';
import { AttachedDocument } from '../../../models/document.model';
import { HeaderComponent } from "../../../components/header/header.component";
import { FooterComponent } from "../../../components/footer/footer.component";
import { SnackbarService } from '../../../services/snackbar.service';

@Component({
  selector: 'app-create-project',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, HeaderComponent, FooterComponent],
  templateUrl: './create-project.component.html',
  styleUrls: ['./create-project.component.scss']
})
export class CreateProjectComponent {

  isSubmitting: boolean = false;
  projectForm!: FormGroup;

  documents: AttachedDocument[] = [];
  pageTitle = 'Create Project';
  maxDocumentsPerUpload = 5;
  maxTotalDocuments = 20;
  documentTypes = ['PDF', 'DOCX', 'XLS', 'PPT', 'TXT', 'CSV', 'ZIP', 'Other'];
  accessTypes = ['Private', 'Restricted', 'Public'];
  submitBtnText = 'Create Project';

  projectId: string | null = null;

  constructor(
    private fb: FormBuilder, 
    private router: Router, 
    private route: ActivatedRoute, 
    private snackbarService: SnackbarService,
    private projectService: ProjectServiceV2) { }

  ngOnInit() {
    this.initForm();

    this.route.paramMap.subscribe(params => {
      this.projectId = params.get('id');
      if (this.projectId) {
        this.pageTitle = 'Edit Project';
        this.submitBtnText = 'Save Changes';
        this.loadProjectData(this.projectId);
      }
    });
  }

  initForm(): void {
    this.projectForm = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      accessType: ['private'],
    });
  }

  loadProjectData(id: string): void {
    this.projectService.getProjectById(id).subscribe(project => {
      this.projectForm.patchValue({
        name: project.name,
        description: project.description,
        accessType: project.accessType,
      });
      this.documents = project.documents || [];
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
      const newDoc: AttachedDocument = {
        name: file.name,
        documentType: fileType,
        uploadedAt: new Date(),
        description: file.name, // Default description is the file name
        size: file.size,
        file: file,
        fileExtension: fileType
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

  createOrUpdateProject(): void {
    if (this.projectForm.valid) {
      const projectData = {
        name: this.projectForm.get('name')?.value,
        description: this.projectForm.get('description')?.value,
        access_type: this.projectForm.get('accessType')?.value,
        state: 'DRAFT'
      };

      const files = this.documents.map(doc => doc.file).filter(Boolean);
      this.isSubmitting = true;

      if (this.projectId) {
        this.projectService.updateProject(this.projectId, projectData, files).subscribe({
          next: response => {
            console.log('Project updated successfully:', response);
            this.router.navigate(['/admin-dashboard']);
          },
          error: error => {
            console.error('Error updating project:', error);
            this.isSubmitting = false;
          },
          complete: () => (this.isSubmitting = false)
        });
      } else {
        this.projectService.createProject(projectData, files).subscribe({
          next: response => {
            console.log('Project created successfully:', response);
            this.snackbarService.showSnackbar('Failed to create project.', 'error')
            this.snackbarService.showSnackbar('Project created Successfully.', 'success')
            this.router.navigate(['/admin-dashboard']);
          },
          error: error => {
            console.error('Error creating project:', error);
            this.snackbarService.showSnackbar('Failed to create project.', 'error');
            this.isSubmitting = false;
          },
          complete: () => (this.isSubmitting = false)
        });
      }
    }
  }

  cancel(): void {
    this.router.navigate(['/admin-dashboard']);
  }
}
