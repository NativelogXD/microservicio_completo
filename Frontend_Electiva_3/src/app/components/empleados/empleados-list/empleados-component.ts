import { Component, OnInit, ChangeDetectorRef } from "@angular/core"
import { CommonModule } from "@angular/common"
import { AuthService } from "../../../services/auth/auth-service"
import { Empleado } from "../../../models/empleado"
import { Persona } from "../../../models/persona"
import { EmpleadosService } from "../../../services/empleados/empleados-service"
import { SaveComponent } from "../save/save-component/save-component"
import { EditComponent } from "../edit/edit-component/edit-component"


@Component({
  selector: "app-empleados-component",
  standalone: true,
  imports: [CommonModule, SaveComponent, EditComponent],
  templateUrl: "./empleados-component.html",
  styleUrls: ["./empleados-component.scss"],
})
export class EmpleadosComponent implements OnInit {
  // ============================
  // 🔐 Usuario y autenticación
  // ============================
  usuario: Persona | null = null
  isUserMenuOpen = false
  isAdmin = false
  isUserRegistered = false
  mostrarModal: boolean = false
  mostrarModalEditar: boolean = false
  empleadoSeleccionado: Empleado | null = null

  // ============================
  // 👩‍💼 Gestión de empleados
  // ============================
  empleados: Empleado[] = []

  // Estadísticas
  totalEmpleados = 0
  empleadosActivos = 0
  salarioPromedio = 0

  // Datos para gráficos
  cargos: { name: string; count: number; percentage: number; color: string }[] = []

  // ============================
  // 🎨 Configuración colores gráficos
  // ============================
  cargoColors = ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4", "#ec4899"]

  constructor(
    private authService: AuthService,
    private serviceEmpleado: EmpleadosService,
    private cdr: ChangeDetectorRef
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
    this.loadEmpleados()
    this.cdr.detectChanges()
  }

  // ============================
  // 🔽 Menú de usuario
  // ============================
  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen
  }

  handleLogin(): void { window.location.href = "/login" }
  handleRegister(): void { window.location.href = "/register" }
  handleProfile(): void { window.location.href = "/edit" }

  openModal() { this.mostrarModal = true }
  cerrarModal() { this.mostrarModal = false }

  openModalEditar() { this.mostrarModalEditar = true }
  cerrarModalEditar() { this.mostrarModalEditar = false }


  // ============================
  // 📊 Lógica de datos
  // ============================
  loadEmpleados() {
    this.serviceEmpleado.allEmpleados().subscribe({
      next: (response: Empleado[]) => {
        this.empleados = response
        this.calculateStatistics()
        this.calculateChartData()
        this.cdr.detectChanges()
      },
      error: () => { }
    })
  }

  calculateStatistics() {
    this.totalEmpleados = this.empleados.length
    this.empleadosActivos = this.empleados.length

    const totalSalarios = this.empleados.reduce((sum, emp) => sum + emp.salario, 0)
    this.salarioPromedio = this.totalEmpleados > 0 ? totalSalarios / this.totalEmpleados : 0
  }

  calculateChartData() {
    // Map para contar empleados por cargo
    const cargoMap = new Map<string, number>()
    this.empleados.forEach(emp => {
      const cargo = emp.cargo || 'Sin cargo'
      cargoMap.set(cargo, (cargoMap.get(cargo) || 0) + 1)
    })

    // Crear array con porcentaje y color
    this.cargos = Array.from(cargoMap.entries())
      .map(([name, count], index) => ({
        name,
        count,
        percentage: this.totalEmpleados > 0 ? Math.round((count / this.totalEmpleados) * 100) : 0,
        color: this.cargoColors[index % this.cargoColors.length]
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)
  }

  // Cálculo de offset para torta SVG
  getCumulativePercentage(index: number): number {
    let cumulative = 0
    for (let i = 0; i < index; i++) {
      cumulative += this.cargos[i].percentage
    }
    return cumulative
  }

  // ============================
  // ⚙️ CRUD Empleados
  // ============================
  guardarEmpleado(empleado: Empleado) {
    this.serviceEmpleado.saveEmpleado(empleado).subscribe({
      next: () => {
        alert('Empleado guardado correctamente')
        this.cerrarModal()
        this.loadEmpleados()
      },
      error: () => alert('Error al guardar el empleado')
    })
  }

  actualizarEmpleado(empleadoEditado: Empleado): void {
    if (!empleadoEditado.id) {
      alert("Error: el empleado no tiene un ID válido para actualizar.")
      return
    }
    this.serviceEmpleado.updateEmpleado(empleadoEditado).subscribe({
      next: () => {
        alert("Empleado actualizado correctamente")
        this.cerrarModalEditar()
        this.loadEmpleados()
      },
      error: () => alert("Error al actualizar el empleado")
    })
  }

  editarEmpleado(empleado: Empleado): void {
    this.empleadoSeleccionado = empleado
    this.openModalEditar()
  }


  eliminarEmpleado(empleado: Empleado) {
    if (confirm(`¿Está seguro de eliminar a ${empleado.nombre} ${empleado.apellido}?`)) {
      this.serviceEmpleado.deleteEmpleado(empleado.id!).subscribe({
        next: () => {
          this.loadEmpleados()
          alert("Empleado eliminado exitosamente");
        },
        error: () => {
          alert("Error al eliminar el empleado");
        }
      });
    }
    this.cdr.detectChanges();
  }
}
