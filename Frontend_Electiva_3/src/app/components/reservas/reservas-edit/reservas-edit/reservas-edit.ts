import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Reserva } from '../../../../models/reserva';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-reservas-edit',
  imports: [FormsModule,CommonModule],
  templateUrl: './reservas-edit.html',
  styleUrl: './reservas-edit.scss'
})
export class ReservasEdit {
  @Input() isOpen = false
  @Input() reservaToEdit!: Reserva | null
  @Output() onClose = new EventEmitter<void>()
  @Output() onSave = new EventEmitter<Reserva>()
}
