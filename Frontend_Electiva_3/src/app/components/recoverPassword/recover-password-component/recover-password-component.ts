import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { PersonasService } from '../../../services/personas/personas-service';
import { Observable, catchError, map, of } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';
import { Persona } from '../../../models/persona';

@Component({
  selector: 'app-recover-password-component',
  imports: [CommonModule, FormsModule],
  templateUrl: './recover-password-component.html',
  styleUrl: './recover-password-component.scss'
})
export class RecoverPasswordComponent {
  // Form fields
  email = ""
  nuevaPassword = ""
  confirmarPassword = ""
  persona: Persona | null = null


  // State management
  emailVerificado = false
  verificandoEmail = false

  // Message system
  mostrarMensaje = false
  mensaje = ""
  tipoMensaje: "exito" | "error" | "info" = "info"

  constructor(private router: Router, private personaService: PersonasService,
    private cdr: ChangeDetectorRef
  ) { }

  /**
   * Verifica si el email existe en el sistema
   */
  verificarEmail(): void {
    if (!this.email) {
      this.mostrarMensajeFlotante("Por favor ingresa un correo electrónico", "error")
      return
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(this.email)) {
      this.mostrarMensajeFlotante("Por favor ingresa un correo electrónico válido", "error")
      return
    }
    this.verificandoEmail = true
    this.verificarEmailEnSistema$(this.email).subscribe(existe => {
      if (existe) {
        this.emailVerificado = true;
        this.cdr.detectChanges()
      } else {
        console.log("El email no fue encontrado o hubo un error.");
        // Haz algo si no existe...
      }
    });
  }


  private verificarEmailEnSistema$(email: string): Observable<boolean> {
    return this.personaService.getPersonaByEmail(email).pipe(
      map(persona => {
        // 'map' transforma el resultado (Persona) en un booleano
        if (persona) {
          this.persona = persona;
          return true; // El email existe
        } else {
          // El email no existe, mostramos el mensaje y devolvemos false
          this.mostrarMensajeFlotante("El correo electrónico no está registrado en el sistema", "error");
          return false;
        }
      }),
      catchError((error) => {
        // Manejar el caso en que el servicio falle (ej. error 500)
        this.mostrarMensajeFlotante("Error al verificar el correo", "error");
        // 'of' devuelve un nuevo Observable con el valor false
        return of(false);
      })
    );
  }


  /**
   * Cambia la contraseña del usuario
   */
  cambiarContrasena(): void {
    // Validar que las contraseñas no estén vacías
    if (!this.nuevaPassword || !this.confirmarPassword) {
      this.mostrarMensajeFlotante("Por favor completa todos los campos", "error")
      return
    }
    // Validar que las contraseñas coincidan
    if (this.nuevaPassword !== this.confirmarPassword) {
      this.mostrarMensajeFlotante("Las contraseñas no coinciden", "error")
      return
    }
    // Validar longitud mínima de contraseña
    if (this.nuevaPassword.length < 6) {
      this.mostrarMensajeFlotante("La contraseña debe tener al menos 6 caracteres", "error")
      return
    }
    if(this.persona){
      this.personaService.updatePassword(this.persona, this.nuevaPassword).subscribe({
        next: () => {
          this.mostrarMensajeFlotante("Contraseña cambiada exitosamente", "exito")
          this.resetearFormulario()
          this.router.navigate(['/login'])
        },
        error: () => {
          this.mostrarMensajeFlotante("Error al cambiar la contraseña", "error")
        }
      })
    }
  }

  /**
   * Muestra un mensaje flotante temporal
   */
  private mostrarMensajeFlotante(mensaje: string, tipo: "exito" | "error" | "info"): void {
    this.mensaje = mensaje
    this.tipoMensaje = tipo
    this.mostrarMensaje = true
    // Ocultar mensaje después de 4 segundos
    setTimeout(() => {
      this.mostrarMensaje = false
    }, 4000)
  }

  /**
   * Resetea el formulario
   */
  resetearFormulario(): void {
    this.email = ""
    this.nuevaPassword = ""
    this.confirmarPassword = ""
    this.emailVerificado = false
    this.verificandoEmail = false
  }
}
