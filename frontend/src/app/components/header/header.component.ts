import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {

  githubUrl = 'https://github.com/bheeshm1998/sherlock-search';

  
  openGithub() {
    window.open(this.githubUrl, '_blank');
  }

}
