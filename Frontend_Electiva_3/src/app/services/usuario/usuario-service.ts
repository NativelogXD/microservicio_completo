import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Usuario } from '../../models/usuario';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private readonly baseUrl = 'http://localhost:8080/ServiceUsuario/api/usuarios'

  constructor(private http: HttpClient){}

  saveUsuario(prop:Usuario):Observable<Usuario>{
    return this.http.post<Usuario>(`${this.baseUrl}/save`,prop)
  }
}
