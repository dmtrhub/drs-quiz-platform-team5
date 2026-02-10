import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { QuizService } from '../../services/quiz.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-leaderboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './leaderboard.component.html',
  styleUrl: './leaderboard.component.css'
})
export class LeaderboardComponent implements OnInit {
  leaderboard: any[] = [];
  quizzes: any[] = [];
  quizId: string = '';
  selectedQuizId: string = '';
  isLoading = true;
  isLoadingQuizzes = true;
  errorMessage = '';
  showQuizFilter = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private quizService: QuizService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.quizId = this.route.snapshot.paramMap.get('id') || '';

    
    const navigation = this.router.getCurrentNavigation();
    const state = navigation?.extras?.state || window.history.state;

    if (state?.preselectedQuizId) {  
    
      this.selectedQuizId = state.preselectedQuizId;
      this.showQuizFilter = true;
      this.loadQuizzes();
      setTimeout(() => this.loadLeaderboard(), 100);

    } else if (this.quizId) {

      this.selectedQuizId = this.quizId;
      this.showQuizFilter = false;
      this.loadLeaderboard();

    } else {

      this.showQuizFilter = true;
      this.loadQuizzes();
    }
  }

  loadQuizzes(): void {
    this.isLoadingQuizzes = true;
    this.quizService.getQuizzes('APPROVED').subscribe({
      next: (quizzes) => {
        
        this.quizzes = quizzes || [];
        this.isLoadingQuizzes = false;
        this.isLoading = false;

      },
      error: (error) => {
        this.errorMessage = 'Failed to load quizzes';
        this.isLoadingQuizzes = false;
        this.isLoading = false;
      }
    });
  }

  onQuizSelect(): void {
    if (this.selectedQuizId) {
      this.loadLeaderboard();
    }
  }

  loadLeaderboard(): void {
    if (!this.selectedQuizId) {
      this.isLoading = false;
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    const quizIdToLoad = this.quizId || this.selectedQuizId;

    this.quizService.getLeaderboard(quizIdToLoad).subscribe({
      next: (response) => {
        this.leaderboard = response.leaderboard || [];
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load leaderboard';
        this.isLoading = false;
      }
    });
  }

  isAdmin(): boolean {
    const user = localStorage.getItem('user');
    if (!user) return false;
    try {
      const userData = JSON.parse(user);
      return userData.role === 'ADMIN';
    } catch {
      return false;
    }
  }

  createPdfReport(): void {
    const quizIdToReport = this.quizId || this.selectedQuizId;
    if (!quizIdToReport) return;

    this.notificationService.info('Generating PDF report...');

    this.quizService.createPdfReport(quizIdToReport).subscribe({
      next: (response) => {
        this.notificationService.success('PDF report has been sent to your email');
      },
      error: (error) => {
        this.notificationService.error(error.error?.error || 'Failed to create PDF report');
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/quizzes']);
  }
}
