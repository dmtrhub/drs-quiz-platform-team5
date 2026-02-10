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
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  
  title = 'Quiz Platform';
  currentUser$ = this.authService.currentUser$;
    private wsSubscriptions: Subscription[] = [];

  constructor(
    private authService: AuthService,    
    private wsService: WebSocketService,
    private notificationService: NotificationService,
    private router: Router
  ) {
    this.subscribeToWebSocketEvents();
  }

  
  ngOnInit(): void {
    const token = this.authService.getToken();
    if (token) {
      this.wsService.connect(token);
    }
  }

  ngOnDestroy(): void {
    this.wsService.disconnect();
    this.wsSubscriptions.forEach(sub => sub.unsubscribe());
  }

  private subscribeToWebSocketEvents(): void {
    
    this.wsSubscriptions.push(
      this.wsService.quizCreated$.subscribe((data: any) => {
        this.notificationService.info(`New quiz "${data.title || 'Untitled'}" submitted for review!`);
      })
    );

    
    this.wsSubscriptions.push(
      this.wsService.quizApproved$.subscribe((data: any) => {
        this.notificationService.success(`Your quiz "${data.title || 'Untitled'}" has been approved!`);
      })
    );

    
    this.wsSubscriptions.push(
      this.wsService.quizRejected$.subscribe((data: any) => {
        this.notificationService.error(`Your quiz "${data.title || 'Untitled'}" was rejected.`);
      })
    );

    
    this.wsSubscriptions.push(
      this.wsService.quizDeleted$.subscribe((data: any) => {
        this.notificationService.info(`Quiz "${data.title || 'Untitled'}" was deleted.`);
      })
    );
  }

  logout(): void {
    this.authService.logout();
    this.wsService.disconnect();
    this.router.navigate(['/login']);
  }

  isPlayer(user: any): boolean {
    return user && user.role === 'PLAYER';
  }

  isModerator(user: any): boolean {
    return user && user.role === 'MODERATOR';
  }

  isAdmin(user: any): boolean {
    return user && user.role === 'ADMIN';
  }

  canCreateQuiz(user: any): boolean {
    return user && (user.role === 'MODERATOR' || user.role === 'ADMIN');
  }

  getProfileImageUrl(user: any): string {
    if (user?.profile_image) {
      return user.profile_image;
    }
    
    return `https://ui-avatars.com/api/?name=${user?.first_name}+${user?.last_name}&background=667eea&color=fff&size=40`;
  }
}
