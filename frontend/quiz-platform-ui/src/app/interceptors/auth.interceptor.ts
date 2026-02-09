import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');

  console.log('Auth Interceptor - Request URL:', req.url);
  console.log('Auth Interceptor - Token present:', !!token);

  if (token) {
    const cloned = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    console.log('Auth Interceptor - Authorization header added');
    return next(cloned);
  }

  console.log('Auth Interceptor - No token, proceeding without auth');
  return next(req);
};
