import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Pago } from '../../models/pago';

@Injectable({
  providedIn: 'root'
})
export class PagoService {
  
  private readonly baseUrl = 'http://localhost:8080/ServicePago'

  constructor(private http: HttpClient){}

  savePago(prop:Pago){
    return this.http.post<Pago>(`${this.baseUrl}/crear`, prop, { withCredentials: true })
  }
}
