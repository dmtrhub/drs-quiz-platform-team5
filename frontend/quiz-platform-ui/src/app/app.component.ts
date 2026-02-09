import { Component,OnInit, OnDestroy  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from './services/auth.service';
import { WebSocketService } from './services/websocket.service';
import { NotificationService } from './services/notification.service';
import { NotificationComponent } from './components/notification/notification.component';

@Component({
  selector: 'app-root',
  standalone: true,
   imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, NotificationComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  
  title = 'Quiz Platform';
  currentUser$ = this.authService.currentUser$;
    private wsSubscriptions: Subscription[] = [];

  constructor(
    private authService: AuthService,    
    private wsService: WebSocketService,
    private notificationService: NotificationService,
    private router: Router
  ) {}

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
