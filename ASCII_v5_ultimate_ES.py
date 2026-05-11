"""
ASCII Art Video Player - Versión 5 (Ultimate / CLI)
====================================================
Versión completa con argparse CLI. Basado en el trabajo de @stepanussaruran.

Características:
  - argparse: todas las opciones vía línea de comandos
  - flag --color / --no-color
  - --width, --skip (salta cada N cuadros para mayor velocidad)
  - --loop para repetir el video
  - --info para mostrar solo la información del video sin reproducir
  - Hilo de decodificación en segundo plano (siempre activo)
  - Cierre seguro (Graceful shutdown)

Créditos Originales: stepanussaruran
Traducción al Español: Nicolas Romero (coralgamer) + Gemini 

=====================================================
ACTUALIZADO POR: CORALGAMER
AGREGADO BY: CORALGAMER
CHANGELOG:
- Traducción completa al español (Interfaz, Comentarios y Ayuda).
- Soporte para ajuste automático al tamaño de la terminal (Ancho y Alto).
- Implementación de relación de aspecto dinámica para evitar estiramientos.
- Barra de estado fija en la última línea de la terminal para evitar parpadeos.
- Mejoras en el modo interactivo (preguntas para Color, Ajuste, Bucle y Salto).
- Optimización de la lógica de renderizado dinámico.
=====================================================
""" 

import argparse
import cv2
import os
import sys
import time
import threading
import numpy as np
from queue import Queue, Empty

# ── Conjunto de 92 caracteres ──────────────────────────────────────────────────
ASCII_CHARS = (
    " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu"
    "[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"
)
_CHARS_ARRAY = np.array(list(ASCII_CHARS))

# ── Códigos de Escape ANSI ───────────────────────────────────────────────────
CURSOR_HOME  = "\033[H"
CLEAR_SCREEN = "\033[2J"
HIDE_CURSOR  = "\033[?25l"
SHOW_CURSOR  = "\033[?25h"
RESET_COLOR  = "\033[0m"

