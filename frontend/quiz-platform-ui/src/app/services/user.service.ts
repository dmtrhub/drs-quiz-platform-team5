import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { finalize, map, shareReplay, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = environment.apiUrl;
  private inFlightRequests = new Map<string, Observable<any>>();
  private responseCache = new Map<string, { expiresAt: number; data: any }>();
  private readonly cacheTtlMs = 10000;

  constructor(private http: HttpClient) {}

  getAllUsers(): Observable<any[]> {
    return this.cachedGet<any[]>('users:list', () =>
      this.http.get<any>(`${this.apiUrl}/users`).pipe(
        map(response => response.users || [])
      )
    );
  }

  getUser(userId: number): Observable<any> {
    return this.cachedGet<any>(`users:${userId}`, () =>
      this.http.get<any>(`${this.apiUrl}/users/${userId}`).pipe(
        map(response => response.user)
      )
    );
  }

  updateUser(userId: number, data: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/users/${userId}`, data).pipe(
      tap(() => this.invalidateCache())
    );
  }

  deleteUser(userId: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/users/${userId}`).pipe(
      tap(() => this.invalidateCache())
    );
  }

  changeUserRole(userId: number, role: string): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/role`, { role }).pipe(
      tap(() => this.invalidateCache())
    );
  }

  private cachedGet<T>(key: string, requestFactory: () => Observable<T>): Observable<T> {
    const cachedEntry = this.responseCache.get(key);
    if (cachedEntry && cachedEntry.expiresAt > Date.now()) {
      return of(cachedEntry.data as T);
    }

    const inFlight = this.inFlightRequests.get(key) as Observable<T> | undefined;
    if (inFlight) {
      return inFlight;
    }

    const request$ = requestFactory().pipe(
      tap((data) => {
        this.responseCache.set(key, {
          expiresAt: Date.now() + this.cacheTtlMs,
          data
        });
      }),
      finalize(() => this.inFlightRequests.delete(key)),
      shareReplay(1)
    );

    this.inFlightRequests.set(key, request$ as Observable<any>);
    return request$;
  }

  private invalidateCache(): void {
    this.responseCache.clear();
    this.inFlightRequests.clear();
  }
}
