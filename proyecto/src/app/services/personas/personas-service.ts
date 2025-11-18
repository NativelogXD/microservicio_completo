import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Persona } from '../../models/persona';
import { loginRequest } from '../../models/loginRequest';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PersonasService {
  private readonly baseUrl = 'http://localhost:8080/ServiceUsuario/api/personas'

  constructor(private http: HttpClient){}

  autentificate(prop: loginRequest): Observable<Persona> {
    return this.http.post<Persona>(`${this.baseUrl}/login`, prop, {
      withCredentials: true
    })
  }

  updatePersona(propr: Persona): Observable<Persona>{
    return this.http.put<Persona>(`${this.baseUrl}/update/${propr.id}`, propr, {
      withCredentials: true
    })
  }
  
  getPersonaByEmail(email: string): Observable<Persona> {
    return this.http.get<Persona>(`${this.baseUrl}/email/${email}`, {
      withCredentials: true
    })
  }

  updatePassword(prop: Persona, password: string):Observable<Persona>{
    return this.http.patch<Persona>(`${this.baseUrl}/updatePassword/${prop.id}`, {password})
  }
}
