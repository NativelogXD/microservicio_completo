import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Mantenimiento } from '../../models/mantenimiento';

@Injectable({
  providedIn: 'root'
})
export class MantenimientoService {
  private readonly Base_Url = 'http://localhost:8080/ServiceMantenimiento/api/empleados'

  constructor(private http: HttpClient) { }

  allMantenimientos():Observable<Mantenimiento[]>{
    return this.http.get<Mantenimiento[]>(`${this.Base_Url}`, {withCredentials: true})
  }
}
