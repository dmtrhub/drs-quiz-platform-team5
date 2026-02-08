import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class QuizService {
    private apiUrl = '/api';

    constructor(private http: HttpClient) {}

    getQuizzes(status?: string): Observable<any> {
        const url = status ? `${this.apiUrl}/quizzes?status=${status}` : `${this.apiUrl}/quizzes`;
        return this.http.get<any>(url).pipe(
            map(response => response.quizzes || []) 
        );
    }
    
  getQuiz(id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/quizzes/${id}`);
  }

  getQuizById(id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/quizzes/${id}`);
  }

  createQuiz(quizData: any): Observable<any> {  
    return this.http.post(`${this.apiUrl}/quizzes`, quizData);
  }

  updateQuiz(id: string, quizData: any): Observable<any> {  
    return this.http.put(`${this.apiUrl}/quizzes/${id}`, quizData);
  }

  getMyQuizzes(): Observable<any> { 
    return this.http.get<any>(`${this.apiUrl}/quizzes/my-quizzes`).pipe(
      map(response => response.quizzes || [])
    );
  }

  getPendingQuizzes(): Observable<any> {  
    return this.http.get<any>(`${this.apiUrl}/quizzes/pending`).pipe(
      map(response => response.quizzes || [])
    );
  }

  approveQuiz(id: string, reviewData: any): Observable<any> { 
    return this.http.put(`${this.apiUrl}/quizzes/${id}/approve`, reviewData);
  }

  rejectQuiz(id: string, reviewData: any): Observable<any> {  
    return this.http.put(`${this.apiUrl}/quizzes/${id}/reject`, reviewData);
  }

  deleteQuiz(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/quizzes/${id}`);
  }

  submitQuiz(quizId: string, answers: any[], timeSpent: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/results/submit?quiz_id=${quizId}`, {
      answers,
      time_spent_seconds: timeSpent 
    });
  }

  getMyResults(): Observable<any> { 
    return this.http.get(`${this.apiUrl}/results/my-results`);
  }

  getLeaderboard(quizId: string, limit: number = 10): Observable<any> { 
    return this.http.get(`${this.apiUrl}/results/leaderboard/${quizId}?limit=${limit}`);
  }

  createPdfReport(quizId: string): Observable<any> {  
    return this.http.post(`${this.apiUrl}/reports/quiz/${quizId}`, {});
  }

}