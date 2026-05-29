import { Component, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MigrationResponse } from './models/migration.model';
import { MigrationService } from './services/migration';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {

  // These are the variables Angular watches
  // When they change → HTML updates automatically
  inputCode: string = '';
  result: MigrationResponse | null = null;
  isLoading: boolean = false;
  errorMessage: string = '';
  showScore: boolean = false;
  showCode: boolean = false;
  showReview: boolean = false;

  constructor(
    private migrationService: MigrationService,
    private cdr: ChangeDetectorRef,
    // NgZone — ensures long async responses trigger Angular update
    private ngZone: NgZone
  ) {}

  migrate() {
    if (!this.inputCode.trim()) {
      this.errorMessage = 'Please paste your code first.';
      return;
    }

    // Reset all variables before new migration
    this.isLoading = true;
    this.result = null;
    this.errorMessage = '';
    this.showScore = false;
    this.showCode = false;
    this.showReview = false;

    // cdr.detectChanges() — tell Angular to update HTML RIGHT NOW
    // so spinner appears immediately when button clicked
    this.cdr.detectChanges();

    this.migrationService.migrate(this.inputCode).subscribe({

      next: (response) => {
        // ngZone.run() — response arrived after 30-60 seconds
        // Angular might have lost track of this async call
        // ngZone.run() brings us back INTO Angular's zone
        // so Angular definitely sees these changes
        this.ngZone.run(() => {


          this.result = response;
          this.isLoading = false;

          // Progressive reveal — show sections one by one
          // Feels faster even though total time is same
          // setTimeout is a common UX trick
          setTimeout(() => {
            this.showScore = true;
            // detectChanges after each setTimeout
            // because setTimeout runs outside Angular zone
            this.cdr.detectChanges();
          }, 100);

          setTimeout(() => {
            this.showCode = true;
            this.cdr.detectChanges();
          }, 300);

          setTimeout(() => {
            this.showReview = true;
            this.cdr.detectChanges();
          }, 500);

          this.cdr.detectChanges();
        });
      },

      error: (err) => {
        // Also wrap error in ngZone.run()
        // Error can also arrive after a long time
        this.ngZone.run(() => {
          this.errorMessage = err.error?.detail || 'Migration failed.';
          this.isLoading = false;
          this.cdr.detectChanges();
        });
      }
    });
  }

  copyCode() {
    navigator.clipboard.writeText(this.result?.migrated_code || '');
    alert('Copied to clipboard!');
  }

  downloadCode() {
    const code = this.result?.migrated_code || '';
    const language = this.result?.language || 'code';
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `migrated.${this.getExtension(language)}`;
    a.click();
  }

  getExtension(language: string): string {
    const map: {[key: string]: string} = {
      'Java': 'java', 'Python': 'py',
      'JavaScript': 'js', 'C++': 'cpp', 'TypeScript': 'ts'
    };
    return map[language] || 'txt';
  }

  getScoreColor(): string {
    const score = this.result?.score || 0;
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  }
}
