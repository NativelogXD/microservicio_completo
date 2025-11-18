export class PagoNoEncontradoException extends Error {
  public readonly statusCode: number = 404;
  public readonly error: string = 'PAGO_NOT_FOUND';

  constructor(id: number) {
    super(`Pago con id ${id} no encontrado`);
    this.name = 'PagoNoEncontradoException';
  }
}
