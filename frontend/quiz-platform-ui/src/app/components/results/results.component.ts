import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { QuizService } from '../../services/quiz.service';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './results.component.html',
  styleUrl: './results.component.css'
})
export class ResultsComponent implements OnInit {
  results: any[] = [];
  isLoading = true;
  errorMessage = '';

  constructor(
    private quizService: QuizService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadResults();
  }

  loadResults(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.quizService.getMyResults().subscribe({
      next: (response) => {
        this.results = response.results || [];
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load results';
        this.isLoading = false;
      }
    });
  }

  viewLeaderboard(quizId: any, quizTitle: string): void {
    const id = quizId?.$oid || quizId;
    this.router.navigate(['/leaderboard'], {
      state: { preselectedQuizId: id, preselectedQuizTitle: quizTitle }
    });
  }

  getPercentage(score: number, maxScore: number): number {
    return maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;
  }
}
