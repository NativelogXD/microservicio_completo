import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PersonasService } from '../../../services/personas/personas-service';
import { Router } from '@angular/router';
import { loginRequest } from '../../../models/loginRequest';
import { ChangeDetectorRef } from '@angular/core';
import { AuthService } from '../../../services/auth/auth-service';

@Component({
  selector: 'app-login-component',
  imports: [CommonModule, FormsModule],
  templateUrl: './login-component.html',
  styleUrl: './login-component.scss'
})
export class LoginComponent {

  loginRequest: loginRequest|null = null
  email = ""
  password = ""
  rememberMe = false
  videoUrl = 'video.mp4'
  mensaje: string = '';
  tipoMensaje: 'success' | 'error' | '' = '';
  mostrarMensaje = false;

  constructor(private personaService: PersonasService,
    private route: Router,
    private cd: ChangeDetectorRef,
    private authSerive: AuthService
  ){}

  loggin(email:string, password:string){
    this.loginRequest = {
      email: email,
      password: password
    }
    this.personaService.autentificate(this.loginRequest).subscribe({
      next: (data) => {
          this.mensaje = 'Bienvenido ' + `${data.nombre}`
          this.tipoMensaje = 'success'
          this.mostrarMensaje = true
          this.cd.detectChanges()
          setTimeout(() => {
            this.mostrarMensaje = false;
            this.cd.detectChanges()
            setTimeout(() => this.onHome(), 500); // Navega después de que el mensaje se oculte
          }, 3000)
      },
      error: (error) => {
          this.mensaje = `Error al iniciar sesión, ${error.error.mensaje}`
          this.tipoMensaje = 'error'
          this.mostrarMensaje = true
          this.cd.detectChanges()
          setTimeout(() => this.mostrarMensaje = false, 3000)
      }
    })
  }

  onHome(){
    this.route.navigate(['/'])
  }
}
