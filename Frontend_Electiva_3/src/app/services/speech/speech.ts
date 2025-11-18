import { Injectable, NgZone } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SpeechService {
  private recognition: any;

  constructor(private zone: NgZone) {}

  private initRecognition() {
    if (typeof window !== 'undefined' && !this.recognition) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'es-ES';
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
      } else {
        console.warn('SpeechRecognition no está disponible en este navegador');
      }
    }
  }

  startListening(callback: (text: string) => void) {
    this.initRecognition();

    if (!this.recognition) return;

    this.recognition.start();

    this.recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      this.zone.run(() => callback(transcript));
    };

    this.recognition.onerror = (event: any) => {
      console.error('Error en reconocimiento de voz:', event.error);
    };
  }

  stopListening() {
    if (this.recognition) {
      this.recognition.stop();
    }
  }
}
