import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule, TitleCasePipe, DatePipe } from '@angular/common';
import { Persona } from '../../../../models/persona';
import { AvionSave } from '../../save/avion-save/avion-save';
import { AvionEdit } from '../../edit/avion-edit/avion-edit';
import { Avion } from '../../../../models/avion';
import { EstadoAvion } from '../../../../models/enums/estadoAvion';
import { AuthService } from '../../../../services/auth/auth-service';
import { AvionService } from '../../../../services/avion/avion-service';
import { error } from 'console';

// Definición de tipos para los datos de los gráficos (asumiendo una estructura)
interface ChartData {
  name: string;
  percentage: number;
  color: string;
  count?: number;
}

@Component({
  selector: 'app-avion-list',
  imports: [CommonModule, AvionSave, AvionEdit, TitleCasePipe, DatePipe],
  templateUrl: './avion-list.html',
  styleUrl: './avion-list.scss',
  standalone: true // Asumo que es un componente standalone por la estructura de imports
})
export class AvionList implements OnInit {
  // Atributos de usuario y menú
  usuario: Persona | null = null
  isUserMenuOpen = false
  isAdmin = false
  isUserRegistered = false

  // Atributos de datos y estadísticas
  aviones: Avion[] = []; // Lista de aviones para la tabla
  totalAviones = 0
  avionesDisponibles = 0
  avionesMantenimiento = 0

  // Atributos para gráficos (inicializados con tipos)
  aerolineas: ChartData[] = []; // Datos para el gráfico circular
  modelos: ChartData[] = []; // Datos para el gráfico de barras

  // Atributos de control de modales
  mostrarModal: boolean = false;
  mostrarModalEditar: boolean = false;
  avionSeleccionado: Avion | null = null;

  // Paleta de colores para asignación dinámica
  private colorPalette: string[] = [
    '#3b82f6', // Azul
    '#10b981', // Verde
    '#8b5cf6', // Púrpura
    '#f59e0b', // Amarillo
    '#ef4444', // Rojo
    '#06b6d4', // Cian
    '#f472b6', // Rosa
    '#a855f7', // Violeta
  ];

  constructor(private authService: AuthService,
    private cdr: ChangeDetectorRef,
    private avionService: AvionService
  ) { }

  ngOnInit(): void {
    // Usuario actual
    this.authService.getUsuarioActual().subscribe({
      next: usuario => {
        this.usuario = usuario
        this.isUserRegistered = !!usuario
        this.isAdmin = usuario?.rol === 'Admin'
        this.cdr.detectChanges()
      },
      error: () => {
        this.usuario = null
        this.isUserRegistered = false
        this.isAdmin = false
        this.cdr.detectChanges()
      }
    })
    // Cargar empleados
    this.loadAviones()
  }

  loadAviones() {
    this.avionService.getAll().subscribe({
      next: (response: Avion[]) => {
        this.aviones = response
        this.cargarDatosAviones();
        this.cdr.detectChanges()
      }
    })
  }


  // Mapa para mantener la consistencia de colores por nombre
  private dynamicColorMap: { [key: string]: string } = {};

  // Método para obtener un color consistente para un nombre dado
  private getColorForName(name: string): string {
    if (!this.dynamicColorMap[name]) {
      // Usar un hash simple para asignar un color de la paleta de forma consistente
      let hash = 0;
      for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
      }
      const index = Math.abs(hash) % this.colorPalette.length;
      this.dynamicColorMap[name] = this.colorPalette[index];
    }
    return this.dynamicColorMap[name];
  }

  // Métodos de control de menú
  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen
  }

  handleLogin(): void { window.location.href = "/login" }
  handleRegister(): void { window.location.href = "/register" }
  handleProfile(): void { window.location.href = "/edit" }

  // Métodos de control de modales
  openModal(): void {
    this.mostrarModal = true;
  }

  cerrarModal(): void {
    this.mostrarModal = false;
  }

  guardarAvion(avion: Avion) {
    console.log(avion)
    this.avionService.saveAvion(avion).subscribe({
      next: () => {
        alert("Avion guardado correctamente")
        this.cerrarModal();
        this.cargarDatosAviones();
      },
      error: () => alert("Error al guardar el avion")
    })
  }

  editarAvion(avion: Avion): void {
    this.avionSeleccionado = avion;
    this.mostrarModalEditar = true;
  }

  cerrarModalEditar(): void {
    this.mostrarModalEditar = false;
    this.avionSeleccionado = null;
  }

  actualizarAvion(avion: Avion): void {
    if(!avion.id){
      alert("Error: el avion no tiene un ID valido para actualizar")
      return
    }
    this.avionService.updateAvion(avion).subscribe({
      next: () => {
        alert("Avion actualizado correctamente")
        this.cerrarModalEditar();
        this.cargarDatosAviones(); // Recargar datos después de actualizar
        this.cdr.detectChanges();
      },
      error: () => alert("Error al actualizar avion")
    })
    this.cdr.detectChanges();
  }

  eliminarAvion(avion: Avion): void {
    if(confirm(`¿Estas seguro de eliminar a ${avion.modelo} ${avion.aerolinea}?`)){
      this.avionService.deleteAvion(avion.id!).subscribe({
        next: () => {
          alert("Avion eliminado exitosamente")
          this.cargarDatosAviones(); // Recargar datos después de eliminar
          this.cdr.detectChanges()
        }
      })
    }
    this.cargarDatosAviones(); // Recargar datos después de eliminar
    this.cdr.detectChanges()
  }

  // Método para el gráfico circular (pie chart)
  getCumulativePercentage(index: number): number {
    if (index === 0) {
      return 0;
    }
    // Lógica para calcular el porcentaje acumulado
    let cumulative = 0;
    for (let i = 0; i < index; i++) {
      cumulative += this.aerolineas[i].percentage;
    }
    return cumulative;
  }

  cargarDatosAviones(): void {

    // 2. Cálculo de estadísticas principales
    this.totalAviones = this.aviones.length;
    this.avionesDisponibles = this.aviones.filter(a => a.estado === EstadoAvion.disponible).length;
    this.avionesMantenimiento = this.aviones.filter(a => a.estado === EstadoAvion.mantenimiento).length;

    // 3. Cálculo dinámico para Aerolíneas (Gráfico Circular)
    const aerolineaCounts = this.aviones.reduce((acc, avion) => {
      acc[avion.aerolinea] = (acc[avion.aerolinea] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });

    this.aerolineas = Object.keys(aerolineaCounts).map(name => {
      const count = aerolineaCounts[name];
      const percentage = (count / this.totalAviones) * 100;
      return {
        name,
        percentage: parseFloat(percentage.toFixed(2)),
        color: this.getColorForName(name), // Asignación dinámica de color
        count
      };
    });

    // 4. Cálculo dinámico para Modelos (Gráfico de Barras)
    const modeloCounts = this.aviones.reduce((acc, avion) => {
      acc[avion.modelo] = (acc[avion.modelo] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });

    this.modelos = Object.keys(modeloCounts).map(name => {
      const count = modeloCounts[name];
      const percentage = (count / this.totalAviones) * 100;
      return {
        name,
        percentage: parseFloat(percentage.toFixed(2)),
        color: this.getColorForName(name), // Asignación dinámica de color
        count
      };
    });
  }
}

