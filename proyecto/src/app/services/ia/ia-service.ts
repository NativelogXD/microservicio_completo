import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class IaService {
  private readonly gatewayUrl = 'http://localhost:8080/AgentIA/query';

  constructor(private http: HttpClient) {}

  // Envía el mensaje del usuario al microservicio de IA vía API Gateway y devuelve el texto de respuesta
  sendMessage(message: string): Observable<string> {
    const payload = { consulta: message };  // coincide con lo que Flask espera
    return this.http.post<{ data: string }>(this.gatewayUrl, payload, { withCredentials: true })
      .pipe(
        map(res => res.data),
        catchError(errGateway => {
          console.error('[IaService] Error contra API Gateway.', errGateway);
          const userMessage = 'No se pudo conectar con el servicio de IA. Intenta nuevamente más tarde.';
          return throwError(() => ({ ...errGateway, userMessage }));
        })
      );
  }
}