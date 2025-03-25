import { Component } from '@angular/core';
import { SnackbarService } from '../../services/snackbar.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-snackbar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './snackbar.component.html',
  styleUrl: './snackbar.component.scss'
})
export class SnackbarComponent {

  snackbar$ = this.snackbarService.snackbarState$;
  constructor(private snackbarService: SnackbarService) {}

}
