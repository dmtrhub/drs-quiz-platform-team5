import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = '/api';

  constructor(private http: HttpClient) {}

    getAllUsers(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/users`).pipe(
      map(response => response.users || [])
    );
  }

    getUser(userId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/users/${userId}`).pipe(
      map(response => response.user)
    );
  }

    updateUser(userId: number, data: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/users/${userId}`, data);
  }

    deleteUser(userId: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/users/${userId}`);
  }

    changeUserRole(userId: number, role: string): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/role`, { role });
  }
}
