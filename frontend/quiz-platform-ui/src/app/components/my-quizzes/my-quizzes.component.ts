import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { QuizService } from '../../services/quiz.service';
import { AuthService } from '../../services/auth.service';
import { WebSocketService } from '../../services/websocket.service';
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
  isLoading = true;
  errorMessage = '';
  successMessage = '';
  private wsSubscriptions: Subscription[] = [];

  constructor(
    private quizService: QuizService,
    private authService: AuthService,
    private router: Router,
    private wsService: WebSocketService
  ) {}

  ngOnInit(): void {
    this.loadMyQuizzes();
    this.subscribeToWebSocket();
  }

  ngOnDestroy(): void {
    this.wsSubscriptions.forEach(sub => sub.unsubscribe());
  }

  subscribeToWebSocket(): void {
    // Subscribe to quiz approval notifications
    this.wsSubscriptions.push(
      this.wsService.quizApproved$.subscribe({
        next: (data: any) => {
          console.log('MyQuizzes - Quiz approved notification:', data);
          this.loadMyQuizzes();
        }
      })
    );

    // Subscribe to quiz rejection notifications
    this.wsSubscriptions.push(
      this.wsService.quizRejected$.subscribe({
        next: (data: any) => {
          console.log('MyQuizzes - Quiz rejected notification:', data);
          this.loadMyQuizzes();
        }
      })
    );

    // Subscribe to quiz deleted notifications
    this.wsSubscriptions.push(
      this.wsService.quizDeleted$.subscribe({
        next: (data: any) => {
          console.log('MyQuizzes - Quiz deleted notification:', data);
          this.loadMyQuizzes();
        }
      })
    );
  }

  loadMyQuizzes(): void {
    this.isLoading = true;
    console.log('MyQuizzes - Loading quizzes...');
    console.log('MyQuizzes - Token:', localStorage.getItem('access_token'));
    console.log('MyQuizzes - User:', localStorage.getItem('user'));

    this.quizService.getMyQuizzes().subscribe({
      next: (data) => {
        console.log('MyQuizzes - Success:', data);
        this.quizzes = data;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('MyQuizzes - Error:', error);
        console.error('MyQuizzes - Error status:', error.status);
        console.error('MyQuizzes - Error message:', error.error);
        this.errorMessage = error.error?.message || 'Failed to load quizzes';
        this.isLoading = false;
      }
    });
  }

  viewQuiz(quizId: any): void {
    const id = quizId?.$oid || quizId;
    this.router.navigate(['/quiz', id]);
  }

  editQuiz(quizId: any): void {
    const id = quizId?.$oid || quizId;
    this.router.navigate(['/quiz/edit', id]);
  }

  deleteQuiz(quizId: any): void {
    if (!confirm('Are you sure you want to delete this quiz?')) {
      return;
    }

    const id = quizId?.$oid || quizId;

    this.quizService.deleteQuiz(id).subscribe({
      next: () => {
        this.loadMyQuizzes();
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Failed to delete quiz';
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
}
