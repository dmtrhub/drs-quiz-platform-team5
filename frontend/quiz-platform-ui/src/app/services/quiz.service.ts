import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError, timer } from 'rxjs';
import { finalize, map, retry, shareReplay, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class QuizService {
  private apiUrl = environment.apiUrl;
  private inFlightRequests = new Map<string, Observable<any>>();
  private responseCache = new Map<string, { expiresAt: number; data: any }>();
  private readonly listCacheTtlMs = 8000;
  private readonly maxRateLimitRetries = 1;

    constructor(private http: HttpClient) {}

    getQuizzes(status?: string): Observable<any> {
        const url = status ? `${this.apiUrl}/quizzes?status=${status}` : `${this.apiUrl}/quizzes`;
        const requestKey = `quizzes:${status || 'ALL'}`;
        return this.listRequest<any[]>(requestKey, () =>
          this.http.get<any>(url).pipe(
            map(response => response.quizzes || [])
          )
        );
    }
    
  getQuiz(id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/quizzes/${id}`);
  }

  getQuizById(id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/quizzes/${id}`);
  }

  createQuiz(quizData: any): Observable<any> {  
    return this.http.post(`${this.apiUrl}/quizzes`, quizData).pipe(
      tap(() => this.invalidateQuizListCache())
    );
  }

  updateQuiz(id: string, quizData: any): Observable<any> {  
    return this.http.put(`${this.apiUrl}/quizzes/${id}`, quizData).pipe(
      tap(() => this.invalidateQuizListCache())
    );
  }

  getMyQuizzes(): Observable<any> { 
    return this.listRequest<any[]>('my-quizzes', () =>
      this.http.get<any>(`${this.apiUrl}/quizzes/my-quizzes`).pipe(
        map(response => response.quizzes || [])
      )
    );
  }

  getPendingQuizzes(): Observable<any> {  
    return this.listRequest<any[]>('pending-quizzes', () =>
      this.http.get<any>(`${this.apiUrl}/quizzes/pending`).pipe(
        map(response => response.quizzes || [])
      )
    );
  }

  approveQuiz(id: string, reviewData: any): Observable<any> { 
    return this.http.put(`${this.apiUrl}/quizzes/${id}/approve`, reviewData).pipe(
      tap(() => this.invalidateQuizListCache())
    );
  }

  rejectQuiz(id: string, reviewData: any): Observable<any> {  
    return this.http.put(`${this.apiUrl}/quizzes/${id}/reject`, reviewData).pipe(
      tap(() => this.invalidateQuizListCache())
    );
  }

  deleteQuiz(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/quizzes/${id}`).pipe(
      tap(() => this.invalidateQuizListCache())
    );
  }

  submitQuiz(quizId: string, answers: any[], timeSpent: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/quizzes/${quizId}/attempts`, {
      answers,
      time_spent_seconds: timeSpent 
    });
  }

  getMyResults(): Observable<any> { 
    return this.http.get(`${this.apiUrl}/results/my-results`);
  }

  getLeaderboard(quizId: string, limit: number = 500): Observable<any> { 
    return this.http.get(`${this.apiUrl}/results/leaderboard/${quizId}?limit=${limit}`);
  }

  createPdfReport(quizId: string): Observable<any> {  
    return this.http.post(`${this.apiUrl}/reports/quiz/${quizId}`, {});
  }

  downloadUserReport(resultId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/reports/result/${resultId}`, {
      responseType: 'blob'
    });
  }

  private listRequest<T>(key: string, requestFactory: () => Observable<T>): Observable<T> {
    const cached = this.getCachedResponse<T>(key);
    if (cached !== null) {
      return of(cached);
    }

    const existingInFlight = this.inFlightRequests.get(key) as Observable<T> | undefined;
    if (existingInFlight) {
      return existingInFlight;
    }

    const request$ = requestFactory().pipe(
      retry({
        count: this.maxRateLimitRetries,
        delay: (error: any, retryCount: number) => {
          if (error?.status !== 429) {
            return throwError(() => error);
          }

          const delayMs = Math.min(4000, 800 * (2 ** Math.max(0, retryCount - 1)));
          return timer(delayMs);
        }
      }),
      tap((data) => this.setCachedResponse(key, data, this.listCacheTtlMs)),
      finalize(() => this.inFlightRequests.delete(key)),
      shareReplay(1)
    );

    this.inFlightRequests.set(key, request$ as Observable<any>);
    return request$;
  }

  private getCachedResponse<T>(key: string): T | null {
    const cachedEntry = this.responseCache.get(key);
    if (!cachedEntry) {
      return null;
    }

    if (cachedEntry.expiresAt < Date.now()) {
      this.responseCache.delete(key);
      return null;
    }

    return cachedEntry.data as T;
  }

  private setCachedResponse<T>(key: string, data: T, ttlMs: number): void {
    this.responseCache.set(key, {
      expiresAt: Date.now() + ttlMs,
      data
    });
  }

  private invalidateQuizListCache(): void {
    this.responseCache.clear();
  }

}