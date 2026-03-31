import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { QuizService } from '../../services/quiz.service';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';
import { WebSocketService } from '../../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-quiz-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './quiz-list.component.html',
  styleUrl: './quiz-list.component.css'
})
export class QuizListComponent implements OnInit, OnDestroy {
  quizzes: any[] = [];
  filteredQuizzes: any[] = [];
  playerPageSize = 12;
  adminPageSize = 9;
  playerCurrentPage = 1;
  isLoading = true;
  errorMessage = '';
  currentUser: any = null;
  filterStatus: string = 'APPROVED';
  private wsSubscriptions: Subscription[] = [];
  private liveReloadTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly liveReloadDebounceMs = 250;

  constructor(
    private quizService: QuizService,
    private authService: AuthService,
    private notificationService: NotificationService,
    private wsService: WebSocketService,
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
    this.subscribeToWebSocket();
    this.loadQuizzes();
  }

  ngOnDestroy(): void {
    this.wsSubscriptions.forEach((sub) => sub.unsubscribe());
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
      this.loadQuizzes();
    }, this.liveReloadDebounceMs);
  }

  private subscribeToWebSocket(): void {
    this.wsSubscriptions.push(
      this.wsService.quizDeleted$.subscribe({
        next: () => this.scheduleLiveReload()
      })
    );

    this.wsSubscriptions.push(
      this.wsService.quizCreated$.subscribe({
        next: () => this.scheduleLiveReload()
      })
    );

    this.wsSubscriptions.push(
      this.wsService.quizApproved$.subscribe({
        next: () => this.scheduleLiveReload()
      })
    );

    this.wsSubscriptions.push(
      this.wsService.quizPublished$.subscribe({
        next: () => this.scheduleLiveReload()
      })
    );

    this.wsSubscriptions.push(
      this.wsService.quizRejected$.subscribe({
        next: () => this.scheduleLiveReload()
      })
    );
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
        this.playerCurrentPage = 1;
        this.isLoading = false;
      },
      error: (error) => {
        if (error?.status === 401) {
          this.authService.logout();
          this.router.navigate(['/login'], { queryParams: { sessionExpired: 'true' } });
          return;
        }
        this.errorMessage = 'Failed to load quizzes. Please try again.';
        this.isLoading = false;
      }
    });
  }

  filterByStatus(status: string): void {
    this.filterStatus = status;
    this.loadQuizzes();
  }

  get totalPlayerPages(): number {
    const total = Math.ceil(this.filteredQuizzes.length / this.currentPageSize);
    return Math.max(total, 1);
  }

  get paginatedQuizzes(): any[] {
    const start = (this.playerCurrentPage - 1) * this.currentPageSize;
    return this.filteredQuizzes.slice(start, start + this.currentPageSize);
  }

  get showPlayerPagination(): boolean {
    return this.filteredQuizzes.length > this.currentPageSize;
  }

  get playerPageNumbers(): number[] {
    return Array.from({ length: this.totalPlayerPages }, (_, index) => index + 1);
  }

  get currentPageSize(): number {
    return this.canApprove() ? this.adminPageSize : this.playerPageSize;
  }

  goToPlayerPage(page: number): void {
    const safePage = Math.max(1, Math.min(page, this.totalPlayerPages));
    this.playerCurrentPage = safePage;
  }

  nextPlayerPage(): void {
    this.goToPlayerPage(this.playerCurrentPage + 1);
  }

  previousPlayerPage(): void {
    this.goToPlayerPage(this.playerCurrentPage - 1);
  }

  canCreateQuiz(): boolean {
    return this.currentUser &&
           (this.currentUser.role === 'MODERATOR' || this.currentUser.role === 'ADMIN');
  }

  canApprove(): boolean {
    return this.currentUser && this.currentUser.role === 'ADMIN';
  }

  isPlayer(): boolean {
    return this.currentUser?.role === 'PLAYER';
  }

  showAuthorInfo(): boolean {
    return !this.isPlayer();
  }

  getQuestionCount(quiz: any): number {
    return Array.isArray(quiz?.questions) ? quiz.questions.length : 0;
  }

  getDurationSeconds(quiz: any): number {
    const duration = Number(quiz?.duration_seconds ?? quiz?.time_limit ?? 0);
    return Number.isFinite(duration) && duration > 0 ? duration : 0;
  }

  formatDurationForCard(quiz: any): string {
    const totalSeconds = this.getDurationSeconds(quiz);

    if (totalSeconds >= 60) {
      const minutes = Math.floor(totalSeconds / 60);
      const seconds = totalSeconds % 60;
      if (seconds === 0) {
        return `${minutes} min`;
      }
      return `${minutes} min ${seconds} sec`;
    }

    return `${totalSeconds} sec`;
  }

  // Arrow function keeps component context when Angular calls trackBy.
  trackByQuizId = (index: number, quiz: any): string => {
    const id = this.normalizeQuizId(quiz?._id);
    return id || String(index);
  };

  private normalizeQuizId(quizId: any): string {
    if (!quizId) {
      return '';
    }
    if (typeof quizId === 'string') {
      return quizId;
    }
    if (quizId?.$oid && typeof quizId.$oid === 'string') {
      return quizId.$oid;
    }
    return String(quizId);
  }

  viewQuiz(quizId: any): void {
    const id = this.normalizeQuizId(quizId);
    this.router.navigate(['/quiz', id]);
  }

  onCardClick(quiz: any): void {
    if (this.isPlayer()) {
      return;
    }
    this.viewQuiz(quiz?._id);
  }

  async startQuizFromCard(quiz: any, event: Event): Promise<void> {
    event.stopPropagation();
    const id = this.normalizeQuizId(quiz?._id);
    if (!id) {
      this.notificationService.error('Invalid quiz ID');
      return;
    }

    const title = (quiz?.title || 'Untitled Quiz').trim();
    const confirmed = await this.notificationService.confirm({
      title: 'Start Quiz',
      message: `Start "${title}" now?`,
      confirmText: 'Start',
      cancelText: 'Cancel',
      variant: 'primary'
    });

    if (!confirmed) {
      return;
    }

    this.router.navigate(['/quiz', id], { queryParams: { autostart: 'true' } });
  }

  openLeaderboardFromCard(quizId: any, event: Event): void {
    event.stopPropagation();
    const id = this.normalizeQuizId(quizId);
    if (!id) {
      this.notificationService.error('Invalid quiz ID');
      return;
    }
    this.router.navigate(['/leaderboard'], { state: { preselectedQuizId: id } });
  }

  createQuiz(): void {
    this.router.navigate(['/quiz/create']);
  }

  private removeQuizFromLocalLists(quizId: string): void {
    this.quizzes = this.quizzes.filter((quiz) => this.normalizeQuizId(quiz._id) !== quizId);
    this.filteredQuizzes = this.filteredQuizzes.filter((quiz) => this.normalizeQuizId(quiz._id) !== quizId);
    if (this.playerCurrentPage > this.totalPlayerPages) {
      this.playerCurrentPage = this.totalPlayerPages;
    }
  }

  async approveQuiz(quizId: any, event: Event): Promise<void> {
    event.stopPropagation();
    const id = this.normalizeQuizId(quizId);
    if (!id) {
      this.notificationService.error('Invalid quiz ID');
      return;
    }
    const confirmed = await this.notificationService.confirm({
      title: 'Approve Quiz',
      message: 'Do you want to approve this quiz now?',
      confirmText: 'Approve',
      cancelText: 'Cancel',
      variant: 'primary'
    });
    if (!confirmed) {
      return;
    }

    this.quizService.approveQuiz(id, {}).subscribe({
      next: () => {
        this.notificationService.success('Quiz approved successfully');
        this.loadQuizzes();
      },
      error: (error) => {
        this.notificationService.error(
          error.error?.error || error.error?.message || 'Failed to approve quiz'
        );
      }
    });
  }

  rejectQuiz(quizId: any, event: Event): void {
    event.stopPropagation();
    const id = this.normalizeQuizId(quizId);
    if (!id) {
      this.notificationService.error('Invalid quiz ID');
      return;
    }
    const reason = prompt('Enter rejection reason:');
    const trimmedReason = (reason || '').trim();
    if (trimmedReason) {
      this.quizService.rejectQuiz(id, { reason: trimmedReason }).subscribe({
        next: () => {
          this.notificationService.info('Quiz rejected');
          this.loadQuizzes();
        },
        error: (error) => {
          this.notificationService.error(
            error.error?.error || error.error?.message || 'Failed to reject quiz'
          );
        }
      });
    }
  }

  async deleteQuiz(quizId: any, event: Event): Promise<void> {
    event.stopPropagation();
    const id = this.normalizeQuizId(quizId);
    if (!id) {
      this.notificationService.error('Invalid quiz ID');
      return;
    }
    const confirmed = await this.notificationService.confirm({
      title: 'Delete Quiz',
      message: 'This quiz will be permanently deleted. This action cannot be undone.',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      variant: 'danger'
    });
    if (!confirmed) {
      return;
    }

    this.quizService.deleteQuiz(id).subscribe({
      next: () => {
        this.removeQuizFromLocalLists(id);
        this.notificationService.success('Quiz deleted successfully');
      },
      error: (error) => {
        this.notificationService.error(
          error.error?.error || error.error?.message || 'Failed to delete quiz'
        );
      }
    });
  }
}
