import { Component, ViewChild, type ElementRef, type AfterViewChecked } from "@angular/core"
import { CommonModule } from "@angular/common"
import { FormsModule } from "@angular/forms"
import { SpeechService } from '../../../../services/speech/speech'
import { IaService } from '../../../../services/ia/ia-service'
import { ResponseFormatService } from '../../../../services/response-format/response-format-service'
import { NgZone } from '@angular/core'
import { ChangeDetectorRef } from '@angular/core'
import { Persona } from '../../../../models/persona'
import { AuthService } from '../../../../services/auth/auth-service'

interface Message {
  text: string
  type: "user" | "ai"
  time: string
}

interface DynamicTable {
  title: string
  columns: string[]
  rows: Record<string, any>[]
  timestamp: string
  isReadOnly: boolean
}

@Component({
  selector: "app-list-agent",
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: "./list-agent.html",
  styleUrls: ["./list-agent.scss"],
})
export class ListAgent implements AfterViewChecked {
  @ViewChild("chatArea") chatArea!: ElementRef

  messageText = ""
  messages: Message[] = []
  dynamicTables: DynamicTable[] = []

  isUserMenuOpen = false
  usuario: Persona | null = null
  isAdmin = false

  // FORMULARIOS SINCRONIZADOS CON MODELOS MCP REALES
  private readonly formTemplates: Record<string, { title: string; columns: string[] }> = {
    // Modelos principales solicitados
    "crear usuario": {
      title: "Formulario de Usuario",
      columns: ["cedula", "nombre", "apellido", "telefono", "email", "contrasenia", "direccion", "id_reserva"]
    },
    "crear reserva": {
      title: "Formulario de Reserva",
      columns: ["usuario", "id_vuelo", "Numasiento", "estado"]
    },
    "crear vuelo": {
      title: "Formulario de Vuelo",
      columns: ["codigoVuelo", "origen", "destino", "id_avion", "id_piloto", "fecha", "hora", "duracionMinutos", "precioBase", "estado"]
    },
    "crear avion": {
      title: "Formulario de Avión",
      columns: ["modelo", "capacidad", "aerolinea", "estado", "fecha_fabricacion"]
    },
    "crear mantenimiento": {
      title: "Formulario de Mantenimiento",
      columns: ["id_avion", "tipo", "descripcion", "fecha", "responsable", "costo", "estado"]
    },
    // Modelos adicionales útiles
    "crear pago": {
      title: "Formulario de Pago",
      columns: ["monto", "estado", "moneda", "metodo_pago", "id_reserva"]
    },
    "crear empleado": {
      title: "Formulario de Empleado",
      columns: ["nombre", "email", "cedula", "telefono", "salario", "cargo"]
    },
    "crear admin": {
      title: "Formulario de Administrador",
      columns: ["nombre", "email", "cedula", "telefono", "nivel_acceso"]
    },
    "registrarme": {
      title: "Formulario de Registro",
      columns: ["nombre", "apellido", "cedula", "telefono", "email", "contrasenia", "direccion"]
    }
  }

  // MAPEO DE TIPOS DE DATOS PARA VALIDACIÓN
  private readonly fieldTypes: Record<string, Record<string, string>> = {
    "crear usuario": {
      "cedula": "string",
      "nombre": "string",
      "apellido": "string",
      "telefono": "string",
      "email": "email",
      "contrasenia": "string",
      "direccion": "string",
      "id_reserva": "string"
    },
    "crear reserva": {
      "usuario": "string",
      "id_vuelo": "string",
      "Numasiento": "string",
      "estado": "select:ACTIVA,CANCELADA,COMPLETADA,PENDIENTE"
    },
    "crear vuelo": {
      "codigoVuelo": "string",
      "origen": "string",
      "destino": "string",
      "id_avion": "string",
      "id_piloto": "string",
      "fecha": "date",
      "hora": "time",
      "duracionMinutos": "number",
      "precioBase": "number",
      "estado": "select:PROGRAMADO,EN_VUELO,ATERRIZADO,CANCELADO,DEMORADO"
    },
    "crear avion": {
      "modelo": "string",
      "capacidad": "number",
      "aerolinea": "string",
      "estado": "select:disponible,mantenimiento,fuera_de_servicio",
      "fecha_fabricacion": "date"
    },
    "crear mantenimiento": {
      "id_avion": "string",
      "tipo": "select:PREVENTIVO,CORRECTIVO,EMERGENCIA,INSPECCION",
      "descripcion": "string",
      "fecha": "date",
      "responsable": "string",
      "costo": "number",
      "estado": "select:Pendiente,En Proceso,Completado"
    },
    "crear pago": {
      "monto": "number",
      "estado": "select:PENDIENTE,COMPLETADO,CANCELADO,FALLIDO",
      "moneda": "string",
      "metodo_pago": "select:TARJETA,EFECTIVO,TRANSFERENCIA,PAYPAL,CRYPTO",
      "id_reserva": "string"
    }
  }

