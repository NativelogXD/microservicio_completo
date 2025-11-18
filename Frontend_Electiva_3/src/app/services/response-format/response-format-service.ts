import { Injectable } from '@angular/core';
import { Persona } from '../../models/persona';
import { Vuelo } from '../../models/vuelo';
import { Usuario } from '../../models/usuario';
import { Empleado } from '../../models/empleado';
import { Admin } from '../../models/admin';
import { Avion } from '../../models/avion';

export interface FormattedTable {
  title: string;
  columns: string[];
  rows: Record<string, string>[];
}

export interface FormattedResponse {
  text: string;
  table?: FormattedTable;
}

@Injectable({
  providedIn: 'root'
})
export class ResponseFormatService {
  formatResponse(reply: unknown): FormattedResponse {
    console.log('[formatResponse] 🔍 Iniciando formateo...');
    console.log('[formatResponse] 📥 Tipo de entrada:', typeof reply);
    console.log('[formatResponse] 📥 Contenido:', reply);

    if (reply === null || reply === undefined) {
      console.log('[formatResponse] ⚠️ Respuesta null/undefined');
      return this.toTextResponse('❌ No se encontró información para tu consulta.');
    }

    if (typeof reply === 'string') {
      console.log('[formatResponse] ✅ Es string directo:', reply);
      if (reply.trim() === '') {
        return this.toTextResponse('❌ No se encontró información para tu consulta.');
      }
      return this.toTextResponse(reply);
    }

    // Si es objeto o array, primero intentar desempaquetar cualquier "result"
    if (typeof reply === 'object') {
      const unwrapped = this.unwrapResult(reply);
      // Si result era un array -> formatear como lista
      if (Array.isArray(unwrapped)) {
        console.log('[formatResponse] 📋 Resultado desempaquetado es array');
        return this.formatArray(unwrapped);
      }
      // Si es string luego de desempaquetar
      if (typeof unwrapped === 'string') {
        return this.toTextResponse(unwrapped);
      }
      // Si es objeto -> seguir con detección/format
      if (typeof unwrapped === 'object' && unwrapped !== null) {
        const obj = unwrapped as Record<string, unknown>;
        console.log('[formatResponse] 🔎 Es objeto (desempaquetado), detectando tipo...');
        const result = this.detectAndFormat(obj);
        console.log('[formatResponse] ✅ Resultado formateado:', result);
        return result;
      }
    }

    console.log('[formatResponse] ⚠️ Usando formato genérico');
    return this.formatGeneric(reply);
  }

  private toTextResponse(text: string): FormattedResponse {
    return { text };
  }

  /**
   * Extrae/Desempaqueta repetidamente el campo 'result' si existe.
   * Devuelve array | object | string | number | ...
   */
  private unwrapResult(value: unknown): unknown {
    let current = value;
    const wrapperKeys = ['execution', 'result', 'data', 'payload'];

    while (current && typeof current === 'object' && !Array.isArray(current)) {
      const asObj = current as Record<string, unknown>;
      let unwrapped = false;

      for (const key of wrapperKeys) {
        if (key in asObj) {
          current = asObj[key];
          unwrapped = true;
          console.log(`[unwrapResult] 🔁 Desempaquetando por "${key}"`);
          break;
        }
      }

      if (!unwrapped) break;
    }

    return current;
  }

