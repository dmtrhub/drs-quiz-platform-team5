import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { QuizService } from '../../services/quiz.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-quiz-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './quiz-list.component.html',
  styleUrl: './quiz-list.component.css'
})
export class QuizListComponent implements OnInit {
  quizzes: any[] = [];
  filteredQuizzes: any[] = [];
  isLoading = true;
  errorMessage = '';
  currentUser: any = null;
  filterStatus: string = 'APPROVED';

  constructor(
    private quizService: QuizService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;

      // Redirect moderators to their quiz page
      if (user && user.role === 'MODERATOR') {
        this.router.navigate(['/my-quizzes']);
        return;
      }
    });
    this.loadQuizzes();
  }

  loadQuizzes(): void {
    this.isLoading = true;
    this.errorMessage = '';

    // Don't pass status filter if "ALL" is selected (for admins)
    const statusFilter = this.filterStatus === 'ALL' ? undefined : this.filterStatus;

    this.quizService.getQuizzes(statusFilter).subscribe({
      next: (quizzes) => {
        this.quizzes = quizzes;
        this.filteredQuizzes = quizzes;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load quizzes. Please try again.';
        this.isLoading = false;
      }
    });
  }

  filterByStatus(status: string): void {
    this.filterStatus = status;
    this.loadQuizzes();
  }

  canCreateQuiz(): boolean {
    return this.currentUser &&
           (this.currentUser.role === 'MODERATOR' || this.currentUser.role === 'ADMIN');
  }

  canApprove(): boolean {
    return this.currentUser && this.currentUser.role === 'ADMIN';
  }

  viewQuiz(quizId: any): void {
    const id = quizId?.$oid || quizId;
    this.router.navigate(['/quiz', id]);
  }

  createQuiz(): void {
    this.router.navigate(['/quiz/create']);
  }

  approveQuiz(quizId: string, event: Event): void {
    event.stopPropagation();
    if (confirm('Are you sure you want to approve this quiz?')) {
      this.quizService.approveQuiz(quizId, {}).subscribe({
        next: () => {
          this.loadQuizzes();
        },
        error: (error) => {
          alert('Failed to approve quiz: ' + (error.error?.message || 'Unknown error'));
        }
      });
    }
  }

  rejectQuiz(quizId: string, event: Event): void {
    event.stopPropagation();
    const reason = prompt('Enter rejection reason:');
    if (reason) {
      this.quizService.rejectQuiz(quizId, reason).subscribe({
        next: () => {
          this.loadQuizzes();
        },
        error: (error) => {
          alert('Failed to reject quiz: ' + (error.error?.message || 'Unknown error'));
        }
      });
    }
  }

  deleteQuiz(quizId: string, event: Event): void {
    event.stopPropagation();
    if (confirm('Are you sure you want to delete this quiz? This cannot be undone.')) {
      this.quizService.deleteQuiz(quizId).subscribe({
        next: () => {
          this.loadQuizzes();
        },
        error: (error) => {
          alert('Failed to delete quiz: ' + (error.error?.message || 'Unknown error'));
        }
      });
    }
  }
}
