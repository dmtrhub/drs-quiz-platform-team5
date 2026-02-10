import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { QuizService } from '../../services/quiz.service';
import { WebSocketService } from '../../services/websocket.service';
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
    private wsService: WebSocketService
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
        next: (data: any) => {
          console.log('QuizReview - New quiz notification received:', data);
          this.loadPendingQuizzes();
        }
      })
    );

    this.wsSubscriptions.push(
      this.wsService.quizDeleted$.subscribe({
        next: (data: any) => {
          console.log('QuizReview - Quiz deleted notification received:', data);
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
        this.errorMessage = error.error?.message || 'Failed to load pending quizzes';
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
        this.errorMessage = error.error?.message || 'Failed to approve quiz';
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
        this.errorMessage = error.error?.message || 'Failed to reject quiz';
      }
    });
  }

  deleteQuiz(quizId: any): void {
    if (!confirm('Are you sure you want to delete this quiz permanently?')) {
      return;
    }

    const id = quizId?.$oid || quizId;

    this.quizService.deleteQuiz(id).subscribe({
      next: () => {
        this.successMessage = 'Quiz deleted successfully!';
        const selectedId = this.selectedQuiz?._id?.$oid || this.selectedQuiz?._id;
        if (selectedId === id) {
          this.closeQuizView();
        }
        this.loadPendingQuizzes();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Failed to delete quiz';
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
}
