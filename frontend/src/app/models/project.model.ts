import { AttachedDocument } from "./document.model";

export interface Project {
    id: string | number;
    name: string;
    description?: string;
    createdAt: Date;
    updatedAt: Date;
    accessType?: string;
    state: ProjectState; 
    documents: AttachedDocument[];
  }

export enum ProjectState {
  DRAFT = 'DRAFT',
  PUBLISHED = 'PUBLISHED',
  ARCHIVED = 'ARCHIVED',
}