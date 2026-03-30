import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export interface Notification {
  message: string;
  type: 'success' | 'error' | 'info';
}

export interface ConfirmDialogOptions {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'primary';
}

export interface ConfirmDialogRequest {
  title: string;
  message: string;
  confirmText: string;
  cancelText: string;
  variant: 'danger' | 'primary';
  resolve: (value: boolean) => void;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notificationSubject = new Subject<Notification>();
  private confirmDialogSubject = new Subject<ConfirmDialogRequest>();
  public notification$ = this.notificationSubject.asObservable();
  public confirmDialog$ = this.confirmDialogSubject.asObservable();

  success(message: string): void {
    this.notificationSubject.next({ message, type: 'success' });
  }

  error(message: string): void {
    this.notificationSubject.next({ message, type: 'error' });
  }

  info(message: string): void {
    this.notificationSubject.next({ message, type: 'info' });
  }

  confirm(options: ConfirmDialogOptions): Promise<boolean> {
    return new Promise((resolve) => {
      this.confirmDialogSubject.next({
        title: options.title,
        message: options.message,
        confirmText: options.confirmText || 'Confirm',
        cancelText: options.cancelText || 'Cancel',
        variant: options.variant || 'primary',
        resolve
      });
    });
  }
}
