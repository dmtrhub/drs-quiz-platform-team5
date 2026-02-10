import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { QuizService } from '../../services/quiz.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-quiz-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './quiz-form.component.html',
  styleUrl: './quiz-form.component.css'
})
export class QuizFormComponent implements OnInit {
  quiz = {
    title: '',
    time_limit: 600,
    questions: [] as any[]
  };

  quizAuthor = '';
  errorMessage = '';
  successMessage = '';
  isLoading = false;
  isEditMode = false;
  quizId: string | null = null;

  constructor(
    private quizService: QuizService,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.quizAuthor = `${currentUser.first_name} ${currentUser.last_name}`;
    }

    
    this.quizId = this.route.snapshot.paramMap.get('id');
    if (this.quizId) {
      this.isEditMode = true;
      this.loadQuiz(this.quizId);
    } else {
      this.addQuestion();
    }
  }

  loadQuiz(id: string): void {
    this.isLoading = true;
    this.quizService.getQuizById(id).subscribe({
      next: (response) => {
        const quizData = response.quiz || response;
        this.quiz = {
          title: quizData.title,
          time_limit: quizData.duration_seconds || quizData.time_limit,
          questions: quizData.questions || []
        };
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = error.error?.message || 'Failed to load quiz';
        this.isLoading = false;
      }
    });
  }

  addQuestion(): void {
    this.quiz.questions.push({
      text: '',
      points: 10,
      answers: [
        { text: '', correct: false },
        { text: '', correct: false }
      ]
    });
  }

  calculatePenaltyPoints(question: any): number {
    
    const wrongAnswersCount = question.answers.filter((a: any) => !a.correct).length;
    if (wrongAnswersCount === 0) return 0;
    return question.points / wrongAnswersCount;
  }

  removeQuestion(index: number): void {
    this.quiz.questions.splice(index, 1);
  }

  addAnswer(questionIndex: number): void {
    this.quiz.questions[questionIndex].answers.push({ text: '', correct: false });
  }

  removeAnswer(questionIndex: number, answerIndex: number): void {
    if (this.quiz.questions[questionIndex].answers.length > 2) {
      this.quiz.questions[questionIndex].answers.splice(answerIndex, 1);
    }
  }

  toggleCorrectAnswer(questionIndex: number, answerIndex: number): void {
    this.quiz.questions[questionIndex].answers[answerIndex].correct =
      !this.quiz.questions[questionIndex].answers[answerIndex].correct;
  }

  onSubmit(): void {
    if (!this.validateQuiz()) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    
    const quizData = {
      title: this.quiz.title,
      duration_seconds: this.quiz.time_limit, // Backend expects duration_seconds
      questions: this.quiz.questions.map((q: any, qIndex: number) => ({
        order: qIndex,
        text: q.text,
        points: q.points,
        answers: q.answers.map((a: any, aIndex: number) => ({
          text: a.text,
          correct: a.correct,
          order: aIndex
        }))
      }))
    };

    console.log('QuizForm - Submitting quiz data:', JSON.stringify(quizData, null, 2));

    const request = this.isEditMode && this.quizId
      ? this.quizService.updateQuiz(this.quizId, quizData)
      : this.quizService.createQuiz(quizData);

    request.subscribe({
      next: () => {
        this.isLoading = false;
        this.successMessage = this.isEditMode
          ? 'Quiz updated successfully! It will be reviewed by an admin.'
          : 'Quiz created successfully! It will be pending until an admin approves it.';

     
        setTimeout(() => {
          this.router.navigate(['/my-quizzes']);
        }, 2000);
      },
      error: (error) => {
        console.error('QuizForm - Submit error:', error);
        console.error('QuizForm - Error details:', error.error);
        this.errorMessage = error.error?.error || error.error?.message || `Failed to ${this.isEditMode ? 'update' : 'create'} quiz`;
        this.isLoading = false;
      }
    });
  }

  validateQuiz(): boolean {
    if (!this.quiz.title) {
      this.errorMessage = 'Please enter a quiz title';
      return false;
    }

    if (this.quiz.questions.length === 0) {
      this.errorMessage = 'Please add at least one question';
      return false;
    }

    for (let i = 0; i < this.quiz.questions.length; i++) {
      const q = this.quiz.questions[i];

      if (!q.text) {
        this.errorMessage = `Question ${i + 1}: Please enter question text`;
        return false;
      }

      if (!q.answers || q.answers.length < 2) {
        this.errorMessage = `Question ${i + 1}: Must have at least 2 answer options`;
        return false;
      }

      if (q.answers.some((a: any) => !a.text)) {
        this.errorMessage = `Question ${i + 1}: All answer options must have text`;
        return false;
      }

      const correctAnswers = q.answers.filter((a: any) => a.correct);
      if (correctAnswers.length === 0) {
        this.errorMessage = `Question ${i + 1}: Must have at least one correct answer`;
        return false;
      }

    
      q.penalty_points = this.calculatePenaltyPoints(q);
    }

    return true;
  }

  isFormValid(): boolean {
    
    if (!this.quiz.title || !this.quiz.time_limit) {
      return false;
    }

    if (this.quiz.questions.length === 0) {
      return false;
    }

    
    for (const q of this.quiz.questions) {
      if (!q.text || !q.points) {
        return false;
      }

      if (!q.answers || q.answers.length < 2) {
        return false;
      }

      
      if (q.answers.some((a: any) => !a.text)) {
        return false;
      }

      
      const hasCorrectAnswer = q.answers.some((a: any) => a.correct);
      if (!hasCorrectAnswer) {
        return false;
      }
    }

    return true;
  }

  cancel(): void {
    this.router.navigate(['/quizzes']);
  }
}
