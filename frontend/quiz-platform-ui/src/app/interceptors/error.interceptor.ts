import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError, timer } from 'rxjs';
import { mergeMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';
import { WebSocketService } from '../services/websocket.service';
import { environment } from '../../environments/environment';

const DEFAULT_RATE_LIMIT_COOLDOWN_MS = 900;
const MAX_RATE_LIMIT_COOLDOWN_MS = 6000;
const RATE_LIMIT_NOTICE_COOLDOWN_MS = 4000;

let rateLimitBlockedUntilMs = 0;
let lastRateLimitNoticeAtMs = 0;

function parseRetryAfterMs(error: HttpErrorResponse): number {
  const retryAfterRaw = error.headers?.get('Retry-After');
  if (!retryAfterRaw) {
    return DEFAULT_RATE_LIMIT_COOLDOWN_MS;
  }

  const seconds = Number(retryAfterRaw);
  if (Number.isFinite(seconds) && seconds > 0) {
    return Math.min(MAX_RATE_LIMIT_COOLDOWN_MS, Math.floor(seconds * 1000));
  }

  const retryDateMs = Date.parse(retryAfterRaw);
  if (Number.isFinite(retryDateMs)) {
    return Math.min(MAX_RATE_LIMIT_COOLDOWN_MS, Math.max(0, retryDateMs - Date.now()));
  }

  return DEFAULT_RATE_LIMIT_COOLDOWN_MS;
}

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const notificationService = inject(NotificationService);  
  const wsService = inject(WebSocketService);
  const isApiRequest = req.url.startsWith(environment.apiUrl) || req.url.includes('/api/');

  const waitMs = Math.max(0, rateLimitBlockedUntilMs - Date.now());
  const request$ = isApiRequest && waitMs > 0
    ? timer(waitMs).pipe(mergeMap(() => next(req)))
    : next(req);

  return request$.pipe(
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

      if (isApiRequest && error.status === 429) {
        const cooldownMs = parseRetryAfterMs(error);
        rateLimitBlockedUntilMs = Date.now() + cooldownMs;

        const now = Date.now();
        if (now - lastRateLimitNoticeAtMs > RATE_LIMIT_NOTICE_COOLDOWN_MS) {
          lastRateLimitNoticeAtMs = now;
          console.warn(`[HTTP 429] Rate limited. Cooling down for ${cooldownMs}ms before next requests.`);
        }
      }

      return throwError(() => error);
    })
  );
};
