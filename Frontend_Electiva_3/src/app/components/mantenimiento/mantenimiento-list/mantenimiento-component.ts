import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Mantenimiento } from '../../../models/mantenimiento';
import { EstadoMantenimiento } from '../../../models/enums/estadoMantenimiento';
import { Persona } from '../../../models/persona';
import { AuthService } from '../../../services/auth/auth-service';
import { MantenimientoService } from '../../../services/mantenimiento/mantenimiento-service';

interface Estado {
  name: string;
  color: string;
  percentage: number;
  count: number;
}

interface Tipo {
  name: string;
  color: string;
  percentage: number;
  count: number;
}

@Component({
  selector: 'app-mantenimiento',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mantenimiento-component.html',
  styleUrl: './mantenimiento-component.scss'
})
export class MantenimientoComponent implements OnInit {
  // Variables de usuario
  usuario: Persona | null = null
  isUserMenuOpen = false
  isAdmin = false
  isUserRegistered = false

  // Variables de datos
  mantenimientos: Mantenimiento[] = [];
  mantenimientoSeleccionado: Mantenimiento | null = null;

  // Variables de estadísticas
  totalMantenimientos = 0;
  mantenimientosCompletados = 0;
  mantenimientosEnProgreso = 0;
  costoTotal = 0;

  estados: Estado[] = [];
  tipos: Tipo[] = [];

  // Variables de modales
  mostrarModal = false;
  mostrarModalEditar = false;
  EstadoMantenimiento = EstadoMantenimiento;

  constructor(private authService: AuthService,
    private cdr: ChangeDetectorRef,
    private mantenimientoService: MantenimientoService
  ) { }

  ngOnInit(): void {
    this.authService.getUsuarioActual().subscribe({
      next: usuario => {
        this.usuario = usuario
        this.isUserRegistered = !!usuario;
        this.isAdmin = usuario?.rol == 'Admin'
        this.cdr.detectChanges()
      },
      error: () => {
        this.usuario = null
        this.isUserRegistered = false
        this.isAdmin = false
        this.cdr.detectChanges()
      }
    })
  }

  // Cargar datos de ejemplo
  cargarDatos(): void {
    this.mantenimientoService.allMantenimientos().subscribe({
      next: (response: Mantenimiento[]) => {
        this.mantenimientos = response
        this.calcularEstadisticas();
        this.procesarDatosGraficos();
        this.cdr.detectChanges()
      }
    })
  }

  // Calcular estadísticas
  calcularEstadisticas(): void {
    this.totalMantenimientos = this.mantenimientos.length;

    this.mantenimientosCompletados = this.mantenimientos.filter(
      m => m.estado === EstadoMantenimiento.Completado
    ).length;

    this.mantenimientosEnProgreso = this.mantenimientos.filter(
      m => m.estado === EstadoMantenimiento.EnProceso
    ).length;

    this.costoTotal = this.mantenimientos.reduce((sum, m) => sum + m.costo, 0);
  }

  // Procesar datos para gráficos
  procesarDatosGraficos(): void {
    const estadoMap = new Map<string, number>();
    this.mantenimientos.forEach(m => {
      estadoMap.set(m.estado, (estadoMap.get(m.estado) || 0) + 1);
    });

    this.estados = [
      {
        name: 'Completado',
        color: '#10b981',
        percentage: this.totalMantenimientos > 0
          ? ((estadoMap.get(EstadoMantenimiento.Completado) || 0) / this.totalMantenimientos * 100)
          : 0,
        count: estadoMap.get(EstadoMantenimiento.Completado) || 0
      },
      {
        name: 'En Proceso',
        color: '#f59e0b',
        percentage: this.totalMantenimientos > 0
          ? ((estadoMap.get(EstadoMantenimiento.EnProceso) || 0) / this.totalMantenimientos * 100)
          : 0,
        count: estadoMap.get(EstadoMantenimiento.EnProceso) || 0
      },
      {
        name: 'Pendiente',
        color: '#3b82f6',
        percentage: this.totalMantenimientos > 0
          ? ((estadoMap.get(EstadoMantenimiento.Pendiente) || 0) / this.totalMantenimientos * 100)
          : 0,
        count: estadoMap.get(EstadoMantenimiento.Pendiente) || 0
      }
    ];

    const tipoMap = new Map<string, number>();
    this.mantenimientos.forEach(m => {
      tipoMap.set(m.tipo, (tipoMap.get(m.tipo) || 0) + 1);
    });

    this.tipos = [
      {
        name: 'Preventivo',
        color: '#3b82f6',
        percentage: this.totalMantenimientos > 0
          ? ((tipoMap.get('Preventivo') || 0) / this.totalMantenimientos * 100)
          : 0,
        count: tipoMap.get('Preventivo') || 0
      },
      {
        name: 'Correctivo',
        color: '#8b5cf6',
        percentage: this.totalMantenimientos > 0
          ? ((tipoMap.get('Correctivo') || 0) / this.totalMantenimientos * 100)
          : 0,
        count: tipoMap.get('Correctivo') || 0
      }
    ];
  }

  // Calcular porcentaje acumulado para el gráfico de pastel
  getCumulativePercentage(index: number): number {
    return this.estados.slice(0, index).reduce((sum, e) => sum + e.percentage, 0);
  }

  // Alternar menú de usuario
  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen;
  }

  // Manejo de eventos del menú de usuario
  handleLogin(): void { window.location.href = "/login" }
  handleRegister(): void { window.location.href = "/register" }
  handleProfile(): void { window.location.href = "/edit" }

  // Modales
  openModal(): void {
    this.mostrarModal = true;
  }

  cerrarModal(): void {
    this.mostrarModal = false;
  }

  cerrarModalEditar(): void {
    this.mostrarModalEditar = false;
    this.mantenimientoSeleccionado = null;
  }

  // Operaciones CRUD
  guardarMantenimiento(nuevoMantenimiento: Mantenimiento): void {
    const maxId = Math.max(...this.mantenimientos.map(m => m.id || 0), 0);
    nuevoMantenimiento.id = maxId + 1;
    this.mantenimientos.push(nuevoMantenimiento);
    this.calcularEstadisticas();
    this.procesarDatosGraficos();
    this.cerrarModal();
  }

  editarMantenimiento(mantenimiento: Mantenimiento): void {
    this.mantenimientoSeleccionado = { ...mantenimiento };
    this.mostrarModalEditar = true;
  }

  actualizarMantenimiento(mantenimientoActualizado: Mantenimiento): void {
    const index = this.mantenimientos.findIndex(m => m.id === mantenimientoActualizado.id);
    if (index !== -1) {
      this.mantenimientos[index] = mantenimientoActualizado;
      this.calcularEstadisticas();
      this.procesarDatosGraficos();
      this.cerrarModalEditar();
    }
  }

  eliminarMantenimiento(mantenimiento: Mantenimiento): void {
    if (confirm('¿Estás seguro de que deseas eliminar este mantenimiento?')) {
      this.mantenimientos = this.mantenimientos.filter(m => m.id !== mantenimiento.id);
      this.calcularEstadisticas();
      this.procesarDatosGraficos();
    }
  }
}
