import { Routes } from '@angular/router';
import { ChatComponent } from './features/chat/chat/chat.component';
import { LandingPageComponent } from './features/landing-page/landing-page.component';
import { UserDashboardComponent } from './features/dashboard/user-dashboard/user-dashboard.component';
import { AdminDashboardComponent } from './features/dashboard/admin-dashboard/admin-dashboard.component';
import { CreateProjectComponent } from './features/projects/create-project/create-project.component';
import { ProjectDetailsComponent } from './features/projects/project-details/project-details.component';

export const routes: Routes = [
    { path: '', redirectTo: '/home', pathMatch: 'full' },
    { path: "home", component: LandingPageComponent},
    { path: "admin-dashboard", component: AdminDashboardComponent},
    { path: "user-dashboard", component: UserDashboardComponent},
    { path: "create-project", component: CreateProjectComponent},
    { path: "edit-project/:id", component: CreateProjectComponent},
    { path: "project-details/:projectId", component: ProjectDetailsComponent},
    { path: "chat/:projectId", component: ChatComponent },
    { path: '**', redirectTo: '/home' }
  ];
