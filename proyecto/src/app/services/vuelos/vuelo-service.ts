import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Vuelo } from '../../models/vuelo';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class VueloService {
  
  private readonly baseUrl = 'http://localhost:8080/ServiceVuelos/api/vuelos'

  constructor(private http: HttpClient){}

  getAllVuelos():Observable<Vuelo[]>{
    return this.http.get<Vuelo[]>(`${this.baseUrl}`, { withCredentials: true })
  }

  saveVuelo(prop:Vuelo):Observable<Vuelo>{
    return this.http.post<Vuelo>(`${this.baseUrl}`, prop, { withCredentials: true })
  }

  updateVuelo(prop:Vuelo):Observable<Vuelo>{
    return this.http.put<Vuelo>(`${this.baseUrl}/${prop.id}`, prop, { withCredentials: true })
  }

  deleteVuelo(id:number):Observable<void>{
    return this.http.delete<void>(`${this.baseUrl}/${id}`, { withCredentials: true })
  }
}
