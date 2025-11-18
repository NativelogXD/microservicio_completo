import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Usuario } from '../../../models/usuario';
import { UsuarioService } from '../../../services/usuario/usuario-service';
import { Router} from '@angular/router';
import { ChangeDetectorRef } from '@angular/core';


@Component({
  selector: 'app-register-component',
  imports: [CommonModule, FormsModule],
  templateUrl: './register-component.html',
  styleUrl: './register-component.scss'
})
export class RegisterComponent {

  constructor(private serviceUsuario: UsuarioService,
    private router: Router,
    private cd: ChangeDetectorRef
  ){}

  usuario: Usuario|null = null
  cedula:string = ''
  nombre:string = ''
  apellido:string = ''
  telefono:string = ''
  email:string = ''
  direccion:string = ''
  password:string = ''
  confirmPassword:string = ''
  mensaje: string = '';
  tipoMensaje: 'success' | 'error' | '' = '';
  mostrarMensaje = false;

  addUsuario(cedula:string, nombre:string, apellido:string, telefono:string, email:string, direccion:string, password:string, confirmPassword:string){
    if(password == confirmPassword){
      this.usuario = {
        id: null,
        cedula: cedula,
        nombre: nombre,
        apellido: apellido,
        telefono: telefono,
        email: email,
        rol: 'Usuario',
        contrasenia: password,
        direccion: direccion,
        reservaId: ""
      }
      this.serviceUsuario.saveUsuario(this.usuario).subscribe({
        next: () => {
          this.mensaje = 'Usuario creado exitosamente'
          this.tipoMensaje = 'success'
          this.mostrarMensaje = true
          this.cd.detectChanges()
          setTimeout(() => {
            this.mostrarMensaje = false;
            this.cd.detectChanges()
            setTimeout(() => this.onLogin(), 500); // Navega después de que el mensaje se oculte
          }, 3000)
        },
        error: (error) => {
          this.mensaje = `Error al crear el usuario, ${error.error.mensaje}`
          this.tipoMensaje = 'error'
          this.mostrarMensaje = true
          this.cd.detectChanges()
          setTimeout(() => this.mostrarMensaje = false, 3000)
        }
      })
    } else {
      this.mensaje = 'Las contraseñas no coinciden'
      this.tipoMensaje = 'error'
      this.mostrarMensaje = true
      this.cd.detectChanges()
      setTimeout(() => this.mostrarMensaje = false, 3000)
    }
  }

  onLogin(){
    this.router.navigate(['/login'])
  }
}