# ── Colores de texto para la interfaz ─────────────────────────────────────────
C_CYAN   = "\033[96m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_RED    = "\033[91m"
C_GRAY   = "\033[90m"
C_BOLD   = "\033[1m"


# ── Utilidades ───────────────────────────────────────────────────────────────

def enable_ansi_windows() -> None:
    """Activa los códigos de escape ANSI en Windows."""
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def get_video_info(cap: cv2.VideoCapture) -> dict:
    """Obtiene los metadatos del video."""
    return {
        "fps"          : cap.get(cv2.CAP_PROP_FPS),
        "total_frames" : int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "width_px"     : int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height_px"    : int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "duration_s"   : cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1),
    }


def print_info(video_path: str, info: dict) -> None:
    """Muestra la información del video en la terminal."""
    dur   = int(info["duration_s"])
    mins  = dur // 60
    secs  = dur % 60
    print(f"\n{C_BOLD}{C_CYAN}{'─' * 52}{RESET_COLOR}")
    print(f"  {C_BOLD}ASCII Video Player v5 — Edición Ultimate{RESET_COLOR}")
    print(f"{C_CYAN}{'─' * 52}{RESET_COLOR}")
    print(f"  {C_YELLOW}Archivo      {RESET_COLOR}: {os.path.basename(video_path)}")
    print(f"  {C_YELLOW}Resolución   {RESET_COLOR}: {info['width_px']} x {info['height_px']} px")
    print(f"  {C_YELLOW}FPS          {RESET_COLOR}: {info['fps']:.2f}")
    print(f"  {C_YELLOW}Duración     {RESET_COLOR}: {mins:02d}:{secs:02d} ({info['total_frames']} cuadros)")
    print(f"{C_CYAN}{'─' * 52}{RESET_COLOR}\n")


# ── Conversor de Cuadros (Frames) ─────────────────────────────────────────────

def frame_to_ascii_nocolor(frame, width: int) -> str:
    """Convierte un cuadro a ASCII sin color (más rápido)."""
    height = max(1, int(frame.shape[0] * width / frame.shape[1] / 2))
    resized = cv2.resize(frame, (width, height))
    gray    = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    n_chars = len(ASCII_CHARS) - 1
    lines = []
    for row in gray:
        line = "".join(ASCII_CHARS[int(p / 255.0 * n_chars)] for p in row)
        lines.append(line)
    return "\n".join(lines)


def frame_to_ascii_color(frame, width: int) -> str:
    """Convierte un cuadro a arte ASCII en color ANSI de 24 bits (vectorizado con numpy)."""
    height = max(1, int(frame.shape[0] * width / frame.shape[1] / 2))
    resized     = cv2.resize(frame, (width, height))
    resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

    r = resized_rgb[:, :, 0].astype(np.float32)
    g = resized_rgb[:, :, 1].astype(np.float32)
    b = resized_rgb[:, :, 2].astype(np.float32)

    brightness   = 0.299 * r + 0.587 * g + 0.114 * b
    char_indices = np.clip(
        (brightness / 255.0 * (len(ASCII_CHARS) - 1)).astype(np.int32),
        0, len(ASCII_CHARS) - 1
    )
    char_map = _CHARS_ARRAY[char_indices]

    lines = []
    for row_i in range(height):
        parts = []
        for col_i in range(width):
            rv = int(resized_rgb[row_i, col_i, 0])
            gv = int(resized_rgb[row_i, col_i, 1])
            bv = int(resized_rgb[row_i, col_i, 2])
            ch = char_map[row_i, col_i]
            parts.append(f"\033[38;2;{rv};{gv};{bv}m{ch}")
        parts.append(RESET_COLOR)
        lines.append("".join(parts))
    return "\n".join(lines)


# ── Hilo Decodificador en Segundo Plano ───────────────────────────────────────

def _frame_decoder(
    cap: cv2.VideoCapture,
    frame_queue: Queue,
    stop_event: threading.Event,
    skip: int
) -> None:
    """Hilo trabajador: lee cuadros del video hacia la cola saltando cuadros si se solicita."""
    frame_idx = 0
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        # Saltar cuadro si se solicita (para acelerar en PCs lentas)
        if skip > 1 and frame_idx % skip != 0:
            frame_idx += 1
            continue

        frame_idx += 1
        while not stop_event.is_set():
            try:
                frame_queue.put(frame, timeout=0.05)
                break
            except Exception:
                pass

    frame_queue.put(None)  # Centinela de fin


# ── Motor de Reproducción ─────────────────────────────────────────────────────

def play_video(
    video_path : str,
    width      : int  = None,
    use_color  : bool = False,
    skip       : int  = 1,
    loop       : bool = False,
    fit_screen : bool = True,
) -> None:
    """Motor principal de reproducción de video ASCII."""
    if not os.path.exists(video_path):
        print(f"{C_RED}[ERROR]{RESET_COLOR} Archivo no encontrado: '{video_path}'")
        sys.exit(1)

    enable_ansi_windows()
    converter = frame_to_ascii_color if use_color else frame_to_ascii_nocolor

    play_count = 0
    while True:
        play_count += 1
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"{C_RED}[ERROR]{RESET_COLOR} No se pudo abrir el video.")
            sys.exit(1)

        info        = get_video_info(cap)
        fps         = info["fps"] if info["fps"] > 0 else 30.0
        frame_delay = (1.0 / fps) * skip
        
        # Relación de aspecto original del video
        video_ar = info["width_px"] / info["height_px"]

        if play_count == 1:
            print_info(video_path, info)
            mode_str = f"{C_GREEN}COLOR (ANSI 24-bit){RESET_COLOR}" if use_color else f"{C_GRAY}BLANCO Y NEGRO{RESET_COLOR}"
            print(f"  Modo      : {mode_str}")
            print(f"  Ajuste    : {'Automático (Pantalla)' if fit_screen else f'{width} chars'}")
            print(f"  Salto     : cada {skip} cuadros")
            print(f"  Bucle     : {'Sí' if loop else 'No'}")
            print(f"\n{C_YELLOW}Iniciando en 2 segundos... Ctrl+C para detener.{RESET_COLOR}\n")
            time.sleep(2.0)

        # Decodificador en segundo plano
        frame_queue = Queue(maxsize=8)
        stop_event  = threading.Event()
        decoder     = threading.Thread(
            target=_frame_decoder,
            args=(cap, frame_queue, stop_event, skip),
            daemon=True
        )
        decoder.start()

        # Configuración de terminal
        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.flush()

        frame_count   = 0
        total_frames  = max(1, info["total_frames"] // skip)

        try:
            while True:
                t_start = time.perf_counter()

                try:
                    frame = frame_queue.get(timeout=2.0)
                except Empty:
                    break

                if frame is None:
                    break

                frame_count += 1
                
                # Calcular dimensiones dinámicas
                term_size = os.get_terminal_size()
                tw, th = term_size.columns, term_size.lines
                
                if fit_screen:
                    # th-2 para dejar espacio a la barra de progreso
                    available_h = max(1, th - 2)
                    available_w = tw
                    
                    # El factor 2.0 es porque los caracteres son más altos que anchos
                    # Calculamos el ancho necesario para llenar el alto disponible
                    w_from_h = int(available_h * video_ar * 2.0)
                    
                    # Elegimos el ancho que no se pase de ninguno de los dos límites
                    current_width = min(available_w, w_from_h)
                else:
                    current_width = width if width else 120

                ascii_art = converter(frame, current_width)

                # Renderizado
                sys.stdout.write(CURSOR_HOME)
                sys.stdout.write(ascii_art)

                # Barra de estado (siempre al final)
                progress = frame_count / total_frames
                bar_len  = max(10, tw - 45) # Barra dinámica
                filled   = int(bar_len * progress)
                bar      = "█" * filled + "░" * (bar_len - filled)
                loop_info = f" | Bucle #{play_count}" if loop else ""
                
                # Posicionar la barra al final de la terminal para evitar parpadeos
                sys.stdout.write(f"\033[{th};1H") 
                sys.stdout.write(
                    f"{RESET_COLOR}{C_GRAY}[{bar}] "
                    f"{frame_count}/{total_frames}{loop_info} | Ctrl+C{RESET_COLOR}"
                )
                sys.stdout.flush()

                # Temporización precisa
                elapsed    = time.perf_counter() - t_start
                sleep_time = frame_delay - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            stop_event.set()
            raise

        finally:
            stop_event.set()
            decoder.join(timeout=2.0)
            cap.release()

        if not loop:
            break

    # Restaurar terminal
    sys.stdout.write(SHOW_CURSOR)
    sys.stdout.write(RESET_COLOR)
    sys.stdout.write(f"\n\n{C_GREEN}[INFO]{RESET_COLOR} Reproducción finalizada.\n")
    sys.stdout.flush()


# ── Analizador de Argumentos CLI ──────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog        = "ASCII_v5_ultimate_ES.py",
        description = "ASCII Art Video Player - Edición Ultimate",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Ejemplos de uso:
  python ASCII_v5_ultimate_ES.py vid.mp4
  python ASCII_v5_ultimate_ES.py vid.mp4 --color --width 100
  python ASCII_v5_ultimate_ES.py vid.mp4 --no-fit --width 140 --loop
  python ASCII_v5_ultimate_ES.py vid.mp4 --color --skip 2
  python ASCII_v5_ultimate_ES.py vid.mp4 --info
"""
    )

    parser.add_argument(
        "video",
        nargs   = "?",
        default = None,
        help    = "Ruta al archivo de video (mp4, avi, mkv, etc.)"
    )
    parser.add_argument(
        "--width", "-w",
        type    = int,
        default = None,
        help    = "Ancho fijo en caracteres (desactiva el ajuste automático)"
    )

    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument(
        "--color", "-c",
        action  = "store_true",
        default = False,
        help    = "Activa color ANSI 24-bit"
    )
    color_group.add_argument(
        "--no-color",
        action  = "store_true",
        default = False,
        help    = "Fuerza el modo blanco y negro"
    )

    parser.add_argument(
        "--no-fit",
        action  = "store_false",
        dest    = "fit",
        default = True,
        help    = "Desactiva el ajuste automático al tamaño de la ventana"
    )

    parser.add_argument(
        "--skip", "-s",
        type    = int,
        default = 1,
        metavar = "N",
        help    = "Renderiza cada N cuadros"
    )
    parser.add_argument(
        "--loop", "-l",
        action  = "store_true",
        default = False,
        help    = "Repite el video continuamente"
    )
    parser.add_argument(
        "--info", "-i",
        action  = "store_true",
        default = False,
        help    = "Muestra solo la info del video"
    )

    return parser


# ── Punto de Entrada ─────────────────────────────────────────────────────────
def main() -> None:
    enable_ansi_windows()
    parser = build_parser()
    args   = parser.parse_args()

    # Si no hay argumentos, entrar en modo interactivo
    if args.video is None:
        print(f"\n{C_BOLD}{C_CYAN}{'─' * 52}{RESET_COLOR}")
        print(f"  {C_BOLD}ASCII Video Player v5 — Edición Ultimate{RESET_COLOR}")
        print(f"{C_CYAN}{'─' * 52}{RESET_COLOR}")
        print(f"\n  Para ver todas las opciones: {C_YELLOW}python ASCII_v5_ultimate_ES.py --help{RESET_COLOR}\n")

        args.video = input("  Introduce la ruta del video: ").strip().strip('"')
        if not args.video:
            print(f"{C_RED}[ERROR]{RESET_COLOR} La ruta del video no puede estar vacía.")
            sys.exit(1)

        color_input = input("  ¿Activar color? (s/N): ").strip().lower()
        args.color  = color_input == "s"

        fit_input = input("  ¿Ajustar automáticamente al tamaño de la terminal? (S/n): ").strip().lower()
        args.fit   = fit_input != "n"

        if not args.fit:
            term_cols = os.get_terminal_size().columns
            try:
                w = input(f"  Ancho de salida (default 120, terminal={term_cols}): ").strip()
                args.width = int(w) if w else 120
            except ValueError:
                args.width = 120

        try:
            s = input("  Saltar cada N cuadros (default 1 = todos los cuadros): ").strip()
            args.skip = int(s) if s else 1
        except ValueError:
            args.skip = 1

        loop_input = input("  ¿Repetir video? (s/N): ").strip().lower()
        args.loop   = loop_input == "s"

    # Si se especifica un ancho manualmente, desactivamos el fit automático por defecto
    if args.width is not None:
        args.fit = False

    # Validación
    if args.skip < 1:
        args.skip = 1

    # Modo solo información
    if args.info:
        if not os.path.exists(args.video):
            print(f"{C_RED}[ERROR]{RESET_COLOR} Archivo no encontrado: '{args.video}'")
            sys.exit(1)
        cap  = cv2.VideoCapture(args.video)
        info = get_video_info(cap)
        cap.release()
        print_info(args.video, info)
        return

    # Reproducir video
    try:
        play_video(
            video_path = args.video,
            width      = args.width,
            use_color  = args.color,
            skip       = args.skip,
            loop       = args.loop,
        )
    except KeyboardInterrupt:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(RESET_COLOR)
        print(f"\n\n{C_YELLOW}[INFO]{RESET_COLOR} Detenido por el usuario.\n")


if __name__ == "__main__":
    main()
