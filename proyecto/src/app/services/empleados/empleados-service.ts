import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Empleado } from '../../models/empleado';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EmpleadosService {
  private readonly Base_Url = 'http://localhost:8080/ServiceUsuario/api/empleados'

  constructor(private http: HttpClient){}

  saveEmpleado(prop: Empleado):Observable<Empleado>{
    return this.http.post<Empleado>(`${this.Base_Url}/save`, prop, { withCredentials: true })
  }

  updateEmpleado(prop: Empleado):Observable<Empleado>{
    return this.http.put<Empleado>(`${this.Base_Url}/update/${prop.id}`, prop, { withCredentials: true })
  }

  deleteEmpleado(id: number):Observable<void>{
    return this.http.delete<void>(`${this.Base_Url}/delete/${id}`, { withCredentials: true })
  }

  allEmpleados():Observable<Empleado[]>{
    return this.http.get<Empleado[]>(`${this.Base_Url}/all`, { withCredentials: true })
  }

}
