import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { Vuelo } from '../../../../models/vuelo';
import { EmpleadosService } from '../../../../services/empleados/empleados-service';
import { AvionService } from '../../../../services/avion/avion-service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-vuelos-edit',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './vuelos-edit.html',
  styleUrl: './vuelos-edit.scss'
})
export class VuelosEdit implements OnInit, OnChanges {

  @Input() isOpen = false
  @Input() vueloToEdit!: Vuelo | null
  @Output() onSave = new EventEmitter<Vuelo>()
  @Output() onClose = new EventEmitter<void>()

  vuelo: Vuelo = {
    id: null,
    codigoVuelo: "",
    origen: "",
    destino: "",
    avionId: "",
    pilotoId: "",
    fecha: new Date(),
    hora: new Date(),
    duracionMinutos: 0,
    estado: "",
    precioBase: 0
  }

  listEmpleados: any[] = []
  listAviones: any[] = []

  constructor(private serviceEmpleado: EmpleadosService,
    private serviceAvion: AvionService) { }

  ngOnInit(): void {
    this.loadEmpleados()
    this.loadAviones()
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(changes["vueloToEdit"] && this.vueloToEdit){
      this.vuelo = {...this.vueloToEdit}
    }
  }

  loadEmpleados() {
    this.serviceEmpleado.allEmpleados().subscribe({
      next: (response: any[]) => {
        this.listEmpleados = response.filter(emp => emp.cargo === 'Piloto')
      },
      error: () => { }
    })
  }

  loadAviones() {
    this.serviceAvion.getAll().subscribe({
      next: (response: any[]) => {
        this.listAviones = response.filter(emp => emp.estado === 'disponible')
      },
      error: () => { }
    })
  }

  saveAvion(): void {
    if (this.isFormValid()) {
      this.onSave.emit({ ...this.vuelo })
      this.closeModal()
    }
  }


  closeModal(): void {
    this.resetForm()
    this.onClose.emit()
  }

  private isFormValid(): boolean {
    return !!(
      this.vuelo.codigoVuelo &&
      this.vuelo.origen &&
      this.vuelo.destino &&
      this.vuelo.avionId &&
      this.vuelo.pilotoId &&
      this.vuelo.fecha &&
      this.vuelo.hora &&
      this.vuelo.duracionMinutos > 0 &&
      this.vuelo.estado &&
      this.vuelo.precioBase > 0
    )
  }

  private resetForm(): void {
    this.vuelo = {
      id: null,
      codigoVuelo: "",
      origen: "",
      destino: "",
      avionId: "",
      pilotoId: "",
      fecha: new Date(),
      hora: new Date(),
      duracionMinutos: 0,
      estado: "",
      precioBase: 0
    }
  }

}
