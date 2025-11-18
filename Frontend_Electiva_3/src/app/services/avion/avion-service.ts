import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Avion } from '../../models/avion';

@Injectable({
  providedIn: 'root'
})
export class AvionService {
  private readonly baseUrl = "http://localhost:8080/ServiceAvion/aviones"

  constructor(private http: HttpClient){}

  getAll():Observable<Avion[]>{
    return this.http.get<Avion[]>(`${this.baseUrl}/`, {withCredentials: true})
  }

  saveAvion(prop: Avion):Observable<Avion>{
    return this.http.post<Avion>(`${this.baseUrl}/`, prop, {withCredentials: true} )
  }

  updateAvion(prop: Avion):Observable<Avion>{
    return this.http.put<Avion>(`${this.baseUrl}/${prop.id}`, prop, {withCredentials: true})
  }

  deleteAvion(prop:number):Observable<Avion>{
    return this.http.delete<Avion>(`${this.baseUrl}/${prop}`, {withCredentials: true})
  }
}
