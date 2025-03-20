import { AttachedDocument } from "./document.model";

export interface Project {
    id: string;
    name: string;
    description?: string;
    createdAt: Date;
    updatedAt: Date;
    accessType?: string;
    documents: AttachedDocument[];
  }