  private detectAndFormat(obj: Record<string, unknown>): FormattedResponse {
    console.log('[detectAndFormat] 🔍 Analizando objeto:', Object.keys(obj));

    // Formato extendido para respuestas de herramientas/agents
    if (this.isExecutionEnvelope(obj)) {
      return this.formatExecutionEnvelope(obj);
    }

    // Mantener chequeos directos que sean comunes
    if (obj['response'] && typeof obj['response'] === 'string') {
      return this.toTextResponse(obj['response'] as string);
    }
    if (obj['message'] && typeof obj['message'] === 'string') {
      return this.toTextResponse(obj['message'] as string);
    }
    if (obj['reply'] && typeof obj['reply'] === 'string') {
      return this.toTextResponse(obj['reply'] as string);
    }
    if (obj['text'] && typeof obj['text'] === 'string') {
      return this.toTextResponse(obj['text'] as string);
    }

    // Si resulta ser un array (ej: { items: [...] } ), dejar que formatUnknownObject lo detecte
    if (Array.isArray(obj)) {
      return this.formatArray(obj as unknown as unknown[]);
    }

    // Tipos conocidos (Persona, Usuario, Empleado, Admin, Vuelo, Avion)
    if (this.isPersona(obj)) {
      return this.toTextResponse(this.formatPersona(obj as unknown as Persona));
    }
    if (this.isUsuario(obj)) {
      return this.toTextResponse(this.formatUsuario(obj as unknown as Usuario));
    }
    if (this.isEmpleado(obj)) {
      return this.toTextResponse(this.formatEmpleado(obj as unknown as Empleado));
    }
    if (this.isAdmin(obj)) {
      return this.toTextResponse(this.formatAdmin(obj as unknown as Admin));
    }
    if (this.isVuelo(obj)) {
      return this.toTextResponse(this.formatVuelo(obj as unknown as Vuelo));
    }
    if (this.isAvion(obj)) {
      return this.toTextResponse(this.formatAvion(obj as unknown as Avion));
    }

    // Contadores
    if (obj['total_personas'] !== undefined) {
      return this.toTextResponse(`👥 Total de personas: ${obj['total_personas']}`);
    }
    if (obj['total_vuelos'] !== undefined) {
      return this.toTextResponse(`✈️ Total de vuelos: ${obj['total_vuelos']}`);
    }
    if (obj['total_aviones'] !== undefined) {
      return this.toTextResponse(`🛩️ Total de aviones: ${obj['total_aviones']}`);
    }

    // Fallback: formatear genérico mejorado
    return this.formatUnknownObject(obj);
  }

  private isExecutionEnvelope(obj: Record<string, unknown>): boolean {
    return (
      typeof obj['execution'] === 'object' &&
      obj['execution'] !== null &&
      (typeof obj['response'] === 'string' || typeof obj['reasoning'] === 'string')
    );
  }

  // ==== Detectores ====
  private isPersona(obj: Record<string, unknown>): boolean {
    return obj['cedula'] !== undefined && (obj['nombre'] !== undefined || obj['apellido'] !== undefined);
  }

  private isVuelo(obj: Record<string, unknown>): boolean {
    return obj['codigoVuelo'] !== undefined && obj['origen'] !== undefined;
  }

  private isUsuario(obj: Record<string, unknown>): boolean {
    return obj['rol'] !== undefined && obj['email'] !== undefined;
  }

  private isEmpleado(obj: Record<string, unknown>): boolean {
    return obj['salario'] !== undefined && obj['cargo'] !== undefined;
  }

  private isAdmin(obj: Record<string, unknown>): boolean {
    return obj['nivelAcceso'] !== undefined && obj['permiso'] !== undefined;
  }

  private isAvion(obj: Record<string, unknown>): boolean {
    return (obj['modelo'] !== undefined && obj['capacidad'] !== undefined) || (obj['id'] !== undefined && obj['modelo'] !== undefined);
  }

