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
  currentQuestionIndex = 0;
  previewQuestionIndex = 0;
  isLoading = true;
  errorMessage = '';
  quizStarted = false;
  quizSubmitted = false;
  timeRemaining: number = 0;
  timerInterval: any;
  currentUser: any = null;
  isAdminView = false;
  private shouldAutoStart = false;
  private quizDeadlineMs: number | null = null;

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
    this.shouldAutoStart = this.route.snapshot.queryParamMap.get('autostart') === 'true';
    if (quizId) {
      this.loadQuiz(quizId);
    }
  }

  ngOnDestroy(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }

    if (this.quizStarted && !this.quizSubmitted && !this.isAdminView) {
      this.persistAttemptState();
    }
  }

  loadQuiz(quizId: string): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.quizService.getQuizById(quizId).subscribe({
      next: (response) => {
        this.quiz = response.quiz || response;
        this.previewQuestionIndex = 0;
        this.timeRemaining = this.quiz.duration_seconds || this.quiz.time_limit;

        // Check if moderator is viewing their own approved quiz (read-only mode)
        this.authService.currentUser$.subscribe(user => {
          if (user && user.role === 'MODERATOR' && this.quiz.status === 'APPROVED') {
            this.isAdminView = true; // Treat as read-only view
          }
        });

        if (!this.isAdminView) {
          this.initializeAnswers();
          this.restoreAttemptState();
        }
        this.isLoading = false;

        if (this.quizStarted && !this.isAdminView) {
          if (this.timeRemaining <= 0) {
            this.submitQuiz(true);
            return;
          }
          this.startTimer();
        } else if (this.shouldAutoStart && !this.isAdminView) {
          this.startQuiz();
        }
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
    this.currentQuestionIndex = 0;
  }

  startQuiz(): void {
    if (this.quizStarted || this.isAdminView || !this.quiz) {
      return;
    }
    this.quizStarted = true;
    if (!this.quizDeadlineMs) {
      this.quizDeadlineMs = Date.now() + (this.timeRemaining * 1000);
    }
    this.persistAttemptState();
    this.startTimer();
  }

  startTimer(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }

    this.timerInterval = setInterval(() => {
      if (this.quizDeadlineMs) {
        this.timeRemaining = Math.max(0, Math.ceil((this.quizDeadlineMs - Date.now()) / 1000));
      } else {
        this.timeRemaining--;
      }

      this.persistAttemptState();

      if (this.timeRemaining <= 0) {
        this.submitQuiz(true);
      }
    }, 1000);
  }

  onAnswerChange(): void {
    this.persistAttemptState();
  }

  get totalQuestions(): number {
    return this.quiz?.questions?.length || 0;
  }

  get currentQuestion(): any | null {
    if (!this.quiz?.questions?.length) {
      return null;
    }
    return this.quiz.questions[this.currentQuestionIndex] ?? null;
  }

  get answeredCount(): number {
    return this.answers.filter((answer) => answer.answer_index !== null && answer.answer_index !== undefined).length;
  }

  get allQuestionsAnswered(): boolean {
    return this.totalQuestions > 0 && this.answeredCount === this.totalQuestions;
  }

  get isLastQuestion(): boolean {
    return this.currentQuestionIndex >= this.totalQuestions - 1;
  }

  get questionProgressPercent(): number {
    if (this.totalQuestions === 0) {
      return 0;
    }
    return ((this.currentQuestionIndex + 1) / this.totalQuestions) * 100;
  }

  get previewQuestion(): any | null {
    if (!this.quiz?.questions?.length) {
      return null;
    }
    return this.quiz.questions[this.previewQuestionIndex] ?? null;
  }

  get previewProgressPercent(): number {
    if (this.totalQuestions === 0) {
      return 0;
    }
    return ((this.previewQuestionIndex + 1) / this.totalQuestions) * 100;
  }

  goToPreviewQuestion(index: number): void {
    if (index < 0 || index >= this.totalQuestions) {
      return;
    }
    this.previewQuestionIndex = index;
  }

  previousPreviewQuestion(): void {
    this.goToPreviewQuestion(this.previewQuestionIndex - 1);
  }

  nextPreviewQuestion(): void {
    this.goToPreviewQuestion(this.previewQuestionIndex + 1);
  }

  isQuestionAnswered(index: number): boolean {
    const answer = this.answers[index];
    return !!answer && answer.answer_index !== null && answer.answer_index !== undefined;
  }

  goToQuestion(index: number): void {
    if (index < 0 || index >= this.totalQuestions) {
      return;
    }
    this.currentQuestionIndex = index;
    this.persistAttemptState();
  }

  nextQuestion(): void {
    this.goToQuestion(this.currentQuestionIndex + 1);
  }

  previousQuestion(): void {
    this.goToQuestion(this.currentQuestionIndex - 1);
  }

  getCurrentAnswerIndex(): number | null {
    const current = this.answers[this.currentQuestionIndex];
    if (!current) {
      return null;
    }
    return current.answer_index;
  }

  setCurrentAnswer(answerIndex: number): void {
    const current = this.answers[this.currentQuestionIndex];
    if (!current) {
      return;
    }
    current.answer_index = answerIndex;
    this.onAnswerChange();
  }

  formatTime(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
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

  submitQuiz(force = false): void {
    if (!force && !this.allQuestionsAnswered) {
      this.errorMessage = 'Please answer all questions before submitting.';
      return;
    }

    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }

    const configuredDuration = this.quiz.duration_seconds || this.quiz.time_limit || 0;
    const timeSpent = Math.max(configuredDuration - this.timeRemaining, 0);
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
        this.clearAttemptState();
        this.quizSubmitted = true;
        this.router.navigate(['/results'], {
          state: {
            justSubmittedQuizId: quizId,
            submittedAtMs: Date.now()
          }
        });
      },
      error: (error) => {
        this.errorMessage = 'Failed to submit quiz: ' + (error.error?.error || error.error?.message || 'Unknown error');
        if (this.timeRemaining > 0) {
          this.startTimer();
        }
      }
    });
  }

  viewLeaderboard(): void {
    const quizId = this.quiz._id?.$oid || this.quiz._id;
    this.router.navigate(['/leaderboard'], { state: { preselectedQuizId: quizId } });
  }

  goBack(): void {
    if (this.quizStarted && !this.quizSubmitted && !this.isAdminView) {
      this.persistAttemptState();
    }
    this.router.navigate(['/quizzes']);
  }

  private getCurrentQuizId(): string {
    return this.quiz?._id?.$oid || this.quiz?._id || '';
  }

  private getAttemptStorageKey(quizId: string): string {
    const userId = this.authService.getCurrentUser()?.id || 'anon';
    return `quiz_attempt_${userId}_${quizId}`;
  }

  private persistAttemptState(): void {
    if (this.isAdminView || !this.quiz || this.quizSubmitted) {
      return;
    }

    const quizId = this.getCurrentQuizId();
    if (!quizId) {
      return;
    }

    const state = {
      quizId,
      quizStarted: this.quizStarted,
      quizSubmitted: this.quizSubmitted,
      currentQuestionIndex: this.currentQuestionIndex,
      timeRemaining: this.timeRemaining,
      quizDeadlineMs: this.quizDeadlineMs,
      answers: this.answers.map((answer) => ({
        question_id: answer.question_id,
        answer_index: answer.answer_index
      }))
    };

    localStorage.setItem(this.getAttemptStorageKey(quizId), JSON.stringify(state));
  }

  private restoreAttemptState(): void {
    if (!this.quiz || this.isAdminView) {
      return;
    }

    const quizId = this.getCurrentQuizId();
    if (!quizId) {
      return;
    }

    const raw = localStorage.getItem(this.getAttemptStorageKey(quizId));
    if (!raw) {
      return;
    }

    try {
      const state = JSON.parse(raw);
      if (state?.quizId !== quizId) {
        return;
      }

      if (Array.isArray(state.answers) && state.answers.length > 0) {
        this.answers = this.quiz.questions.map((_: any, index: number) => ({
          question_id: index,
          answer_index: state.answers[index]?.answer_index ?? null
        }));
      }

      this.quizStarted = !!state.quizStarted;
      this.quizSubmitted = !!state.quizSubmitted;

      if (typeof state.currentQuestionIndex === 'number') {
        this.currentQuestionIndex = Math.max(0, Math.min(state.currentQuestionIndex, this.totalQuestions - 1));
      }

      if (typeof state.quizDeadlineMs === 'number') {
        const restoredDeadlineMs = state.quizDeadlineMs;
        this.quizDeadlineMs = restoredDeadlineMs;
        this.timeRemaining = Math.max(0, Math.ceil((restoredDeadlineMs - Date.now()) / 1000));
      } else if (typeof state.timeRemaining === 'number') {
        this.timeRemaining = Math.max(0, state.timeRemaining);
      }
    } catch {
      this.clearAttemptState();
    }
  }

  private clearAttemptState(): void {
    const quizId = this.getCurrentQuizId();
    if (!quizId) {
      return;
    }
    localStorage.removeItem(this.getAttemptStorageKey(quizId));
  }
}
