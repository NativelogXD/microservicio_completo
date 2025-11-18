import { Component } from '@angular/core';
import { Persona } from '../../../models/persona';
import { AuthService } from '../../../services/auth/auth-service';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { ReservasEdit } from '../reservas-edit/reservas-edit/reservas-edit';
import { Reserva } from '../../../models/reserva';
import { ReservaService } from '../../../services/reservas/reserva-service';


@Component({
  selector: 'app-reservas-component',
  imports: [CommonModule, ReservasEdit],
  templateUrl: './reservas-component.html',
  styleUrl: './reservas-component.scss'
})
export class ReservasComponent {

  constructor(private authService: AuthService,
    private cdr: ChangeDetectorRef,
    private reservaService: ReservaService
  ){}

  isUserMenuOpen = false
  usuario: Persona|null = null
  isAdmin = false
  isUserRegistered = false
  reservas: Reserva[] = [];
  reservasFiltradas: Reserva[] = [];

  // Estadísticas
  totalReservas: number = 0;
  reservasCompletadas: number = 0;
  reservasCanceladas: number = 0;

  // Gráficos
  estados: any[] = []; // Pie chart
  vuelos: any[] = [];  // Bar chart

  // Modales
  mostrarModalReserva: boolean = false;
  mostrarModalEditarReserva: boolean = false;
  reservaSeleccionada: Reserva | null = null;


  /**
  **
   * Funcion para mostrar o ocultar los objetos en el menu
   */
  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen
  }

  /**
   * Funcion para redirigir el usuario al login
   */
  handleLogin(): void {
    window.location.href = '/login'
  }

  /**
   * Funcion para redirigir el usuario al registro
   */
  handleRegister(): void {
    window.location.href = '/register'
  }

  handleEditProfile(): void {
    window.location.href = '/edit'
  }



  ngOnInit(): void {
    this.authService.getUsuarioActual().subscribe({
      next: usuario => {
        this.usuario = usuario;
        this.isUserRegistered = !!usuario;
        this.isAdmin = usuario?.rol === 'Admin';
        this.cargarReservas();
        this.cdr.detectChanges();
      },
      error: err => {
        // Por ejemplo, si no hay token o el usuario no está autenticado
        this.usuario = null;
        this.isUserRegistered = false;
        this.isAdmin = false;
        this.cdr.detectChanges();
      }
    });
  }

  /** Cargar reservas del usuario actual */
  cargarReservas(): void {
    this.reservaService.getReservas().subscribe((data: Reserva[]) => {
      this.reservas = data;
      // IMPORTANTE: Filtrar por nombre de usuario.
      // Sería mejor si el backend filtrara por ID de usuario.
      this.reservasFiltradas = this.reservas.filter(
        r => r.usuario === this.usuario?.email
      );

      this.actualizarEstadisticas();
      this.generarDatosGraficos();
      this.cdr.detectChanges(); // Forzar detección de cambios
    });
  }

  /** Estadísticas simples */
  actualizarEstadisticas(): void {
    this.totalReservas = this.reservasFiltradas.length;
    this.reservasCompletadas = this.reservasFiltradas.filter(r => r.estado.toLowerCase() === 'confirmada').length;
    this.reservasCanceladas = this.reservasFiltradas.filter(r => r.estado.toLowerCase() === 'cancelada').length;
  }

  /** Datos gráficos */
  generarDatosGraficos(): void {
    // Evitar división por cero si no hay reservas
    if (this.totalReservas === 0) {
      this.estados = [];
      this.vuelos = [];
      return;
    }
    
    // Pie chart por estado
    const estadosMap: any = {};
    this.reservasFiltradas.forEach(r => {
      if (!estadosMap[r.estado]) estadosMap[r.estado] = 0;
      estadosMap[r.estado]++;
    });

    this.estados = Object.keys(estadosMap).map((key) => ({
      name: key,
      count: estadosMap[key],
      percentage: (estadosMap[key] / this.totalReservas) * 100,
      color: this.getColorByEstado(key)
    }));

    // Bar chart por vuelo
    const vuelosMap: any = {};
    this.reservasFiltradas.forEach(r => {
      if (!vuelosMap[r.vuelo]) vuelosMap[r.vuelo] = 0;
      vuelosMap[r.vuelo]++;
    });

    this.vuelos = Object.keys(vuelosMap).map(key => ({
      name: key,
      reservasCount: vuelosMap[key],
      reservasPorcentaje: (vuelosMap[key] / this.totalReservas) * 100,
      color: this.getRandomColor()
    }));
  }

  /** Pie chart: offset */
  getCumulativePercentageEstado(index: number): number {
    let sum = 0;
    for (let i = 0; i < index; i++) {
      sum += this.estados[i].percentage;
    }
    return sum;
  }

  /** Colores por estado */
  getColorByEstado(estado: string): string {
    switch (estado.toLowerCase()) {
      case 'confirmada': return '#28a745';
      case 'pendiente': return '#ffc107';
      case 'cancelada': return '#dc3545';
      default: return '#6c757d';
    }
  }

  /** Color random para vuelos */
  getRandomColor(): string {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

  /** Modales */
  openModalReserva(): void { this.mostrarModalReserva = true; }
  cerrarModalReserva(): void { this.mostrarModalReserva = false; }

  abrirEditarReserva(reserva: Reserva): void {
    this.reservaSeleccionada = { ...reserva }; // Clonar el objeto para evitar mutaciones
    this.mostrarModalEditarReserva = true;
  }
  cerrarModalEditarReserva(): void {
    this.reservaSeleccionada = null;
    this.mostrarModalEditarReserva = false;
  }

  actualizarReserva(reservaEditada: Reserva): void {
    this.reservaService.editarReserva(reservaEditada)
      .subscribe(() => this.cargarReservas());
    this.cerrarModalEditarReserva();
  }

  eliminarReserva(reserva: Reserva): void {
    if (confirm('¿Deseas eliminar esta reserva?')) {
      this.reservaService.eliminarReserva(reserva.id!)
        .subscribe(() => this.cargarReservas());
    }
  }
}
