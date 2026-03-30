import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

function redirectUnauthorized(router: Router): boolean {
  router.navigate(['/quizzes']);
  return false;
}

export const moderatorGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isModerator()) {
    return true;
  }

  return redirectUnauthorized(router);
};

export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAdmin()) {
    return true;
  }

  return redirectUnauthorized(router);
};
