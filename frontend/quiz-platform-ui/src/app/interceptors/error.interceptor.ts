import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';
import { WebSocketService } from '../services/websocket.service';


export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const notificationService = inject(NotificationService);  
  const wsService = inject(WebSocketService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        
        if (authService.isAuthenticated()) {  
          
          console.log('Session expired - logging out');
          notificationService.error('Session expired. Please login again.');
          wsService.disconnect();
          authService.logout();
          router.navigate(['/login'], {
            queryParams: { sessionExpired: 'true' }
          });
        }
      }

      return throwError(() => error);
    })
  );
};
