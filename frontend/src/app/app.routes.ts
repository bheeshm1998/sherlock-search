import { Routes } from '@angular/router';
import { ProjectListComponent } from './features/projects/project-list/project-list.component';
import { ChatComponent } from './features/chat/chat/chat.component';
import { LandingPageComponent } from './features/landing-page/landing-page.component';
import { UserDashboardComponent } from './features/dashboard/user-dashboard/user-dashboard.component';
import { AdminDashboardComponent } from './features/dashboard/admin-dashboard/admin-dashboard.component';
import { CreateProjectComponent } from './features/projects/create-project/create-project.component';

export const routes: Routes = [
    { path: '', redirectTo: '/home', pathMatch: 'full' },
    { path: "home", component: LandingPageComponent},
    { path: "admin-dashboard", component: AdminDashboardComponent},
    { path: "user-dashboard", component: UserDashboardComponent},
    { path: "project", component: CreateProjectComponent},
    { path: 'chat/:id', component: ChatComponent },
    { path: '**', redirectTo: '/home' }
  ];
