import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  console.log('AuthGuard - Checking authentication for:', state.url);
  console.log('AuthGuard - Token exists:', !!authService.getToken());
  console.log('AuthGuard - Is authenticated:', authService.isAuthenticated());
  console.log('AuthGuard - Current user:', authService.getCurrentUser());

  if (authService.isAuthenticated()) {
    console.log('AuthGuard - Access granted');
    return true;
  }

  console.log('AuthGuard - Access denied, redirecting to login');
  router.navigate(['/login']);
  return false;
};
