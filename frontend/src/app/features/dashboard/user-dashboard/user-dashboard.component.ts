import { Component } from '@angular/core';
import { HeaderComponent } from "../../../components/header/header.component";
import { FooterComponent } from "../../../components/footer/footer.component";

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [HeaderComponent, FooterComponent],
  templateUrl: './user-dashboard.component.html',
  styleUrl: './user-dashboard.component.scss'
})
export class UserDashboardComponent {


  handleLogout(): void {
    console.log("Clicked on logout button")
  }

}
