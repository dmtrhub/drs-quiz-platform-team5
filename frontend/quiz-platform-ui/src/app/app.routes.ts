import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { guestGuard } from './guards/guest.guard';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { QuizListComponent } from './components/quiz-list/quiz-list.component';
import { QuizFormComponent } from './components/quiz-form/quiz-form.component';


export const routes: Routes = [
  { path: '', redirectTo: '/quizzes', pathMatch: 'full' },
  { path: 'login', component: LoginComponent, canActivate: [guestGuard] },
  { path: 'register', component: RegisterComponent, canActivate: [guestGuard] },
  { path: 'quizzes', component: QuizListComponent, canActivate: [authGuard] },
  { path: 'quiz/create', component: QuizFormComponent, canActivate: [authGuard] },
  { path: 'quiz/edit/:id', component: QuizFormComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: '/quizzes' }
];