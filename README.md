# Guitar Pedalboard 🎸

Simulador de pedales de guitarra en tiempo real para Linux.
Conectá tu interfaz de audio USB, armá tu cadena de efectos y tocá con el sonido que quieras — todo desde una interfaz gráfica simple e intuitiva.

> **Autor:** Lucas Aguirre — [@LucasAguirre99](https://github.com/LucasAguirre99)
> **Licencia:** MIT

---

## Características

- **14 efectos en tiempo real**: Distorsión, Overdrive, Reverb, Delay, Chorus, Phaser, Compresor, Puerta de Ruido, Filtro de Agudos, Filtro de Graves, Pitch Shift, Wah y Amplificador
- **Cadena de efectos configurable**: agregá, quitá y reordenás los pedales en cualquier momento mientras tocás
- **Editor de parámetros en vivo**: ajustás cada perilla con sliders que se aplican en tiempo real sin interrumpir el audio
- **Activar / desactivar pedales individualmente** sin sacarlos de la cadena
- **Presets predefinidos**: cargá sonidos completos con un clic, incluyendo estilos de artistas
- **Afinador cromático en tiempo real**: detecta la nota que estás tocando y te muestra los cents de desafinación
- **Círculo de Quintas interactivo**: visualizá escalas, seleccioná tónica y reproducí una base para improvisar
- **Visualización tipo pedalboard real**: cada efecto tiene el diseño gráfico del pedal físico que representa
- **Selección de dispositivos de audio**: compatible con cualquier interfaz USB
- **Procesamiento de baja latencia** usando [pedalboard](https://github.com/spotify/pedalboard) de Spotify + [sounddevice](https://python-sounddevice.readthedocs.io/)

---

## Efectos disponibles

| Pedal | Inspirado en | Parámetros |
|---|---|---|
| **Volumen** | BOSS FV-500H | Ganancia (dB) |
| **Distorsión** | BOSS DS-1 | Drive (dB) |
| **Overdrive** | Ibanez TS9 | Drive suave (dB) |
| **Reverb** | BOSS RV-6 | Tamaño de sala, Amortiguación, Efecto, Seco |
| **Delay** | BOSS DD-3 | Tiempo (s), Retroalimentación, Mezcla |
| **Chorus** | BOSS CE-5 | Velocidad (Hz), Profundidad, Mezcla |
| **Phaser** | MXR Phase 90 | Velocidad (Hz), Profundidad, Mezcla |
| **Compresor** | MXR Dyna Comp | Umbral (dB), Ratio, Ataque (ms), Release (ms) |
| **Puerta de Ruido** | BOSS NS-2 | Umbral (dB), Ratio, Ataque (ms), Release (ms) |
| **Filtro Agudos** | EHX Knockout | Frecuencia de corte (Hz) |
| **Filtro Graves** | EHX Bass Boost | Frecuencia de corte (Hz) |
| **Pitch Shift** | BOSS PS-6 | Semitonos |
| **Wah** | Dunlop Cry Baby | Posición (Hz), Resonancia, Mezcla + modo Auto con LFO |
| **Amplificador** | Mesa Boogie Mk V | Modelo, Ganancia, Graves, Medios, Agudos, Presencia, Volumen |

### Wah — manual y automático

El pedal Wah implementa un filtro biquad resonante con barrido de frecuencia (300–2200 Hz):

- **Modo Manual**: un slider controla la posición del wah, como si el pedal estuviera pisado en un punto fijo
- **Modo Auto**: un LFO senoidal barre la frecuencia automáticamente a la velocidad y profundidad que configures

### Amplificador — simulación de amp completa

Simula la cadena de señal interna de un amplificador de guitarra:

```
Pre-amp (saturación tanh) → Tone stack (graves/medios/agudos) → Presencia → Cabinet sim → Volumen
```

Incluye 5 modelos con EQ y carácter propio:

| Modelo | Carácter |
|---|---|
| Fender Clean | Limpio, brillante, muy poco drive |
| Vox AC30 | Overdrive suave, mucha presencia |
| Marshall Crunch | Crunch clásico, mid scooped |
| Mesa Boogie Lead | High gain apretado y articulado |
| Orange Dirty | Grave y grueso, muy saturado |

---

## Presets

Cargá un sonido completo con un clic desde el panel izquierdo:

| Preset | Cadena de efectos |
|---|---|
| **Marty Friedman - Lead** | Puerta de Ruido → Distorsión alta → Filtro Agudos → Reverb sutil |
| **Sonido Limpio** | Compresor → Chorus suave → Reverb |
| **Blues Clásico** | Compresor → Overdrive → Reverb |
| **Doom / Stoner** | Puerta de Ruido → Distorsión extrema → Filtro Graves → Reverb largo |
| **Surf Rock** | Chorus → Reverb largo → Delay |
| **Shred / Metal Moderno** | Puerta de Ruido → Compresor → Distorsión → Filtro Agudos → Delay |

---

## Afinador cromático

El afinador está integrado en el panel derecho y funciona en tiempo real mientras tocás:

- Detecta la nota y el octavo usando autocorrelación via FFT
- Muestra los **cents de desafinación** con una barra de color:
  - **Verde**: ±10 cents (en tono)
  - **Amarillo**: ±25 cents (cerca)
  - **Rojo**: >25 cents (lejos)
- Rango: E2 (82 Hz) hasta notas agudas del traste 24
- Analiza el audio **antes** de los efectos para mayor precisión

---

## Círculo de Quintas / Escalas / Base

Abrí la herramienta desde el botón en la barra inferior de la aplicación.

### Círculo de Quintas interactivo

- Visualización de las 12 notas en orden de quintas (anillo exterior: mayores, interior: relativas menores)
- **Hacé clic en cualquier nota** del círculo para seleccionarla como tónica
- Las notas de la escala seleccionada se resaltan en verde; la tónica en rojo

### Escalas disponibles

Mayor, Menor Natural, Pentatónica Mayor, Pentatónica Menor, Blues, Dorian, Frigio, Lidio, Mixolidio, Menor Armónica

### Base para improvisar

- Seleccioná tónica + escala + BPM y presioná **Reproducir base**
- La base se sintetiza automáticamente con acordes diatónicos de la escala elegida
- Progresión I–IV–V–I para escalas mayores, i–VI–VII–i para menores y modos oscuros
- Suena en loop continuo y simultáneamente con tu guitarra procesada
- Cambiá la escala o la tónica en cualquier momento y la base se actualiza sola

---

## Requisitos del sistema

- **Sistema operativo:** Linux (probado en Ubuntu 22.04+)
- **Python:** 3.8 o superior
- **Dependencias del sistema:**
  ```bash
  sudo apt-get install python3-tk libportaudio2
  ```
- **Interfaz de audio:** cualquier interfaz USB compatible con ALSA/PulseAudio (probado con HUGEL KM-A101)

---

## Instalación

1. **Cloná el repositorio:**
   ```bash
   git clone https://github.com/LucasAguirre99/guitar-pedalboard.git
   cd guitar-pedalboard
   ```

2. **Instalá las dependencias del sistema:**
   ```bash
   sudo apt-get install python3-tk libportaudio2
   ```

3. **Instalá las dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutá la aplicación:**
   ```bash
   python3 guitar_pedalboard.py
   ```

---

## Uso

### Configuración inicial

1. Conectá tu interfaz de audio USB a la computadora
2. Abrí la aplicación
3. En la barra superior, seleccioná:
   - **Entrada:** `pulse` (captura desde la interfaz activa en PulseAudio)
   - **Salida:** `pulse` (envía al dispositivo de salida configurado en el sistema)
   - **Hz:** `44100`
4. Presioná **Iniciar**

### Flujo de la señal

```
GUITARRA → Interfaz USB → PulseAudio (entrada) → Cadena de efectos → PulseAudio (salida) → Auriculares / Parlantes
```

### Cómo usar la interfaz

| Elemento | Acción |
|---|---|
| Panel izquierdo | Hacé clic en un pedal para agregarlo a la cadena |
| Clic en un pedal de la cadena | Abrís su editor de parámetros |
| Botón **ON / OFF** | Activás o desactivás el pedal sin eliminarlo |
| Botones **< >** | Reordenás el pedal dentro de la cadena |
| Botón **X** | Eliminás el pedal de la cadena |
| Sliders del panel derecho | Ajustás los parámetros en tiempo real |
| Botón **Restablecer valores** | Devolvés los parámetros al valor por defecto |
| Dropdown de presets | Seleccionás un preset predefinido |
| Botón **Cargar preset** | Reemplazás la cadena actual con el preset |
| Botón inferior **Círculo de Quintas** | Abrís la herramienta de escalas y base |

### Tips

- **Latencia:** si notás retraso, probá reducir el buffer a `128` o `64` (requiere interfaz de audio estable)
- **Ruido de fondo:** agregá una **Puerta de Ruido** al inicio de la cadena para eliminar el zumbido cuando no estás tocando
- **Sonido limpio:** un **Compresor** antes de la distorsión da un tono más profesional
- **El orden importa:** la señal pasa por los pedales de izquierda a derecha, igual que en un pedalboard físico
- **Amplificador:** poné el Amplificador al final de la cadena (antes del Reverb/Delay) para el flujo de señal más realista
- **Improvisar:** usá el Círculo de Quintas para elegir una escala, activá la base y tocá encima — las notas resaltadas en verde son las que suenan bien

---

## Cómo contribuir

Las contribuciones son bienvenidas. Si querés agregar un efecto, mejorar la interfaz o arreglar un bug:

1. **Hacé un fork** del repositorio
2. **Creá una rama** para tu feature:
   ```bash
   git checkout -b feature/nombre-del-feature
   ```
3. **Hacé tus cambios** y commiteá con mensajes descriptivos:
   ```bash
   git commit -m "feat: agregar efecto Tremolo"
   ```
4. **Pusheá tu rama:**
   ```bash
   git push origin feature/nombre-del-feature
   ```
5. **Abrí un Pull Request** en GitHub describiendo qué cambiaste y por qué

### Ideas para contribuir

- Soporte para Windows y macOS
- Guardar y cargar presets personalizados desde archivo
- Efectos adicionales: Fuzz, Tremolo, Vibrato, Flanger, Looper
- Visualizador de forma de onda / espectro en tiempo real
- Control MIDI para los parámetros
- Interfaz gráfica con knobs animados en lugar de sliders
- Más modelos de amplificador
- Empaquetado como `.deb` o AppImage

### Reportar bugs

Abrí un [Issue en GitHub](https://github.com/LucasAguirre99/guitar-pedalboard/issues) con:
- Descripción del problema
- Sistema operativo y versión
- Interfaz de audio utilizada
- Pasos para reproducir el error
- Mensaje de error (si hay)

---

## Estructura del proyecto

```
guitar-pedalboard/
├── guitar_pedalboard.py   # Aplicación principal (archivo único)
├── requirements.txt       # Dependencias de Python
├── LICENSE                # Licencia MIT
├── README.md              # Este archivo
├── PROJECT.md             # Documentación técnica interna
└── docs/
    └── screenshots/       # Capturas de pantalla
```

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

Copyright (c) 2025 Lucas Aguirre — aguirrelucas.unrc@gmail.com
