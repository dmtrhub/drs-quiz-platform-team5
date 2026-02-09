import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: Socket | null = null;
  private quizCreatedSubject = new Subject<any>();
  private quizApprovedSubject = new Subject<any>();
  private quizRejectedSubject = new Subject<any>();
  private quizDeletedSubject = new Subject<any>();

  public quizCreated$ = this.quizCreatedSubject.asObservable();
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
      console.log('[WebSocket] Connected');
      this.socket?.emit('authenticate', { token });
    });

    this.socket.on('authenticated', (data: any) => {
      console.log('[WebSocket] Authenticated as:', data.role);
    });

    this.socket.on('new_quiz_created', (data: any) => {
      console.log('[WebSocket] New quiz created:', data);
      this.quizCreatedSubject.next(data);
    });

    this.socket.on('quiz_approved', (data: any) => {
      console.log('[WebSocket] Quiz approved:', data);
      this.quizApprovedSubject.next(data);
    });

    this.socket.on('quiz_rejected', (data: any) => {
      console.log('[WebSocket] Quiz rejected:', data);
      this.quizRejectedSubject.next(data);
    });

    this.socket.on('quiz_deleted', (data: any) => {
      console.log('[WebSocket] Quiz deleted:', data);
      this.quizDeletedSubject.next(data);
    });

    this.socket.on('connect_error', (error: any) => {
      console.warn('[WebSocket] Connection error (this is normal if WebSocket server is not running):', error.message);
    });

    this.socket.on('error', (error: any) => {
      console.error('[WebSocket] Error:', error);
    });

    this.socket.on('disconnect', () => {
      console.log('[WebSocket] Disconnected');
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}
