import { Component, EventEmitter, Input, Output, OnChanges, SimpleChanges } from '@angular/core';
import { Reserva } from '../../../../models/reserva';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Pago } from '../../../../models/pago';
import { EstadoPago } from '../../../../models/enums/estadoPago';
import { MetodoPago } from '../../../../models/enums/MetodoPago';

interface ReservaYPago{
  reserva: Reserva,
  pago: Pago
}

@Component({
  selector: 'app-reservas-save',
  imports: [FormsModule,CommonModule],
  templateUrl: './reservas-save.html',
  styleUrl: './reservas-save.scss'
})

export class ReservasSave implements OnChanges {
  @Input() isOpen = false
  // 🔹 NUEVO INPUT: Recibe la reserva pre-inicializada desde el componente padre
  @Input() reservaToEdit: Reserva | null = null;
  @Input() pagoToEdit: Pago | null = null;
  
  @Output() onClose = new EventEmitter<void>()
  @Output() onSave = new EventEmitter<ReservaYPago>()

  listaVuelos: any[] = []; // Asumo que esta lista se llenará con datos del microservicio

  // 🔹 Variable local para el formulario, inicializada con un valor por defecto
  reserva: Reserva = {
    id: null,
    usuario: "",
    vuelo: "",
    estado: "",
    numasiento: ""
  }

  pago: Pago = {
    id: null,
    monto: 0,
    fecha: new Date(),
    estado: EstadoPago.PENDIENTE,
    moneda: "",
    metodo_pago: MetodoPago.TRANSFERENCIA,
    reserva: "",
    usuario: ""
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['reservaToEdit'] && this.reservaToEdit) {
      console.log(this.reservaToEdit)
      this.reserva = { ...this.reservaToEdit };
    }
    if (changes['pagoToEdit'] && this.pagoToEdit) {
      console.log(this.pagoToEdit)
      this.pago = { ...this.pagoToEdit };
    }
  }

  closeModal(): void {
    this.onClose.emit();
  }

  saveReserva(): void {
    // 🔹 Emitimos la reserva con los datos del formulario
    this.onSave.emit({reserva: this.reserva, pago: this.pago});
  }
}
