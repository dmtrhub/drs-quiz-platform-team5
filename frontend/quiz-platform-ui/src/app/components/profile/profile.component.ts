import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  currentUser: any = null;
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  isEditing = false;

  profile = {
    first_name: '',
    last_name: '',
    email: '',
    birth_date: '',
    gender: '',
    country: '',
    street: '',
    street_number: '',
    profile_image: '',
    role: ''
  };

  passwordChange = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  };

  selectedFile: File | null = null;
  imagePreview: string | null = null;

  constructor(
    private userService: UserService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.currentUser = user;
        this.loadProfile();
      }
    });
  }

  loadProfile(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.userService.getUser(this.currentUser.id).subscribe({
      next: (user) => {
        this.profile = {
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          email: user.email || '',
          birth_date: user.birth_date || '',
          gender: user.gender || '',
          country: user.country || '',
          street: user.street || '',
          street_number: user.street_number || '',
          profile_image: user.profile_image || '',
          role: user.role || ''
        };
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load profile. Please try again.';
        this.isLoading = false;
      }
    });
  }

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (!this.isEditing) {
      this.loadProfile();
      this.passwordChange = {
        current_password: '',
        new_password: '',
        confirm_password: ''
      };
      this.selectedFile = null;
      this.imagePreview = null;
    }
    this.errorMessage = '';
    this.successMessage = '';
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;

      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  onSubmit(): void {
    if (this.passwordChange.new_password || this.passwordChange.confirm_password) {
      if (!this.passwordChange.current_password) {
        this.errorMessage = 'Current password is required to change password';
        return;
      }
      if (this.passwordChange.new_password !== this.passwordChange.confirm_password) {
        this.errorMessage = 'New passwords do not match';
        return;
      }
      if (this.passwordChange.new_password.length < 8) {
        this.errorMessage = 'New password must be at least 8 characters long';
        return;
      }
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const updateData: any = {
      first_name: this.profile.first_name,
      last_name: this.profile.last_name,
      birth_date: this.profile.birth_date || null,
      gender: this.profile.gender || null,
      country: this.profile.country || null,
      street: this.profile.street || null,
      street_number: this.profile.street_number || null
    };

    if (this.passwordChange.new_password) {
      updateData.current_password = this.passwordChange.current_password;
      updateData.new_password = this.passwordChange.new_password;
    }

    if (this.selectedFile) {
      const reader = new FileReader();
      reader.onload = () => {
        updateData.profile_image = reader.result as string;
        this.updateProfile(updateData);
      };
      reader.readAsDataURL(this.selectedFile);
    } else {
      this.updateProfile(updateData);
    }
  }

  private updateProfile(updateData: any): void {
    this.userService.updateUser(this.currentUser.id, updateData).subscribe({
      next: (response) => {
        this.successMessage = 'Profile updated successfully!';
        this.isEditing = false;
        this.isLoading = false;
        this.selectedFile = null;
        this.imagePreview = null;
        this.passwordChange = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        };

        this.profile = response.user;

        this.authService.updateUserInStorage(response.user);

        setTimeout(() => this.successMessage = '', 5000);
      },
      error: (error) => {
        console.error('Profile update error:', error);
        this.errorMessage = error.error?.error || error.error?.errors || error.message || 'Failed to update profile. Please try again.';
        this.isLoading = false;
      }
    });
  }

  getProfileImageUrl(): string {
    if (this.imagePreview) {
      return this.imagePreview;
    }
    if (this.profile.profile_image) {
      return this.profile.profile_image;
    }
    return `https://ui-avatars.com/api/?name=${this.profile.first_name}+${this.profile.last_name}&background=667eea&color=fff&size=200`;
  }
}
