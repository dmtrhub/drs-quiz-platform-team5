import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  user = {
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    birth_date: '',
    gender: '',
    country: '',
    street: '',
    street_number: ''
  };
  errorMessage = '';
  successMessage = '';
  isLoading = false;
  fieldErrors: { [key: string]: string[] } = {};

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    this.fieldErrors = {};
    this.errorMessage = '';

    if (this.user.password !== this.user.confirmPassword) {
      this.errorMessage = 'Passwords do not match';
      return;
    }

    this.isLoading = true;
    this.successMessage = '';

    const registerData = {
      email: this.user.email,
      password: this.user.password,
      first_name: this.user.first_name,
      last_name: this.user.last_name,
      birth_date: this.user.birth_date || null,
      gender: this.user.gender || null,
      country: this.user.country || null,
      street: this.user.street || null,
      street_number: this.user.street_number || null
    };

    this.authService.register(registerData).subscribe({
      next: (response) => {
        this.successMessage = 'Registration successful! Redirecting to login...';
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
        this.isLoading = false;

        if (error.error?.errors) {
          this.fieldErrors = error.error.errors;
          this.errorMessage = 'Please fix the validation errors below';
        } else if (error.error?.error) {
          this.errorMessage = error.error.error;
        } else if (error.error?.message) {
          this.errorMessage = error.error.message;
        } else {
          this.errorMessage = 'Registration failed. Please try again.';
        }
      }
    });
  }

  getFieldError(fieldName: string): string | null {
    if (this.fieldErrors[fieldName] && this.fieldErrors[fieldName].length > 0) {
      return this.fieldErrors[fieldName][0];
    }
    return null;
  }

  hasFieldError(fieldName: string): boolean {
    return this.fieldErrors[fieldName] && this.fieldErrors[fieldName].length > 0;
  }
}
