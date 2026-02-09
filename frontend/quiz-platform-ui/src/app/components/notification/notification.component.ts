import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService, Notification } from '../../services/notification.service';

@Component({
  selector: 'app-notification',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notification.component.html',
  styleUrl: './notification.component.css'
})
export class NotificationComponent implements OnInit {
  notifications: (Notification & { id: number })[] = [];
  private nextId = 0;

  constructor(private notificationService: NotificationService) {}

  ngOnInit(): void {
    this.notificationService.notification$.subscribe(notification => {
      const id = this.nextId++;
      this.notifications.push({ ...notification, id });

      // Auto-remove after 3 seconds
      setTimeout(() => {
        this.removeNotification(id);
      }, 3000);
    });
  }

  removeNotification(id: number): void {
    this.notifications = this.notifications.filter(n => n.id !== id);
  }
}
