import { Injectable, signal } from '@angular/core';
import { Project } from '../models/project.model';
import { v4 as uuidv4 } from 'uuid';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private storageKey = 'llm-app-projects';
  private projectsSignal = signal<Project[]>([]);
  
  projects = this.projectsSignal.asReadonly();
  
  constructor() {
    this.loadProjects();
  }
  
  private loadProjects(): void {
    const stored = localStorage.getItem(this.storageKey);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Convert string dates back to Date objects
      const projects = parsed.map((p: any) => ({
        ...p,
        createdAt: new Date(p.createdAt),
        updatedAt: new Date(p.updatedAt)
      }));
      this.projectsSignal.set(projects);
    }
  }
  
  private saveProjects(): void {
    localStorage.setItem(this.storageKey, JSON.stringify(this.projectsSignal()));
  }
  
  createProject(name: string, description?: string): Project {
    const now = new Date();
    const newProject: Project = {
      id: uuidv4(),
      name,
      description,
      createdAt: now,
      updatedAt: now
    };
    
    this.projectsSignal.update(projects => [...projects, newProject]);
    this.saveProjects();
    return newProject;
  }
  
  updateProject(id: string, updates: Partial<Project>): Project | null {
    let updatedProject: Project | null = null;
    
    this.projectsSignal.update(projects => 
      projects.map(project => {
        if (project.id === id) {
          updatedProject = {
            ...project,
            ...updates,
            updatedAt: new Date()
          };
          return updatedProject;
        }
        return project;
      })
    );
    
    this.saveProjects();
    return updatedProject;
  }
  
  deleteProject(id: string): void {
    this.projectsSignal.update(projects => 
      projects.filter(project => project.id !== id)
    );
    this.saveProjects();
  }
  
  getProject(id: string): Project | undefined {
    return this.projectsSignal().find(project => project.id === id);
  }
}