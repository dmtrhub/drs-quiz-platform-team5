import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.css'
})
export class UserManagementComponent implements OnInit {
  users: any[] = [];
  filteredUsers: any[] = [];
  isLoading = true;
  errorMessage = '';
  successMessage = '';
  currentUser: any = null;
  searchTerm = '';
  filterRole = 'ALL';
  editingUserId: number | null = null;
  selectedRole: string = '';

  constructor(
    private userService: UserService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (user && user.role === 'ADMIN') {
        this.loadUsers();
      } else {
        this.errorMessage = 'Access denied. Admin privileges required.';
        this.isLoading = false;
      }
    });
  }

  loadUsers(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.userService.getAllUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.applyFilters();
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load users. Please try again.';
        this.isLoading = false;
      }
    });
  }

  applyFilters(): void {
    this.filteredUsers = this.users.filter(user => {
      const matchesSearch = !this.searchTerm ||
        user.email.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        user.first_name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        user.last_name.toLowerCase().includes(this.searchTerm.toLowerCase());

      const matchesRole = this.filterRole === 'ALL' || user.role === this.filterRole;

      return matchesSearch && matchesRole;
    });
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onFilterChange(): void {
    this.applyFilters();
  }

  startEditingRole(userId: number, currentRole: string): void {
    this.editingUserId = userId;
    this.selectedRole = currentRole;
  }

  cancelEditingRole(): void {
    this.editingUserId = null;
    this.selectedRole = '';
  }

  saveRoleChange(userId: number): void {
    if (!this.selectedRole) {
      return;
    }

    this.userService.changeUserRole(userId, this.selectedRole).subscribe({
      next: (response) => {
        this.successMessage = `Role changed to ${this.selectedRole} successfully. User has been notified via email.`;
        this.loadUsers();
        this.editingUserId = null;
        this.selectedRole = '';
        setTimeout(() => this.successMessage = '', 5000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || 'Failed to change user role.';
        setTimeout(() => this.errorMessage = '', 5000);
      }
    });
  }

  changeRole(userId: number, currentRole: string): void {
    this.startEditingRole(userId, currentRole);
  }

  deleteUser(userId: number, userName: string): void {
    if (userId === this.currentUser?.id) {
      alert('You cannot delete your own account.');
      return;
    }

    if (confirm(`Are you sure you want to delete user "${userName}"? This action cannot be undone.`)) {
      this.userService.deleteUser(userId).subscribe({
        next: () => {
          this.successMessage = `User "${userName}" deleted successfully.`;
          this.loadUsers();
          setTimeout(() => this.successMessage = '', 5000);
        },
        error: (error) => {
          this.errorMessage = error.error?.error || 'Failed to delete user.';
          setTimeout(() => this.errorMessage = '', 5000);
        }
      });
    }
  }

  getRoleBadgeClass(role: string): string {
    switch (role) {
      case 'ADMIN':
        return 'badge-admin';
      case 'MODERATOR':
        return 'badge-moderator';
      case 'PLAYER':
      default:
        return 'badge-player';
    }
  }
}
