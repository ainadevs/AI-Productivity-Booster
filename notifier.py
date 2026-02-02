"""
Sistema de Notificaciones - Gestión de alertas al usuario
"""
import sys

class NotificationManager:
    def __init__(self):
        self.notifier = None
        self._init_notifier()
        
    def _init_notifier(self):
        """Inicializar el sistema de notificaciones"""
        try:
            # Intentar winotify primero (Windows 10+)
            from winotify import Notification, audio
            self.notifier = 'winotify'
            self.winotify_module = Notification
            self.audio_module = audio
            print("✓ Notificaciones: winotify")
        except ImportError:
            try:
                # Fallback a win10toast
                from win10toast import ToastNotifier
                self.notifier = 'win10toast'
                self.toast = ToastNotifier()
                print("✓ Notificaciones: win10toast")
            except ImportError:
                # Fallback a consola
                self.notifier = 'console'
                print("⚠ Notificaciones: consola (instala winotify o win10toast)")
                
    def send_notification(self, title, message, icon=None):
        """Enviar notificación"""
        try:
            if self.notifier == 'winotify':
                toast = self.winotify_module(
                    app_id="AI Productivity Booster",
                    title=title,
                    msg=message,
                    duration="short"
                )
                
                if icon:
                    toast.set_audio(self.audio_module.Default, loop=False)
                    
                toast.show()
                
            elif self.notifier == 'win10toast':
                self.toast.show_toast(
                    title,
                    message,
                    duration=5,
                    threaded=True
                )
                
            else:
                # Fallback a consola
                print(f"\n{'='*50}")
                print(f"📢 {title}")
                print(f"{message}")
                print(f"{'='*50}\n")
                
        except Exception as e:
            print(f"⚠ Error enviando notificación: {e}")
            print(f"📢 {title}: {message}")
            
    def send_break_reminder(self, minutes_worked):
        """Enviar recordatorio de descanso"""
        self.send_notification(
            "⏰ Tiempo de Descanso",
            f"Llevas {minutes_worked} minutos trabajando.\n¿Qué tal un pequeño descanso?"
        )
        
    def send_posture_reminder(self):
        """Enviar recordatorio de postura"""
        self.send_notification(
            "🪑 Revisa tu Postura",
            "Recuerda mantener la espalda recta y los hombros relajados."
        )
        
    def send_stretch_reminder(self):
        """Enviar recordatorio de estiramiento"""
        self.send_notification(
            "🤸 Hora de Estirarse",
            "Levántate y haz algunos estiramientos. Tu cuerpo te lo agradecerá."
        )
        
    def send_hydration_reminder(self):
        """Enviar recordatorio de hidratación"""
        self.send_notification(
            "💧 Hidrátate",
            "No olvides beber agua. Mantente hidratado."
        )
        
    def send_achievement(self, message):
        """Enviar notificación de logro"""
        self.send_notification(
            "🏆 ¡Logro Desbloqueado!",
            message
        )

def notify(message, title="AI Productivity Booster"):
    """Función simple para enviar notificación"""
    manager = NotificationManager()
    manager.send_notification(title, message)
