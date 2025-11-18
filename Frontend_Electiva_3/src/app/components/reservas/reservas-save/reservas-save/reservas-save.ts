import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Reserva } from '../../../../models/reserva';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-reservas-save',
  imports: [FormsModule,CommonModule],
  templateUrl: './reservas-save.html',
  styleUrl: './reservas-save.scss'
})
export class ReservasSave {
  @Input() isOpen = false
  // 🔹 NUEVO INPUT: Recibe la reserva pre-inicializada desde el componente padre
  @Input() reservaToEdit: Reserva | null = null;
  
  @Output() onClose = new EventEmitter<void>()
  @Output() onSave = new EventEmitter<Reserva>()

  listaVuelos: any[] = []; // Asumo que esta lista se llenará con datos del microservicio

  // 🔹 Variable local para el formulario, inicializada con un valor por defecto
  reserva: Reserva = {
    id: null,
    usuario: "",
    vuelo: "",
    estado: "",
    numasiento: ""
  }

  ngOnInit(): void {
    // 🔹 Al inicializar, si se recibe una reserva, la usamos para el formulario
    if (this.reservaToEdit) {
      // Clonamos el objeto para evitar modificar el objeto original del padre
      this.reserva = { ...this.reservaToEdit };
    }
    console.log(this.reserva);
  }

  closeModal(): void {
    this.onClose.emit();
  }

  saveReserva(): void {
    // 🔹 Emitimos la reserva con los datos del formulario
    this.onSave.emit(this.reserva);
  }
}
