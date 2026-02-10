import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { QuizService } from '../../services/quiz.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-quiz-detail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './quiz-detail.component.html',
  styleUrl: './quiz-detail.component.css'
})
export class QuizDetailComponent implements OnInit {
  quiz: any = null;
  answers: any[] = [];
  isLoading = true;
  errorMessage = '';
  quizStarted = false;
  quizSubmitted = false;
  timeRemaining: number = 0;
  timerInterval: any;
  currentUser: any = null;
  isAdminView = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private quizService: QuizService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Check if user is admin
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.isAdminView = !!(user && user.role === 'ADMIN');
    });

    const quizId = this.route.snapshot.paramMap.get('id');
    if (quizId) {
      this.loadQuiz(quizId);
    }
  }

  ngOnDestroy(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  }

  loadQuiz(quizId: string): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.quizService.getQuizById(quizId).subscribe({
      next: (response) => {
        this.quiz = response.quiz || response;
        this.timeRemaining = this.quiz.duration_seconds || this.quiz.time_limit;

        // Check if moderator is viewing their own approved quiz (read-only mode)
        this.authService.currentUser$.subscribe(user => {
          if (user && user.role === 'MODERATOR' && this.quiz.status === 'APPROVED') {
            this.isAdminView = true; // Treat as read-only view
          }
        });

        if (!this.isAdminView) {
          this.initializeAnswers();
        }
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load quiz. Please try again.';
        this.isLoading = false;
      }
    });
  }

  initializeAnswers(): void {
    this.answers = this.quiz.questions.map((q: any, index: number) => ({
      question_id: index,
      answer_index: null
    }));
  }

  startQuiz(): void {
    this.quizStarted = true;
    this.startTimer();
  }

  startTimer(): void {
    this.timerInterval = setInterval(() => {
      this.timeRemaining--;
      if (this.timeRemaining <= 0) {
        this.submitQuiz();
      }
    }, 1000);
  }

  formatTime(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  }

  submitQuiz(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }

    const timeSpent = (this.quiz.duration_seconds || this.quiz.time_limit) - this.timeRemaining;
    const quizId = this.quiz._id?.$oid || this.quiz._id;

    // Transform answers to match backend schema
    const formattedAnswers = this.answers.map((ans: any, index: number) => {
      const question = this.quiz.questions[index];
      const questionId = question._id?.$oid || question._id || index.toString();

      // Get the selected answer's ID (handle unanswered questions)
      if (ans.answer_index === null || ans.answer_index === undefined) {
        // No answer selected - submit empty array or first answer as default
        return {
          question_id: questionId,
          answer_ids: []
        };
      }

      const selectedAnswer = question.answers[ans.answer_index];
      const answerId = selectedAnswer?._id?.$oid || selectedAnswer?._id || ans.answer_index.toString();

      return {
        question_id: questionId,
        answer_ids: [answerId]
      };
    });

    this.quizService.submitQuiz(quizId, formattedAnswers, timeSpent).subscribe({
      next: () => {
        this.quizSubmitted = true;
        setTimeout(() => {
          this.router.navigate(['/results']);
        }, 3000);
      },
      error: (error) => {
        this.errorMessage = 'Failed to submit quiz: ' + (error.error?.message || 'Unknown error');
        this.startTimer();
      }
    });
  }

  viewLeaderboard(): void {
    const quizId = this.quiz._id?.$oid || this.quiz._id;
    this.router.navigate(['/leaderboard'], { state: { preselectedQuizId: quizId } });
  }

  goBack(): void {
    this.router.navigate(['/quizzes']);
  }
}
