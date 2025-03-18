import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

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
  imports: [CommonModule, FormsModule],
  templateUrl: './create-project.component.html',
  styleUrls: ['./create-project.component.scss']
})
export class CreateProjectComponent {
  project = {
    name: '',
    description: '',
    documentType: '',
    accessType: 'private'
  };

  documents: Document[] = [];
  maxDocumentsPerUpload = 5;
  maxTotalDocuments = 20;
  documentTypes = ['PDF', 'DOCX', 'XLS', 'PPT', 'TXT', 'CSV', 'ZIP', 'Other'];
  accessTypes = ['Private', 'Restricted', 'Public'];

  constructor(private router: Router) {}

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
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  createProject(): void {
    // Here you would implement the actual project creation logic
    // For example, sending the form data and files to your backend API
    console.log('Creating project:', this.project);
    console.log('With documents:', this.documents);
    
    // Navigate back to dashboard after successful creation
    this.router.navigate(['/admin']);
  }

  cancel(): void {
    this.router.navigate(['/admin']);
  }
}
