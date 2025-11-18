import { Component } from '@angular/core';
import { Persona } from '../../../models/persona';
import { AuthService } from '../../../services/auth/auth-service';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-home-component',
  imports: [CommonModule],
  templateUrl: './home-component.html',
  styleUrl: './home-component.scss'
})
export class HomeComponent {

  constructor(private authService: AuthService,
    private cdr: ChangeDetectorRef
  ){}

  usuario: Persona|null = null
  isUserMenuOpen = false
  isAdmin = false
  isUserRegistered = false
  /**
  **
   * Funcion para mostrar o ocultar los objetos en el menu
   */
  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen
  }

  /**
   * Funcion para redirigir el usuario al login
   */
  handleLogin(): void {
    window.location.href = '/login'
  }

  /**
   * Funcion para redirigir el usuario al registro
   */
  handleRegister(): void {
    window.location.href = '/register'
  }

  handleProfileEdit(): void {
    window.location.href = '/edit'
  }

  ngOnInit(): void {
    this.authService.getUsuarioActual().subscribe({
      next: response => {
        console.log(response)
        this.usuario = response;
        this.isUserRegistered = !!response;
        this.isAdmin = response?.rol === 'Admin';
        this.cdr.detectChanges();
      },
      error: err => {
        // Por ejemplo, si no hay token o el usuario no está autenticado
        this.usuario = null;
        this.isUserRegistered = false;
        this.isAdmin = false;
        this.cdr.detectChanges();
      }
    });
    this.cdr.detectChanges();
  }
}
