import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Persona } from '../../../models/persona';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth/auth-service';
import { PersonasService } from '../../../services/personas/personas-service';

@Component({
  selector: 'app-edit-component',
  imports: [CommonModule, FormsModule],
  standalone: true,
  templateUrl: './edit-component.html',
  styleUrl: './edit-component.scss'
})
export class EditComponent implements OnInit {

  constructor(
    private authservice: AuthService,
    private cdr: ChangeDetectorRef,
    private personaService: PersonasService
  ) { }

  usuario: Persona | null = null;
  usuarioEdit: Persona | null = null;

  contraseniaActual = '';
  contraseniaNueva = '';
  contraseniaConfirmar = '';
  isUserMenuOpen = false;
  isAdmin = false

  ngOnInit(): void {
    this.authservice.getUsuarioActual().subscribe({
      next: (response) => {
        this.usuario = response;
        if (this.usuario.rol == 'Admin') {
          this.isAdmin = true;
          this.cdr.detectChanges();
        }
        // 👇 fuerza la actualización de la vista
        this.cdr.detectChanges();
      }
    });
  }

  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen;
  }

  guardarCambios(): void {
    const contraseniaNuevaVacia = !this.contraseniaNueva.trim();
    const contraseniaConfirmarVacia = !this.contraseniaConfirmar.trim();

    if (contraseniaNuevaVacia && contraseniaConfirmarVacia && this.usuario) {
      // 👇 Usar la misma instancia de usuario para mantener la clase original
      this.usuarioEdit = this.usuario;

      // 👇 Actualizar solo los campos que cambian
      this.usuarioEdit.nombre = this.usuario.nombre ?? '';
      this.usuarioEdit.apellido = this.usuario.apellido ?? '';
      this.usuarioEdit.telefono = this.usuario.telefono ?? '';
      this.usuarioEdit.email = this.usuario.email ?? '';
      this.usuarioEdit.contrasenia = this.usuario.contrasenia ?? '';

      console.log('Objeto a enviar:', this.usuarioEdit);

      this.personaService.updatePersona(this.usuarioEdit).subscribe({
        next: (response) => {
          this.usuario = response;
          window.location.href = '/';
        },
        error: (err) => {
          console.error('Error al actualizar:', err);
        }
      });
    }
  }




  cancelarCambios(): void {
    window.location.href = '/';
  }

  handleProfile(): void {
  }
}
