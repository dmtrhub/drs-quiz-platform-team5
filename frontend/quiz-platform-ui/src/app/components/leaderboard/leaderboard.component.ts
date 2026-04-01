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
  pageSize = 10;
  currentPage = 1;
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
      // Stagger component load to prevent request burst (429 rate limiting)
      setTimeout(() => this.loadQuizzes(), 300);
      setTimeout(() => this.loadLeaderboard(), 400);

    } else if (this.quizId) {

      this.selectedQuizId = this.quizId;
      this.showQuizFilter = false;
      setTimeout(() => this.loadLeaderboard(), 300);

    } else {

      this.showQuizFilter = true;
      setTimeout(() => this.loadQuizzes(), 300);
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
        this.currentPage = 1;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load leaderboard';
        this.isLoading = false;
      }
    });
  }

  get totalPages(): number {
    const total = Math.ceil(this.leaderboard.length / this.pageSize);
    return Math.max(total, 1);
  }

  get paginatedLeaderboard(): any[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.leaderboard.slice(start, start + this.pageSize);
  }

  get showPagination(): boolean {
    return this.leaderboard.length > this.pageSize;
  }

  get pageNumbers(): number[] {
    return Array.from({ length: this.totalPages }, (_, index) => index + 1);
  }

  goToPage(page: number): void {
    const safePage = Math.max(1, Math.min(page, this.totalPages));
    this.currentPage = safePage;
  }

  nextPage(): void {
    this.goToPage(this.currentPage + 1);
  }

  previousPage(): void {
    this.goToPage(this.currentPage - 1);
  }

  getRank(indexOnPage: number): number {
    return (this.currentPage - 1) * this.pageSize + indexOnPage + 1;
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
      next: (response: any) => {
        const message = response?.message || 'PDF report has been generated';
        this.notificationService.success(message);
        if (response?.warning) {
          this.notificationService.info(response.warning);
        }
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
