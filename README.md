# Guitar Pedalboard 🎸

Simulador de pedales de guitarra en tiempo real para Linux.
Conectá tu interfaz de audio USB, armá tu cadena de efectos y tocá con el sonido que quieras — todo desde una interfaz gráfica simple e intuitiva.

> **Autor:** Lucas Aguirre — [@LucasAguirre99](https://github.com/LucasAguirre99)
> **Licencia:** MIT

---

## Capturas de pantalla

> **Nota para colaboradores:** las capturas se encuentran en la carpeta `docs/screenshots/`.
> Si estás contribuyendo y mejorás la interfaz, actualizá las imágenes con `gnome-screenshot` o `scrot`.

### Vista principal — cadena vacía
![Vista principal](docs/screenshots/main_empty.png)

### Cadena de efectos con pedales activos
![Cadena con pedales](docs/screenshots/chain_active.png)

### Editor de parámetros
![Editor de parámetros](docs/screenshots/editor_params.png)

---

## Características

- **11 efectos en tiempo real**: Distorsión, Overdrive, Reverb, Delay, Chorus, Phaser, Compresor, Puerta de Ruido, Filtro de Agudos, Filtro de Graves, Pitch Shift y control de Volumen
- **Cadena de efectos configurable**: agregá, quitá y reordenás los pedales en cualquier momento mientras tocás
- **Editor de parámetros en vivo**: ajustás cada perilla con sliders que se aplican en tiempo real sin interrumpir el audio
- **Activar / desactivar pedales individualmente** sin sacarlos de la cadena
- **Selección de dispositivos de audio**: compatible con cualquier interfaz USB
- **Procesamiento de baja latencia** usando [pedalboard](https://github.com/spotify/pedalboard) de Spotify + [sounddevice](https://python-sounddevice.readthedocs.io/)

---

## Efectos disponibles

| Pedal | Parámetros |
|---|---|
| **Volumen** | Ganancia (dB) |
| **Distorsión** | Drive (dB) |
| **Overdrive** | Drive suave (dB) |
| **Reverb** | Tamaño de sala, Amortiguación, Efecto, Seco |
| **Delay** | Tiempo (s), Retroalimentación, Mezcla |
| **Chorus** | Velocidad (Hz), Profundidad, Mezcla |
| **Phaser** | Velocidad (Hz), Profundidad, Mezcla |
| **Compresor** | Umbral (dB), Ratio, Ataque (ms), Release (ms) |
| **Puerta de Ruido** | Umbral (dB), Ratio, Ataque (ms), Release (ms) |
| **Filtro Agudos** | Frecuencia de corte (Hz) |
| **Filtro Graves** | Frecuencia de corte (Hz) |
| **Pitch Shift** | Semitonos |

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

### Tips

- **Latencia:** si notás retraso, probá reducir el buffer a `128` o `64` (requiere interfaz de audio estable)
- **Ruido de fondo:** agregá una **Puerta de Ruido** al inicio de la cadena para eliminar el zumbido cuando no estás tocando
- **Sonido limpio:** un **Compresor** antes de la distorsión da un tono más profesional
- **El orden importa:** la señal pasa por los pedales de izquierda a derecha, igual que en un pedalboard físico

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
   git commit -m "feat: agregar efecto Wah-Wah"
   ```
4. **Pusheá tu rama:**
   ```bash
   git push origin feature/nombre-del-feature
   ```
5. **Abrí un Pull Request** en GitHub describiendo qué cambiaste y por qué

### Ideas para contribuir

- Soporte para Windows y macOS
- Guardar y cargar presets de cadenas de efectos
- Efectos adicionales: Wah, Fuzz, Tremolo, Vibrato, Looper
- Visualizador de forma de onda / espectro en tiempo real
- Control MIDI para los parámetros
- Interfaz gráfica con knobs (perillas) en lugar de sliders
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
├── guitar_pedalboard.py   # Aplicación principal
├── requirements.txt       # Dependencias de Python
├── LICENSE                # Licencia MIT
├── README.md              # Este archivo
└── docs/
    └── screenshots/       # Capturas de pantalla
```

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

Copyright (c) 2025 Lucas Aguirre — aguirrelucas.unrc@gmail.com
