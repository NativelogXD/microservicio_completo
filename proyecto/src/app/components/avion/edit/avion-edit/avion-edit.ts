import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Avion } from '../../../../models/avion';
import { EstadoAvion } from '../../../../models/enums/estadoAvion';

@Component({
  selector: 'app-avion-edit',
  imports: [CommonModule, FormsModule],
  templateUrl: './avion-edit.html',
  styleUrl: './avion-edit.scss'
})
export class AvionEdit implements OnChanges {

  @Input() isOpen = false
  @Input() avionToEdit!: Avion | null
  @Output() onSave = new EventEmitter<Avion>()
  @Output() onClose = new EventEmitter<void>()

  avion: Avion = {
    id: null,
    modelo: "",
    capacidad: 0,
    aerolinea: "",
    estado: EstadoAvion.disponible,
    fecha_fabricacion: ""
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(changes["avionToEdit"] && this.avionToEdit){
      this.avion = {...this.avionToEdit}
    }
  }

  saveAvion(): void {
    if (this.isFormValid()) {
      this.onSave.emit({...this.avion})
      this.closeModal()
    }
  }


  closeModal(): void {
    this.onClose.emit()
    this.resetForm()
  }

  private isFormValid(): boolean {
    return !!(
      this.avion.modelo &&
      this.avion.capacidad > 0 &&
      this.avion.aerolinea &&
      this.avion.fecha_fabricacion
    )
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
}
