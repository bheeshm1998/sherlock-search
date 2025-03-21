import { NgFor, NgIf, DatePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HeaderComponent } from '../../../components/header/header.component';
import { ProjectService } from '../../../services/project.services';
import { Router } from '@angular/router';
import { Project } from '../../../models/project.model';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports:  [HeaderComponent, NgFor, NgIf, DatePipe, FormsModule, HttpClientModule],
  templateUrl: './project-list.component.html',
  styleUrl: './project-list.component.scss'
})
export class ProjectListComponent implements OnInit {
  projects = this.projectService.projects;
  showNewProjectForm = false;
  newProjectName = '';
  newProjectDescription = '';
  content: string = "not active";
  
  constructor(private projectService: ProjectService, private router: Router,  private http: HttpClient) {}
  
  ngOnInit(): void {
    this.http.get('http://localhost:7888/debug')
      .subscribe((data: any) => {
        console.log(data);
        this.content = data.status
        // Handle the data from the API
      }, (error) => {
        console.error('Error fetching projects', error);
      });

  }
  
  createProject(): void {
    if (this.newProjectName.trim()) {
      const project = this.projectService.createProject(
        this.newProjectName.trim(),
        this.newProjectDescription.trim() || undefined
      );
      this.newProjectName = '';
      this.newProjectDescription = '';
      this.showNewProjectForm = false;
      
      // Navigate to the new project
      this.router.navigate(['/chat', project.id]);
    }
  }
  
  openProject(project: Project): void {
    this.router.navigate(['/chat', project.id]);
  }
}

