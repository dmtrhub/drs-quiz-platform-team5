import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError, timer } from 'rxjs';
import { retry, mergeMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';
import { WebSocketService } from '../services/websocket.service';


export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const notificationService = inject(NotificationService);  
  const wsService = inject(WebSocketService);

  return next(req).pipe(
    // Retry 429 responses with exponential backoff
    retry({
      count: 3,
      delay: (error, retryCount) => {
        if (error.status === 429) {
          const delayMs = Math.pow(2, retryCount + 1) * 100; // 200ms, 400ms, 800ms
          console.warn(`[HTTP 429] Rate limited. Retrying in ${delayMs}ms (attempt ${retryCount + 1}/3)`);
          return timer(delayMs);
        }
        return throwError(() => error);
      }
    }),
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        const isAuthRequest =
          req.url.includes('/auth/login') ||
          req.url.includes('/auth/register') ||
          req.url.includes('/auth/logout');

        if (!isAuthRequest) {
          notificationService.error('Session expired. Please login again.');
          wsService.disconnect();
          authService.logout();
          router.navigate(['/login'], {
            queryParams: { sessionExpired: 'true' }
          });
        }
      }

      if (error.status === 429) {
        console.warn('[HTTP 429] Rate limit exceeded after retries');
      }

      return throwError(() => error);
    })
  );
};
