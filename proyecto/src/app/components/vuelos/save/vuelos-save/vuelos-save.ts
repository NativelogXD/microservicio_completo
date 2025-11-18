import { CommonModule} from '@angular/common';
import { Component, EventEmitter, Input, Output, OnInit  } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Vuelo } from '../../../../models/vuelo';
import { EmpleadosService } from '../../../../services/empleados/empleados-service';
import { AvionService } from '../../../../services/avion/avion-service';


@Component({
  selector: 'app-vuelos-save',
  imports: [CommonModule, FormsModule],
  templateUrl: './vuelos-save.html',
  styleUrl: './vuelos-save.scss'
})
export class VuelosSave implements OnInit{

  @Input() isOpen = false
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
    private serviceAvion: AvionService){}

  ngOnInit(): void {
    this.loadEmpleados()
    this.loadAviones()
  }

  loadEmpleados(){
    this.serviceEmpleado.allEmpleados().subscribe({
      next: (response: any[]) => {
        this.listEmpleados = response.filter(emp => emp.cargo === 'Piloto')
      },
      error: () => { }
    })
  }

  loadAviones(){
    this.serviceAvion.getAll().subscribe({
      next: (response: any[]) => {
        this.listAviones = response.filter(emp => emp.estado === 'disponible')
      },
      error: () => { }
    })
  }

  onSubmit(): void {
    if(this.isFormValid()){
      this.onSave.emit(this.vuelo)
      this.resetForm()
    }
  }

  onCancel(): void {
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
