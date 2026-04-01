import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { QuizService } from '../../services/quiz.service';
import { AuthService } from '../../services/auth.service';
import { WebSocketService } from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-my-quizzes',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './my-quizzes.component.html',
  styleUrl: './my-quizzes.component.css'
})
export class MyQuizzesComponent implements OnInit, OnDestroy {
  quizzes: any[] = [];
  pageSize = 9;
  currentPage = 1;
  isLoading = true;
  errorMessage = '';
  successMessage = '';
  private wsSubscriptions: Subscription[] = [];

  constructor(
    private quizService: QuizService,
    private authService: AuthService,
    private router: Router,
    private wsService: WebSocketService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    // Stagger component load to prevent request burst (429 rate limiting)
    setTimeout(() => {
      this.loadMyQuizzes();
    }, 300);
    this.subscribeToWebSocket();
  }

  ngOnDestroy(): void {
    this.wsSubscriptions.forEach(sub => sub.unsubscribe());
  }

  subscribeToWebSocket(): void {
    // Subscribe to quiz approval notifications
    this.wsSubscriptions.push(
      this.wsService.quizApproved$.subscribe({
        next: () => {
          this.loadMyQuizzes();
        }
      })
    );

    // Subscribe to quiz rejection notifications
    this.wsSubscriptions.push(
      this.wsService.quizRejected$.subscribe({
        next: () => {
          this.loadMyQuizzes();
        }
      })
    );

    // Subscribe to quiz deleted notifications
    this.wsSubscriptions.push(
      this.wsService.quizDeleted$.subscribe({
        next: () => {
          this.loadMyQuizzes();
        }
      })
    );
  }

  loadMyQuizzes(): void {
    this.isLoading = true;

    this.quizService.getMyQuizzes().subscribe({
      next: (data) => {
        this.quizzes = data;
        this.currentPage = 1;
        this.isLoading = false;
      },
      error: (error) => {
        if (error?.status === 401) {
          this.authService.logout();
          this.router.navigate(['/login'], { queryParams: { sessionExpired: 'true' } });
          return;
        }
        this.errorMessage = error.error?.error || error.error?.message || 'Failed to load quizzes';
        this.isLoading = false;
      }
    });
  }

  viewQuiz(quizId: any): void {
    const id = quizId?.$oid || quizId;
    this.router.navigate(['/quiz', id]);
  }

  isQuizOpenable(quiz: any): boolean {
    return quiz?.status === 'APPROVED';
  }

  onQuizCardClick(quiz: any): void {
    if (!this.isQuizOpenable(quiz)) {
      return;
    }
    this.viewQuiz(quiz?._id);
  }

  editQuiz(quizId: any, event?: Event): void {
    event?.stopPropagation();
    const id = quizId?.$oid || quizId;
    this.router.navigate(['/quiz/edit', id]);
  }

  async deleteQuiz(quizId: any, event?: Event): Promise<void> {
    event?.stopPropagation();
    const id = quizId?.$oid || quizId;

    if (!id) {
      this.notificationService.error('Invalid quiz ID');
      return;
    }

    const confirmed = await this.notificationService.confirm({
      title: 'Delete Quiz',
      message: 'Are you sure you want to permanently delete this quiz?',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      variant: 'danger'
    });

    if (!confirmed) {
      return;
    }

    this.quizService.deleteQuiz(id).subscribe({
      next: () => {
        this.quizzes = this.quizzes.filter((quiz) => {
          const currentId = quiz?._id?.$oid || quiz?._id;
          return currentId !== id;
        });
        if (this.currentPage > this.totalPages) {
          this.currentPage = this.totalPages;
        }
        this.successMessage = 'Quiz deleted successfully';
        this.notificationService.success('Quiz deleted successfully');
        setTimeout(() => this.successMessage = '', 2500);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || error.error?.message || 'Failed to delete quiz';
        this.notificationService.error(this.errorMessage);
      }
    });
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'APPROVED': return 'status-approved';
      case 'PENDING': return 'status-pending';
      case 'REJECTED': return 'status-rejected';
      default: return '';
    }
  }

  getStatusText(status: string): string {
    switch (status) {
      case 'APPROVED': return 'Approved';
      case 'PENDING': return 'Pending Review';
      case 'REJECTED': return 'Rejected';
      default: return status;
    }
  }

  getCreatedDate(createdAt: any): Date {
    if (!createdAt) return new Date();
    // Handle MongoDB date format {$date: timestamp}
    if (createdAt.$date) {
      return new Date(createdAt.$date);
    }
    // Handle ISO string or timestamp
    return new Date(createdAt);
  }

  formatDuration(secondsValue: any): string {
    const totalSeconds = Number(secondsValue || 0);
    if (!Number.isFinite(totalSeconds) || totalSeconds <= 0) {
      return '0 sec';
    }

    if (totalSeconds < 60) {
      return `${totalSeconds} sec`;
    }

    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    if (seconds === 0) {
      return `${minutes} min`;
    }

    return `${minutes} min ${seconds} sec`;
  }

  get totalPages(): number {
    const total = Math.ceil(this.quizzes.length / this.pageSize);
    return Math.max(total, 1);
  }

  get paginatedQuizzes(): any[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.quizzes.slice(start, start + this.pageSize);
  }

  get showPagination(): boolean {
    return this.quizzes.length > this.pageSize;
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
}
