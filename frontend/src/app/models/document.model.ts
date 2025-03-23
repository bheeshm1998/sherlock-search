export interface AttachedDocument {
    id?: string;
    name: string;
    description?: string;
    uploadedAt: Date;
    documentType: string;
    fileExtension?: string;
    size: number;
    file: File ;
  }