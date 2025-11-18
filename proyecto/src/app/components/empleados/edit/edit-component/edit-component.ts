import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Empleado } from '../../../../models/empleado';
import { OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-edit-component',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-component.html',
  styleUrl: './edit-component.scss'
})
export class EditComponent implements OnChanges {
  @Input() isOpen = false
  @Input() empleadoToEdit!: Empleado | null
  @Output() onSave = new EventEmitter<Empleado>()
  @Output() onClose = new EventEmitter<void>()

  empleado: Empleado = {
    id: null,
    cedula: "",
    nombre: "",
    apellido: "",
    telefono: "",
    email: "",
    contrasenia: "",
    salario: 0,
    cargo: "",
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes["empleadoToEdit"] && this.empleadoToEdit) {
      this.empleado = { ...this.empleadoToEdit }
    }
  }

  saveEmpleado(): void {
    if (this.isFormValid()) {
      this.onSave.emit({ ...this.empleado })
      this.closeModal()
    }
  }

  closeModal(): void {
    this.onClose.emit()
    this.resetForm()
  }

  private isFormValid(): boolean {
    return !!(
      this.empleado.cedula &&
      this.empleado.nombre &&
      this.empleado.apellido &&
      this.empleado.telefono &&
      this.empleado.email &&
      this.empleado.cargo &&
      this.empleado.salario > 0 &&
      this.empleado.contrasenia
    )
  }

  private resetForm(): void {
    this.empleado = {
      id: null,
      cedula: "",
      nombre: "",
      apellido: "",
      telefono: "",
      email: "",
      contrasenia: "",
      salario: 0,
      cargo: "",
    }
  }
}
