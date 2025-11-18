import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { Reserva } from '../../../../models/reserva';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-reservas-edit',
  imports: [FormsModule, CommonModule],
  templateUrl: './reservas-edit.html',
  styleUrl: './reservas-edit.scss'
})

export class ReservasEdit implements OnChanges {
  @Input() isOpen = false
  @Input() reservaToEdit!: Reserva | null
  @Output() onClose = new EventEmitter<void>()
  @Output() onSave = new EventEmitter<Reserva>()

  reserva: Reserva = {
    id: null,
    usuario: "",
    vuelo: "",
    estado: "",
    numasiento: ""
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(changes["reservaToEdit"] && this.reservaToEdit){
      this.reserva = {...this.reservaToEdit}
    }
  }

  closeModal(): void {
    this.onClose.emit();
  }

  saveReserva(): void {
    this.onSave.emit(this.reserva);
  }
}