  private formatExecutionEnvelope(envelope: Record<string, unknown>): FormattedResponse {
    const lines: string[] = [];
    let nestedTable: FormattedTable | undefined;

    if (typeof envelope['response'] === 'string') {
      lines.push(`✅ ${envelope['response']}`);
    }
    if (typeof envelope['reasoning'] === 'string') {
      lines.push(`🧠 ${envelope['reasoning']}`);
    }
    if (typeof envelope['tool_used'] === 'string') {
      lines.push(`🛠️ Herramienta: ${envelope['tool_used']}`);
    }
    if (typeof envelope['confidence'] === 'number') {
      lines.push(`📈 Confianza: ${(envelope['confidence'] * 100).toFixed(1)}%`);
    }

    const execution = envelope['execution'] as Record<string, unknown> | undefined;
    if (execution) {
      if (typeof execution['status'] === 'string') {
        lines.push(`⚙️ Ejecución: ${execution['status']}`);
      }
      if (execution['result'] !== undefined) {
        const unwrapped = this.unwrapResult(execution['result']);
        let formattedResult: string;

        if (unwrapped === null || unwrapped === undefined) {
          formattedResult = '(sin resultado)';
        } else if (typeof unwrapped === 'object') {
          const nested = this.detectAndFormat(unwrapped as Record<string, unknown>);
          formattedResult = nested.text;
          nestedTable = nested.table ?? nestedTable;
        } else {
          formattedResult = String(unwrapped);
        }

        lines.push(`📊 Resultado: ${formattedResult}`);
      }
      if (typeof execution['execution_time'] === 'number') {
        lines.push(`⏱️ Tiempo: ${execution['execution_time'].toFixed(3)}s`);
      }
    }

    if (lines.length === 0) {
      return this.formatUnknownObject(envelope);
    }

    const response: FormattedResponse = this.toTextResponse(lines.join('\n'));
    if (nestedTable) {
      response.table = nestedTable;
    }
    return response;
  }

  // ==== Formateadores específicos ====
  private formatPersona(persona: Persona): string {
    const nombreCompleto = `${persona.nombre ?? ''} ${persona.apellido ?? ''}`.trim();
    let resultado = `👤 ${nombreCompleto || 'Nombre no disponible'}`;
    if (persona.cedula) resultado += `\n   📋 Cédula: ${persona.cedula}`;
    if (persona.email) resultado += `\n   📧 Email: ${persona.email}`;
    if (persona.telefono) resultado += `\n   📞 Teléfono: ${persona.telefono}`;
    return resultado;
  }

  private formatVuelo(vuelo: Vuelo): string {
    return `✈️ Vuelo ${vuelo.codigoVuelo}\n` +
           `   🛫 Origen: ${vuelo.origen}\n` +
           `   🛬 Destino: ${vuelo.destino}\n` +
           `   📅 Fecha: ${vuelo.fecha}\n` +
           `   💰 Precio: ${vuelo.precioBase}`;
  }

  private formatUsuario(usuario: Usuario): string {
    const nombreCompleto = `${usuario.nombre ?? ''} ${usuario.apellido ?? ''}`.trim();
    return `👨‍💼 Usuario: ${nombreCompleto}\n` +
           `   📧 Email: ${usuario.email}\n` +
           `   📞 Teléfono: ${usuario.telefono}`;
  }

  private formatEmpleado(empleado: Empleado): string {
    const nombreCompleto = `${empleado.nombre ?? ''} ${empleado.apellido ?? ''}`.trim();
    let resultado = `💼 Empleado: ${nombreCompleto}`;
    if (empleado.cedula) resultado += `\n   📋 Cédula: ${empleado.cedula}`;
    if (empleado.email) resultado += `\n   📧 Email: ${empleado.email}`;
    if (empleado.telefono) resultado += `\n   📞 Teléfono: ${empleado.telefono}`;
    if (empleado.cargo) resultado += `\n   🎯 Cargo: ${empleado.cargo}`;
    if (empleado.salario) resultado += `\n   💵 Salario: ${empleado.salario}`;
    return resultado;
  }

  private formatAdmin(admin: Admin): string {
    const nombreCompleto = `${admin.nombre ?? ''} ${admin.apellido ?? ''}`.trim();
    let resultado = `🔐 Administrador: ${nombreCompleto}`;
    if (admin.cedula) resultado += `\n   📋 Cédula: ${admin.cedula}`;
    if (admin.email) resultado += `\n   📧 Email: ${admin.email}`;
    if (admin.telefono) resultado += `\n   📞 Teléfono: ${admin.telefono}`;
    if (admin.nivelAcceso) resultado += `\n   🎚️ Nivel de Acceso: ${admin.nivelAcceso}`;
    if (admin.permiso) resultado += `\n   ✅ Permisos: ${admin.permiso}`;
    return resultado;
  }

