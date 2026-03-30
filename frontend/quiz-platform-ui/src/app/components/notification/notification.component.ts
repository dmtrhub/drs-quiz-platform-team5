import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import {
  NotificationService,
  Notification,
  ConfirmDialogRequest
} from '../../services/notification.service';

@Component({
  selector: 'app-notification',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notification.component.html',
  styleUrl: './notification.component.css'
})
export class NotificationComponent implements OnInit {
  notifications: (Notification & { id: number })[] = [];
  confirmDialog: ConfirmDialogRequest | null = null;
  private nextId = 0;
  private subscriptions: Subscription[] = [];

  constructor(private notificationService: NotificationService) {}

  ngOnInit(): void {
    this.subscriptions.push(this.notificationService.notification$.subscribe(notification => {
      const id = this.nextId++;
      this.notifications.push({ ...notification, id });

      // Auto-remove after 3 seconds
      setTimeout(() => {
        this.removeNotification(id);
      }, 3000);
    }));

    this.subscriptions.push(this.notificationService.confirmDialog$.subscribe(dialog => {
      this.confirmDialog = dialog;
    }));
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach((sub) => sub.unsubscribe());
  }

  removeNotification(id: number): void {
    this.notifications = this.notifications.filter(n => n.id !== id);
  }

  confirmAction(): void {
    if (!this.confirmDialog) {
      return;
    }
    this.confirmDialog.resolve(true);
    this.confirmDialog = null;
  }

  cancelAction(): void {
    if (!this.confirmDialog) {
      return;
    }
    this.confirmDialog.resolve(false);
    this.confirmDialog = null;
  }
}
