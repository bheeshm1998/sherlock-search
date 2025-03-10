import { Routes } from '@angular/router';
import { ProjectListComponent } from './features/projects/project-list/project-list.component';
import { ChatComponent } from './features/chat/chat/chat.component';

export const routes: Routes = [
    { path: '', redirectTo: '/projects', pathMatch: 'full' },
    { path: 'projects', component: ProjectListComponent },
    { path: 'chat/:id', component: ChatComponent },
    { path: '**', redirectTo: '/projects' }
  ];
