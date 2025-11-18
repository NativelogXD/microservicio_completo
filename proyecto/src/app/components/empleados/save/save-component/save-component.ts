import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Empleado } from '../../../../models/empleado';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-save-component',
  imports: [CommonModule, FormsModule],
  standalone: true,
  templateUrl: './save-component.html',
  styleUrl: './save-component.scss'
})
export class SaveComponent {

  @Input() isOpen = false
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

  onSubmit(): void {
    // Validar que todos los campos requeridos estén llenos
    if (this.isFormValid()) {
      console.log(this.empleado)
      this.onSave.emit(this.empleado)
      this.resetForm()
    }
  }

  onCancel(): void {
    this.resetForm()
    this.onClose.emit()
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
