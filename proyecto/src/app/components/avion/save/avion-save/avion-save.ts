import { CommonModule } from '@angular/common';
import { Component, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Avion } from '../../../../models/avion';
import { EventEmitter } from '@angular/core';
import { EstadoAvion } from '../../../../models/enums/estadoAvion';

@Component({
  selector: 'app-avion-save',
  imports: [CommonModule, FormsModule],
  templateUrl: './avion-save.html',
  styleUrl: './avion-save.scss'
})
export class AvionSave {

  @Input() isOpen = false
  @Output() onSave = new EventEmitter<Avion>();
  @Output() onClose = new EventEmitter<void>();

  avion: Avion = {
    id: null,
    modelo: "",
    capacidad: 0,
    aerolinea: "",
    estado: EstadoAvion.disponible,
    fecha_fabricacion: ""
  }

  onSubmit(): void {
    if(this.isFormValid()){
      this.onSave.emit(this.avion)
      this.resetForm()
    }
  }

  onCancel(): void {
    this.resetForm()
    this.onClose.emit()
  }

  private resetForm(): void {
    this.avion = {
      id: null,
      modelo: "",
      capacidad: 0,
      aerolinea: "",
      estado: EstadoAvion.disponible,
      fecha_fabricacion: ""
    }
  }

  private isFormValid(): boolean {
    return !!(
      this.avion.modelo &&
      this.avion.capacidad > 0 &&
      this.avion.aerolinea &&
      this.avion.fecha_fabricacion
    )
  }


}
