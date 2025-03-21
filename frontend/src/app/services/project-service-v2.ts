import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Project } from '../models/project.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProjectServiceV2 {
  private apiUrl = `${environment.apiBaseUrl}`;
  private http = inject(HttpClient);

  getProjects(): Observable<Project[]> {
    return this.http.get<Project[]>(this.apiUrl);
  }

  createProject(projectData: any, files: File[]): Observable<any> {
    const formData = new FormData();
    
    // Append project data as JSON string
    formData.append('project_data', JSON.stringify(projectData));
    
    // Append files
    files.forEach(file => {
      formData.append('files', file, file.name);
    });

    // Make the HTTP POST request
    return this.http.post<any>(`${this.apiUrl}/projectsv2`, formData);
  }

  updateProject(id: string, updates: Partial<Project>): Observable<Project> {
    return this.http.put<Project>(`${this.apiUrl}/${id}`, updates);
  }

  deleteProject(id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/${id}`);
  }

  getProjectById(id: string): Observable<Project> {
    return this.http.get<Project>(`${this.apiUrl}/${id}`);
  }
}