  private formatAvion(avion: Avion): string {
    return `🛩️ Avión ${avion.id ?? ''}\n` +
           `   🏷️ Modelo: ${avion.modelo}\n` +
           `   👥 Capacidad: ${avion.capacidad}\n` +
           `   🏢 Aerolínea: ${avion.aerolinea ?? '(no disponible)'}\n` +
           `   📊 Estado: ${avion.estado ?? '(no disponible)'}\n` +
           `   📅 Fabricación: ${avion.fecha_fabricacion ?? '(no disponible)'}`;
  }

  // ==== Formato de arrays ====
  private formatArray(items: unknown[]): FormattedResponse {
    if (!items || items.length === 0) {
      return this.toTextResponse('❌ No se encontraron elementos.');
    }

    const recordItems = items.filter(item => this.isRecord(item)) as Record<string, unknown>[];

    if (recordItems.length > 0) {
      const table = this.buildTableFromRecords(recordItems);
      return {
        text: `📋 Se encontraron ${recordItems.length} registro(s).`,
        table
      };
    }

    const formattedText = items.map((item, index) => {
      if (item === null || item === undefined) return `\n${index + 1}. (no disponible)`;
      if (typeof item === 'object') {
        const itemFormatted = this.detectAndFormat(item as Record<string, unknown>);
        return `\n${index + 1}. ${itemFormatted.text}\n${'─'.repeat(50)}`;
      }
      return `\n${index + 1}. ${String(item)}`;
    });

    return this.toTextResponse(`📋 Se encontraron ${items.length} elemento(s):\n${formattedText.join('\n')}`);
  }

  // ==== Formato mejorado para objetos desconocidos ====
  private formatUnknownObject(obj: Record<string, unknown>): FormattedResponse {
    console.log('[formatUnknownObject] 📦 Formateando objeto desconocido');
    const lines: string[] = ['📄 Información:'];
    let nestedTable: FormattedTable | undefined;
    let hasContent = false;
    // NO eliminar 'id' automáticamente — puede ser relevante
    const skipKeys = new Set(['result', '__v', '_id']); // quité 'id' de aquí
    for (const [key, value] of Object.entries(obj)) {
      if (skipKeys.has(key)) continue;
      const emoji = this.getEmojiForKey(key);
      const formattedKey = this.formatKey(key);

      if (value === null || value === undefined) {
        lines.push(`   ${emoji} ${formattedKey}: (no disponible)`);
        hasContent = true;
      } else if (Array.isArray(value)) {
        lines.push(`   ${emoji} ${formattedKey}: ${value.length} elemento(s)`);
        // si quieres mostrar más, podrías mapear aquí
        hasContent = true;
      } else if (typeof value === 'object') {
        lines.push(`   ${emoji} ${formattedKey}:`);
        const nested = this.detectAndFormat(value as Record<string, unknown>);
        lines.push(`      ${nested.text.replace(/\n/g, '\n      ')}`);
        nestedTable = nestedTable ?? nested.table;
        hasContent = true;
      } else {
        lines.push(`   ${emoji} ${formattedKey}: ${String(value)}`);
        hasContent = true;
      }
    }

    if (!hasContent) {
      return this.toTextResponse('❌ No se encontró información relevante.');
    }

    const response = this.toTextResponse(lines.join('\n'));
    if (nestedTable) {
      response.table = nestedTable;
    }
    return response;
  }

