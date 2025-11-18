import { Injectable } from '@angular/core';
import { Reserva } from '../../models/reserva';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ReservaService {

  private readonly baseUrl = 'http://localhost:8080/ServiceReserva/api/reservas';

  
  constructor(private http: HttpClient) {}

  getReservas(): Observable<Reserva[]> {
    return this.http.get<Reserva[]>(`${this.baseUrl}`, { withCredentials: true });
  }

  crearReserva(reserva: Reserva): Observable<Reserva> {
    console.log(reserva);
    return this.http.post<Reserva>(`${this.baseUrl}`, reserva, {withCredentials: true});
  }


  editarReserva(reserva: Reserva): Observable<Reserva> {
    return this.http.put<Reserva>(`${this.baseUrl}/reservas/${reserva.id}`, reserva, {withCredentials: true});
  }

  eliminarReserva(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/reservas/${id}`,  {withCredentials: true});
  }
}
