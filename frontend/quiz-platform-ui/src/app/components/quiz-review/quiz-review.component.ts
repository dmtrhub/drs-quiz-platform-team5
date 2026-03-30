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
  selectedQuiz: any = null;
  isLoading = true;
  errorMessage = '';
  successMessage = '';
  private wsSubscriptions: Subscription[] = [];

  reviewForm = {
    rejectionReason: ''
  };

  constructor(
    private quizService: QuizService,
    private wsService: WebSocketService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadPendingQuizzes();
    this.subscribeToWebSocket();
  }

  ngOnDestroy(): void {
    this.wsSubscriptions.forEach(sub => sub.unsubscribe());
  }

  subscribeToWebSocket(): void {
    this.wsSubscriptions.push(
      this.wsService.quizCreated$.subscribe({
        next: () => {
          this.loadPendingQuizzes();
        }
      })
    );

    this.wsSubscriptions.push(
      this.wsService.quizDeleted$.subscribe({
        next: () => {
          this.loadPendingQuizzes();
        }
      })
    );
  }

  loadPendingQuizzes(): void {
    this.isLoading = true;
    this.quizService.getPendingQuizzes().subscribe({
      next: (data) => {
        this.pendingQuizzes = data;
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
    this.reviewForm.rejectionReason = '';
  }

  closeQuizView(): void {
    this.selectedQuiz = null;
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
}
