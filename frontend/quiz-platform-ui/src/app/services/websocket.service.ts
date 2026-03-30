import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: Socket | null = null;
  private quizCreatedSubject = new Subject<any>();
  private quizPublishedSubject = new Subject<any>();
  private quizApprovedSubject = new Subject<any>();
  private quizRejectedSubject = new Subject<any>();
  private quizDeletedSubject = new Subject<any>();

  public quizCreated$ = this.quizCreatedSubject.asObservable();
  public quizPublished$ = this.quizPublishedSubject.asObservable();
  public quizApproved$ = this.quizApprovedSubject.asObservable();
  public quizRejected$ = this.quizRejectedSubject.asObservable();
  public quizDeleted$ = this.quizDeletedSubject.asObservable();

  connect(token: string): void {
    if (this.socket) {
      return;
    }

    const socketUrl = window.location.origin;
    this.socket = io(socketUrl, {
      path: '/socket.io',
      transports: ['polling', 'websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      upgrade: true
    });

    this.socket.on('connect', () => {
      this.socket?.emit('authenticate', { token });
    });

    this.socket.on('new_quiz_created', (data: any) => {
      this.quizCreatedSubject.next(data);
    });

    this.socket.on('quiz_published', (data: any) => {
      this.quizPublishedSubject.next(data);
    });

    this.socket.on('quiz_approved', (data: any) => {
      this.quizApprovedSubject.next(data);
    });

    this.socket.on('quiz_rejected', (data: any) => {
      this.quizRejectedSubject.next(data);
    });

    this.socket.on('quiz_deleted', (data: any) => {
      this.quizDeletedSubject.next(data);
    });

  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}