  constructor(
    private speechService: SpeechService,
    private iaService: IaService,
    private responseFormatService: ResponseFormatService,
    private ngZone: NgZone,
    private cdr: ChangeDetectorRef,
    private authService: AuthService
  ) { }

  private shouldScroll = false
  isLoading = false
  errorText: string | null = null
  isUserRegistered = false

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom()
      this.shouldScroll = false
    }
  }

  getCurrentTime(): string {
    const now = new Date()
    return now.toLocaleTimeString("es-ES", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  private detectFormIntent(message: string): { title: string; columns: string[] } | null {
    const normalize = (text: string) =>
      text
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // remove accents
        .replace(/\s+/g, ' ') // collapse spaces
        .trim()

    const normalizedMessage = normalize(message)

    const containsTokensInOrder = (haystack: string, key: string): boolean => {
      const tokens = normalize(key).split(' ').filter(Boolean)
      let startIndex = 0
      for (const token of tokens) {
        const idx = haystack.indexOf(token, startIndex)
        if (idx === -1) return false
        startIndex = idx + token.length
      }
      return true
    }

    for (const [key, template] of Object.entries(this.formTemplates)) {
      if (containsTokensInOrder(normalizedMessage, key)) {
        return template
      }
    }
    return null
  }

  private addDynamicTable(title: string, columns: string[], rows: Record<string, any>[], options?: { isReadOnly?: boolean }): void {
    const newTable: DynamicTable = {
      title,
      columns,
      rows,
      timestamp: this.getCurrentTime(),
      isReadOnly: options?.isReadOnly ?? false,
    }
    this.dynamicTables.push(newTable)
    console.log("[v0] 📊 Tabla dinámica agregada:", title, "con", rows.length, "filas")
  }

  removeTable(index: number): void {
    if (index >= 0 && index < this.dynamicTables.length) {
      const removedTable = this.dynamicTables.splice(index, 1)[0]
      console.log("[v0] 🗑️ Tabla eliminada:", removedTable.title)
    }
  }

  /**
   * 🚀 Cambio clave: sendMessage ahora solo genera tabla si detecta intención de formulario
   */
  sendMessage(): void {
    const message = this.messageText.trim()
    if (message === "" || this.isLoading) return

    this.messages.push({
      text: message,
      type: "user",
      time: this.getCurrentTime(),
    })

    this.messageText = ""
    this.shouldScroll = true
    this.cdr.detectChanges()

    this.isLoading = true
    this.errorText = null

    // Detectar si el mensaje es para crear un formulario
    const formIntent = this.detectFormIntent(message)
    if (formIntent) {
      // Crear tabla inicial con fila vacía
      const rows = [Object.fromEntries(formIntent.columns.map(c => [c, ""]))]
      this.addDynamicTable(formIntent.title, formIntent.columns, rows)

      this.isLoading = false // Ya no está cargando
      this.cdr.detectChanges()
      console.log("[sendMessage] 🧾 Formulario detectado:", formIntent.title)
      return // NO enviar mensaje a la IA todavía
    }

    // Si NO es formulario, sí enviar mensaje a la IA
    this.iaService.sendMessage(message).subscribe({
      next: (reply: unknown) => {
        this.ngZone.run(() => {
          try {
            const formatted = this.responseFormatService.formatResponse(reply)
            const replyText = formatted.text?.trim()

            if (!replyText) {
              if (!formatted.table) {
                throw new Error('Respuesta vacía del formateador')
              }
              this.messages.push({
                text: '📊 Se generó una tabla con los resultados.',
                type: "ai",
                time: this.getCurrentTime(),
              })
            } else {
              this.messages.push({
                text: replyText,
                type: "ai",
                time: this.getCurrentTime(),
              })
            }

            if (formatted.table) {
              this.addDynamicTable(
                formatted.table.title,
                formatted.table.columns,
                formatted.table.rows,
                { isReadOnly: true }
              )
            }
            this.isLoading = false
            this.shouldScroll = true
            this.cdr.detectChanges()
          } catch (formatError) {
            console.error('❌ Error al formatear la respuesta:', formatError)
            this.messages.push({
              text: 'Error al procesar la respuesta de la IA.',
              type: "ai",
              time: this.getCurrentTime(),
            })
            this.isLoading = false
            this.cdr.detectChanges()
          }
        })
      },
      error: (err) => {
        this.ngZone.run(() => {
          this.errorText = 'Hubo un problema obteniendo la respuesta. Intenta de nuevo.'
          this.messages.push({
            text: this.errorText,
            type: "ai",
            time: this.getCurrentTime(),
          })
          this.isLoading = false
          this.shouldScroll = true
          this.cdr.detectChanges()
        })
      },
    })

    console.log("[sendMessage] 🕒 Mensaje enviado a IA:", message)
  }

  /**
   * 🚀 MEJORADO: Enviar datos estructurados en formato JSON a la IA
   */
  confirmTable(index: number): void {
    const table = this.dynamicTables[index]
    if (table.isReadOnly) return
    const formData = { ...table.rows[0] }
    const required = this.fieldTypes[this.normalizeTitleToEntity(table.title)] || {}
    const missing: string[] = []
    Object.keys(required).forEach(k => {
      if (!(k in formData) || String(formData[k] ?? '').trim() === '') missing.push(k)
    })
    if (missing.length) {
      this.errorText = `Faltan campos: ${missing.join(', ')}`
      this.messages.push({ text: this.errorText, type: "ai", time: this.getCurrentTime() })
      this.shouldScroll = true
      this.cdr.detectChanges()
      return
    }
    const msg = this.buildCreateMessage(table.title, formData)
    this.messages.push({ text: msg, type: "user", time: this.getCurrentTime() })
    this.shouldScroll = true
    this.cdr.detectChanges()
    this.isLoading = true
    this.errorText = null
    this.iaService.sendMessage(msg).subscribe({
      next: (reply: unknown) => {
        this.ngZone.run(() => {
          try {
            const formatted = this.responseFormatService.formatResponse(reply)
            const replyText = formatted.text?.trim()
            if (!replyText) {
              if (!formatted.table) throw new Error('Respuesta vacía')
              this.messages.push({ text: '📊 Se generó una tabla con los resultados.', type: "ai", time: this.getCurrentTime() })
            } else {
              this.messages.push({ text: replyText, type: "ai", time: this.getCurrentTime() })
            }
            if (formatted.table) {
              this.addDynamicTable(formatted.table.title, formatted.table.columns, formatted.table.rows, { isReadOnly: true })
            }
            this.isLoading = false
            this.shouldScroll = true
            this.cdr.detectChanges()
          } catch {
            this.messages.push({ text: 'Error al procesar la respuesta de la IA.', type: "ai", time: this.getCurrentTime() })
            this.isLoading = false
            this.cdr.detectChanges()
          }
        })
      },
      error: () => {
        this.ngZone.run(() => {
          this.errorText = 'Hubo un problema obteniendo la respuesta. Intenta de nuevo.'
          this.messages.push({ text: this.errorText, type: "ai", time: this.getCurrentTime() })
          this.isLoading = false
          this.shouldScroll = true
          this.cdr.detectChanges()
        })
      },
    })
    this.removeTable(index)
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === "Enter" && !this.isLoading) {
      this.sendMessage()
    }
  }

  resetChat(): void {
    this.messages = []
    this.messageText = ""
    this.isLoading = false
    this.errorText = null
    this.shouldScroll = true
    this.cdr.detectChanges()
  }

  private scrollToBottom(): void {
    try {
      setTimeout(() => {
        if (this.chatArea?.nativeElement) {
          this.chatArea.nativeElement.scrollTop = this.chatArea.nativeElement.scrollHeight
        }
      }, 100)
    } catch (err) {
      console.error("Error scrolling to bottom:", err)
    }
  }

  speakMessage(text: string) {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = "es-ES"
      utterance.rate = 1
      utterance.pitch = 1
      speechSynthesis.speak(utterance)
    } else {
      console.warn("Tu navegador no soporta Speech Synthesis.")
    }
  }

  startListening(): void {
    if (this.isLoading) return

    this.speechService.startListening((transcript: string) => {
      this.messageText = transcript
      this.sendMessage()
    })
  }

  trackByIndex(index: number, item: Message): number {
    return index
  }

  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen
  }

  handleLogin(): void {
    window.location.href = '/login'
  }

  handleRegister(): void {
    window.location.href = '/register'
  }

  handleEdit(): void {
    window.location.href = '/edit'
  }

  ngOnInit(): void {
    this.authService.getUsuarioActual().subscribe({
      next: usuario => {
        this.usuario = usuario;
        this.isUserRegistered = !!usuario;
        this.isAdmin = usuario?.rol === 'Admin';
        this.cdr.detectChanges();
      },
      error: err => {
        this.usuario = null;
        this.isUserRegistered = false;
        this.isAdmin = false;
        this.cdr.detectChanges();
      }
    });
    this.cdr.detectChanges();
  }

  private normalizeTitleToEntity(title: string): string {
    const t = title.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    if (t.includes('usuario')) return 'usuario'
    if (t.includes('reserva')) return 'reserva'
    if (t.includes('vuelo')) return 'vuelo'
    if (t.includes('avion')) return 'avion'
    if (t.includes('mantenimiento')) return 'mantenimiento'
    if (t.includes('pago')) return 'pago'
    return 'usuario'
  }

  getSelectOptions(entityTitle: string, field: string): string[] {
    const entity = this.normalizeTitleToEntity(entityTitle)
    const types = this.fieldTypes[`crear ${entity}`] || {}
    const t = types[field]
    if (!t || !t.startsWith('select:')) return []
    return t.replace('select:', '').split(',')
  }

  getFieldType(entityTitle: string, field: string): string {
    const entity = this.normalizeTitleToEntity(entityTitle)
    const types = this.fieldTypes[`crear ${entity}`] || {}
    const t = types[field] || 'string'
    if (t.startsWith('select:')) return 'select'
    if (t === 'number') return 'number'
    if (t === 'date') return 'date'
    if (t === 'time') return 'time'
    return 'text'
  }

  private normalizeSelection(entity: string, field: string, value: any): any {
    if (value === undefined || value === null) return value
    const v = String(value).trim()
    if (entity === 'avion' && field === 'estado') {
      const map: Record<string, string> = {
        'DISPONIBLE': 'disponible',
        'MANTENIMIENTO': 'mantenimiento',
        'FUERA_SERVICIO': 'fuera_de_servicio',
        'disponible': 'disponible',
        'mantenimiento': 'mantenimiento',
        'fuera_de_servicio': 'fuera_de_servicio'
      }
      return map[v] || v
    }
    if (entity === 'pago' && field === 'estado') {
      const allowed = ['PENDIENTE','COMPLETADO','CANCELADO','FALLIDO']
      const upper = v.toUpperCase()
      return allowed.includes(upper) ? upper : v
    }
    if (entity === 'pago' && field === 'metodo_pago') {
      const allowed = ['TARJETA','EFECTIVO','TRANSFERENCIA','PAYPAL','CRYPTO']
      const upper = v.toUpperCase()
      return allowed.includes(upper) ? upper : v
    }
    if (entity === 'mantenimiento' && field === 'estado') {
      const map: Record<string, string> = {
        'PROGRAMADO': 'Pendiente',
        'EN_PROGRESO': 'En Proceso',
        'COMPLETADO': 'Completado',
        'Pendiente': 'Pendiente',
        'En Proceso': 'En Proceso',
        'Completado': 'Completado'
      }
      return map[v] || v
    }
    if (entity === 'vuelo' && field === 'estado') {
      const allowed = ['PROGRAMADO','EN_VUELO','ATERRIZADO','CANCELADO','DEMORADO']
      const upper = v.toUpperCase()
      return allowed.includes(upper) ? upper : v
    }
    if (entity === 'reserva' && field === 'estado') {
      const allowed = ['ACTIVA','CANCELADA','COMPLETADA','PENDIENTE']
      const upper = v.toUpperCase()
      return allowed.includes(upper) ? upper : v
    }
    return value
  }

  private buildCreateMessage(title: string, data: Record<string, any>): string {
    const entity = this.normalizeTitleToEntity(title)
    const pairs: string[] = []
    const push = (k: string) => {
      const v = data[k]
      if (v === undefined || v === null || String(v).trim() === '') return
      const norm = this.normalizeSelection(entity, k, v)
      pairs.push(`${k} ${norm}`)
    }
    if (entity === 'usuario') {
      ;['nombre','apellido','cedula','telefono','email','contrasenia','direccion','id_reserva'].forEach(push)
      return `crear usuario: ${pairs.join(', ')}`
    }
    if (entity === 'reserva') {
      ;['usuario','id_vuelo','Numasiento','estado'].forEach(push)
      return `crear reserva: ${pairs.join(', ')}`
    }
    if (entity === 'vuelo') {
      ;['codigoVuelo','origen','destino','id_avion','id_piloto','fecha','hora','duracionMinutos','precioBase','estado'].forEach(push)
      return `crear vuelo: ${pairs.join(', ')}`
    }
    if (entity === 'avion') {
      ;['modelo','capacidad','aerolinea','estado','fecha_fabricacion'].forEach(push)
      return `crear avion: ${pairs.join(', ')}`
    }
    if (entity === 'mantenimiento') {
      ;['id_avion','tipo','descripcion','fecha','responsable','costo','estado'].forEach(push)
      return `crear mantenimiento: ${pairs.join(', ')}`
    }
    if (entity === 'pago') {
      ;['monto','estado','moneda','metodo_pago','id_reserva'].forEach(push)
      return `crear pago: ${pairs.join(', ')}`
    }
    return `crear ${entity}: ${pairs.join(', ')}`
  }
}