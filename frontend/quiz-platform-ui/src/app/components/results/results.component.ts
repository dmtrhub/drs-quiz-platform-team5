import { Component, OnDestroy, OnInit } from '@angular/core';
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
  pageSize = 6;
  currentPage = 1;
  isLoading = true;
  errorMessage = '';
  downloadingReportId: string | null = null;

  private pendingSubmittedQuizId: string | null = null;
  private pendingSubmittedAtMs: number | null = null;
  private pollAttempts = 0;
  private pollTimer: any = null;
  private readonly maxPollAttempts = 8;
  private readonly pollIntervalMs = 700;

  constructor(
    private quizService: QuizService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.captureSubmissionState();
    this.loadResults();
  }

  ngOnDestroy(): void {
    this.clearPollTimer();
  }

  loadResults(showLoader: boolean = true): void {
    if (showLoader) {
      this.isLoading = true;
    }
    this.errorMessage = '';

    this.quizService.getMyResults().subscribe({
      next: (response) => {
        this.results = response.results || [];
        if (showLoader) {
          this.currentPage = 1;
        }
        this.isLoading = false;
        this.handlePendingSubmissionPolling();
      },
      error: (error) => {
        this.errorMessage = 'Failed to load results';
        this.isLoading = false;
        this.clearPollTimer();
      }
    });
  }

  private captureSubmissionState(): void {
    const navigationState = this.router.getCurrentNavigation()?.extras?.state as any;
    const historyState = history.state as any;

    const submittedQuizId = navigationState?.justSubmittedQuizId || historyState?.justSubmittedQuizId;
    const submittedAtMs = navigationState?.submittedAtMs || historyState?.submittedAtMs;

    if (!submittedQuizId || !submittedAtMs) {
      return;
    }

    this.pendingSubmittedQuizId = String(submittedQuizId);
    this.pendingSubmittedAtMs = Number(submittedAtMs);
    this.pollAttempts = 0;
  }

  private handlePendingSubmissionPolling(): void {
    if (!this.pendingSubmittedQuizId || !this.pendingSubmittedAtMs) {
      return;
    }

    if (this.hasNewlySubmittedResult()) {
      this.pendingSubmittedQuizId = null;
      this.pendingSubmittedAtMs = null;
      this.clearPollTimer();
      return;
    }

    if (this.pollAttempts >= this.maxPollAttempts) {
      this.clearPollTimer();
      return;
    }

    this.pollAttempts += 1;
    this.clearPollTimer();
    this.pollTimer = setTimeout(() => {
      this.loadResults(false);
    }, this.pollIntervalMs);
  }

  private hasNewlySubmittedResult(): boolean {
    if (!this.pendingSubmittedQuizId || !this.pendingSubmittedAtMs) {
      return true;
    }

    return this.results.some((result) => {
      const resultQuizId = this.normalizeId(result?.quiz_id);
      if (resultQuizId !== this.pendingSubmittedQuizId) {
        return false;
      }

      const submittedAtMs = this.parseSubmittedAtMs(result?.submitted_at);
      if (submittedAtMs === null) {
        return false;
      }

      return submittedAtMs >= this.pendingSubmittedAtMs!;
    });
  }

  private parseSubmittedAtMs(submittedAt: any): number | null {
    if (!submittedAt) {
      return null;
    }

    if (typeof submittedAt === 'string' || typeof submittedAt === 'number') {
      const parsed = new Date(submittedAt).getTime();
      return Number.isFinite(parsed) ? parsed : null;
    }

    if (submittedAt.$date) {
      const parsed = new Date(submittedAt.$date).getTime();
      return Number.isFinite(parsed) ? parsed : null;
    }

    return null;
  }

  private normalizeId(value: any): string {
    if (!value) {
      return '';
    }
    return String(value?.$oid || value);
  }

  private clearPollTimer(): void {
    if (!this.pollTimer) {
      return;
    }
    clearTimeout(this.pollTimer);
    this.pollTimer = null;
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

  downloadReport(resultId: any): void {
    const id = resultId?.$oid || resultId;
    if (!id) {
      return;
    }

    this.downloadingReportId = id;

    this.quizService.downloadUserReport(id).subscribe({
      next: (blob) => {
        const objectUrl = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = objectUrl;
        anchor.download = `quiz_result_${id}.pdf`;
        anchor.click();
        URL.revokeObjectURL(objectUrl);
        this.downloadingReportId = null;
      },
      error: (error) => {
        this.errorMessage = error?.error?.error || 'Failed to download report';
        this.downloadingReportId = null;
      }
    });
  }

  get totalPages(): number {
    const total = Math.ceil(this.results.length / this.pageSize);
    return Math.max(total, 1);
  }

  get paginatedResults(): any[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.results.slice(start, start + this.pageSize);
  }

  get showPagination(): boolean {
    return this.results.length > this.pageSize;
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
