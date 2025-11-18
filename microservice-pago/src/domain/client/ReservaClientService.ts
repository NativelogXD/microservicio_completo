import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { AxiosError } from 'axios';
import { firstValueFrom } from 'rxjs';

@Injectable()
export default class ReservaClientService {
  constructor(private readonly http: HttpService) {}

  private readonly baseUrl =
    process.env.RESERVAS_BASE_URL || 'http://localhost:8080/api/reservas';

  async existsById(id: string): Promise<boolean> {
    try {
      const url = `${this.baseUrl}/${encodeURIComponent(id)}`;
      const response = await firstValueFrom(this.http.get(url));
      return response.status === 200 && !!response.data;
    } catch (error) {
      const err = error as AxiosError;
      if (err.response && err.response.status === 404) {
        return false;
      }
      // Propaga otros errores (timeout, 5xx) al servicio llamante
      throw error;
    }
  }
}
