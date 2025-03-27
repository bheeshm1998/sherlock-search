import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Project } from '../models/project.model';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ProjectServiceV2 {
  private apiUrl = `${environment.apiBaseUrl}`;
  private http = inject(HttpClient);

  constructor(private authService: AuthService) { }

  getAllProjects(): Observable<Project[]> {
    return this.http.get<Project[]>(`${this.apiUrl}/projects`);
  }

  createProject(projectData: any, files: File[] | null, selectedGroups: any): Observable<any> {
    const formData = new FormData();
    
    // Append project data as JSON string
    formData.append('project_data', JSON.stringify(projectData));
    formData.append("groups", JSON.stringify(selectedGroups))
    
    // Append files
    if(files) {
      files.forEach(file => {
        formData.append('files', file, file.name);
      });
    }

    // Make the HTTP POST request
    return this.http.post<any>(`${this.apiUrl}/projectsv2`, formData);
  }

  updateProject(id: string, projectData: any, files: File[] | null): Observable<Project> {
    const formData = new FormData();
    
    // Append project data as JSON string
    formData.append('project_data', JSON.stringify(projectData));
    
    // Append files
    if(files) {
      files.forEach(file => {
        formData.append('files', file, file.name);
      });
    }
    
    return this.http.put<any>(`${this.apiUrl}/projects/${id}`, formData);
  }

  deleteProject(id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/projects/${id}`);
  }

  getProjectById(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/projects/${id}`);
  }

  publishProject(id: string | number): Observable<Project> {

    return this.http.put<Project>(`${this.apiUrl}/projects/${id}/publish`, {});
  }

  getAllProjectsForAUser(userId: string): Observable<Project[]> {

    const headers = new HttpHeaders({
            'Authorization': 'Bearer ' + this.authService.getToken()
          });
    return this.http.get<Project[]>(`${this.apiUrl}/projects/user/${userId}`, { headers });
  }
}