  private getEmojiForKey(key: string): string {
    const emojiMap: Record<string, string> = {
      'id': '🆔',
      'nombre': '👤',
      'apellido': '👤',
      'email': '📧',
      'telefono': '📞',
      'cedula': '📋',
      'rol': '🎭',
      'cargo': '🎯',
      'salario': '💵',
      'nivelAcceso': '🎚️',
      'permiso': '✅',
      'codigoVuelo': '✈️',
      'origen': '🛫',
      'destino': '🛬',
      'fecha': '📅',
      'precio': '💰',
      'precioBase': '💰',
      'aerolinea': '🏢',
      'contrasenia': '🔒',
      'password': '🔒',
      'created': '📅',
      'updated': '🔄',
      'modelo': '🏷️',
      'capacidad': '👥',
      'estado': '📊'
    };
    return emojiMap[key] || '•';
  }

  private formatKey(key: string): string {
    const formatted = key
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .trim();

    const replacements: Record<string, string> = {
      'Id': 'ID',
      'Email': 'Email',
      'Codigo Vuelo': 'Código de Vuelo',
      'Precio Base': 'Precio Base',
      'Nivel Acceso': 'Nivel de Acceso',
      'Contrasenia': 'Contraseña'
    };
    return replacements[formatted] || formatted;
  }

  private isRecord(value: unknown): value is Record<string, unknown> {
    return !!value && typeof value === 'object' && !Array.isArray(value);
  }

  private buildTableFromRecords(records: Record<string, unknown>[]): FormattedTable {
    const columns = this.getColumnsForRecords(records);
    const columnDefinitions = columns.map(key => ({ key, label: this.formatKey(key) }));
    const rows = records.map(item => {
      const row: Record<string, string> = {};
      columnDefinitions.forEach(({ key, label }) => {
        row[label] = this.formatTableValue(item[key]);
      });
      return row;
    });

    return {
      title: this.getTableTitle(records[0]),
      columns: columnDefinitions.map(def => def.label),
      rows
    };
  }

  private getColumnsForRecords(records: Record<string, unknown>[]): string[] {
    const collected = new Set<string>();
    records.forEach(record => {
      Object.entries(record).forEach(([key, value]) => {
        if (this.shouldSkipTableKey(key)) return;
        if (value === undefined) return;
        collected.add(key);
      });
    });

    const priority = [
      'cedula', 'nombre', 'apellido', 'email', 'telefono',
      'rol', 'cargo', 'salario', 'nivelAcceso', 'permiso',
      'codigoVuelo', 'origen', 'destino', 'fecha', 'precioBase',
      'modelo', 'capacidad', 'estado', 'aerolinea', 'id'
    ];

    const ordered = priority.filter(key => collected.has(key));
    const remaining = Array.from(collected).filter(key => !priority.includes(key));
    return [...ordered, ...remaining];
  }

  private shouldSkipTableKey(key: string): boolean {
    return ['__v', '_id', 'result', 'password', 'contrasenia'].includes(key);
  }

  private formatTableValue(value: unknown): string {
    if (value === null || value === undefined) return '—';
    if (Array.isArray(value)) return `${value.length} elemento(s)`;
    if (typeof value === 'object') {
      try {
        return JSON.stringify(value);
      } catch {
        return '[objeto]';
      }
    }
    return String(value);
  }

  private getTableTitle(sample: Record<string, unknown>): string {
    if (this.isPersona(sample)) return 'Personas';
    if (this.isUsuario(sample)) return 'Usuarios';
    if (this.isEmpleado(sample)) return 'Empleados';
    if (this.isAdmin(sample)) return 'Administradores';
    if (this.isVuelo(sample)) return 'Vuelos';
    if (this.isAvion(sample)) return 'Aviones';
    return 'Resultados';
  }

  private formatGeneric(obj: unknown): FormattedResponse {
    try {
      const result = JSON.stringify(obj, null, 2);
      console.log('[formatGeneric] 📄 JSON stringified:', result);
      return this.toTextResponse(result);
    } catch (err) {
      console.error('[formatGeneric] ❌ Error al hacer stringify:', err);
      return this.toTextResponse(String(obj));
    }
  }
}
