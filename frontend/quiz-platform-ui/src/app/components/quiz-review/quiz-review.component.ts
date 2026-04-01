import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { QuizService } from '../../services/quiz.service';
import { WebSocketService } from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-quiz-review',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './quiz-review.component.html',
  styleUrl: './quiz-review.component.css'
})
export class QuizReviewComponent implements OnInit, OnDestroy {
  pendingQuizzes: any[] = [];
  pageSize = 9;
  currentPage = 1;
  selectedQuiz: any = null;
  reviewQuestionIndex = 0;
  isLoading = true;
  errorMessage = '';
  successMessage = '';
  private wsSubscriptions: Subscription[] = [];
  private liveReloadTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly liveReloadDebounceMs = 300;

  reviewForm = {
    rejectionReason: ''
  };

  constructor(
    private quizService: QuizService,
    private wsService: WebSocketService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    // Stagger component load to prevent request burst (429 rate limiting)
    setTimeout(() => {
      this.loadPendingQuizzes();
    }, 700);
    this.subscribeToWebSocket();
  }

  ngOnDestroy(): void {
    this.wsSubscriptions.forEach(sub => sub.unsubscribe());
    if (this.liveReloadTimer) {
      clearTimeout(this.liveReloadTimer);
      this.liveReloadTimer = null;
    }
  }

  private scheduleLiveReload(): void {
    if (this.liveReloadTimer) {
      clearTimeout(this.liveReloadTimer);
    }

    this.liveReloadTimer = setTimeout(() => {
      this.liveReloadTimer = null;
      this.loadPendingQuizzes();
    }, this.liveReloadDebounceMs);
  }

  subscribeToWebSocket(): void {
    this.wsSubscriptions.push(
      this.wsService.quizCreated$.subscribe({
        next: () => {
          this.scheduleLiveReload();
        }
      })
    );

    this.wsSubscriptions.push(
      this.wsService.quizDeleted$.subscribe({
        next: () => {
          this.scheduleLiveReload();
        }
      })
    );
  }

  loadPendingQuizzes(): void {
    this.isLoading = true;
    this.quizService.getPendingQuizzes().subscribe({
      next: (data) => {
        this.pendingQuizzes = data;
        this.currentPage = 1;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = error.error?.error || error.error?.message || 'Failed to load pending quizzes';
        this.isLoading = false;
      }
    });
  }

  viewQuiz(quiz: any): void {
    this.selectedQuiz = quiz;
    this.reviewQuestionIndex = 0;
    this.reviewForm.rejectionReason = '';
  }

  closeQuizView(): void {
    this.selectedQuiz = null;
    this.reviewQuestionIndex = 0;
    this.reviewForm.rejectionReason = '';
  }

  approveQuiz(): void {
    if (!this.selectedQuiz) return;

    const quizId = this.selectedQuiz._id?.$oid || this.selectedQuiz._id;

    this.quizService.approveQuiz(quizId, {}).subscribe({
      next: () => {
        this.successMessage = 'Quiz approved successfully!';
        this.closeQuizView();
        this.loadPendingQuizzes();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || error.error?.message || 'Failed to approve quiz';
      }
    });
  }

  rejectQuiz(): void {
    if (!this.selectedQuiz) return;

    if (!this.reviewForm.rejectionReason) {
      this.errorMessage = 'Please provide a rejection reason';
      return;
    }

    const reviewData = {
      reason: this.reviewForm.rejectionReason
    };

    const quizId = this.selectedQuiz._id?.$oid || this.selectedQuiz._id;

    this.quizService.rejectQuiz(quizId, reviewData).subscribe({
      next: () => {
        this.successMessage = 'Quiz rejected successfully!';
        this.closeQuizView();
        this.loadPendingQuizzes();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || error.error?.message || 'Failed to reject quiz';
      }
    });
  }

  deleteQuiz(quizId: any): void {
    this.confirmAndDeleteQuiz(quizId);
  }

  private async confirmAndDeleteQuiz(quizId: any): Promise<void> {
    const confirmed = await this.notificationService.confirm({
      title: 'Delete Quiz',
      message: 'Delete this pending quiz permanently?',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      variant: 'danger'
    });

    if (!confirmed) {
      return;
    }

    const id = quizId?.$oid || quizId;
    if (!id) {
      this.notificationService.error('Invalid quiz ID');
      return;
    }

    this.quizService.deleteQuiz(id).subscribe({
      next: () => {
        this.successMessage = 'Quiz deleted successfully!';
        this.notificationService.success('Quiz deleted successfully');
        const selectedId = this.selectedQuiz?._id?.$oid || this.selectedQuiz?._id;
        if (selectedId === id) {
          this.closeQuizView();
        }
        this.pendingQuizzes = this.pendingQuizzes.filter((quiz) => {
          const currentId = quiz?._id?.$oid || quiz?._id;
          return currentId !== id;
        });
        if (this.currentPage > this.totalPages) {
          this.currentPage = this.totalPages;
        }
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || error.error?.message || 'Failed to delete quiz';
        this.notificationService.error(this.errorMessage);
      }
    });
  }

  getCreatedDate(createdAt: any): Date {
    if (!createdAt) return new Date();
        if (createdAt.$date) {
      return new Date(createdAt.$date);
    }
       return new Date(createdAt);
  }

  getQuizId(quiz: any): string {
    return quiz?._id?.$oid || quiz?._id || '';
  }

  isSelectedQuiz(quiz: any): boolean {
    if (!this.selectedQuiz) {
      return false;
    }
    return this.getQuizId(this.selectedQuiz) === this.getQuizId(quiz);
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

  get totalReviewQuestions(): number {
    return this.selectedQuiz?.questions?.length || 0;
  }

  get currentReviewQuestion(): any | null {
    if (!this.selectedQuiz?.questions?.length) {
      return null;
    }
    return this.selectedQuiz.questions[this.reviewQuestionIndex] ?? null;
  }

  get reviewProgressPercent(): number {
    if (this.totalReviewQuestions === 0) {
      return 0;
    }
    return ((this.reviewQuestionIndex + 1) / this.totalReviewQuestions) * 100;
  }

  goToReviewQuestion(index: number): void {
    if (index < 0 || index >= this.totalReviewQuestions) {
      return;
    }
    this.reviewQuestionIndex = index;
  }

  previousReviewQuestion(): void {
    this.goToReviewQuestion(this.reviewQuestionIndex - 1);
  }

  nextReviewQuestion(): void {
    this.goToReviewQuestion(this.reviewQuestionIndex + 1);
  }

  get totalPages(): number {
    const total = Math.ceil(this.pendingQuizzes.length / this.pageSize);
    return Math.max(total, 1);
  }

  get paginatedPendingQuizzes(): any[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.pendingQuizzes.slice(start, start + this.pageSize);
  }

  get showPagination(): boolean {
    return this.pendingQuizzes.length > this.pageSize;
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
