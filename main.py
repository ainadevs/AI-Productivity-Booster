import threading
import time
from wellbeing import WellbeingMonitor
from notifier import notify
from dashboard_mini import MiniDashboard

# Constantes
CHECK_INTERVAL_SECONDS = 60

# Instancia global del monitor
monitor = WellbeingMonitor()

def wellbeing_loop():
    """Loop principal que verifica el bienestar del usuario cada minuto"""
    while True:
        # Actualizar tiempo activo
        monitor.update_active_time()
        
        # Verificar si necesita descanso
        if monitor.needs_break():
            stats = monitor.get_stats()
            notify(
                "⏰ Hora de descansar",
                f"Has trabajado {stats['continuous_work_minutes']} minutos continuos.\n"
                "Se recomienda tomar un descanso de 10-15 minutos."
            )
            # Marcar que se notificó y esperar un descanso
            time.sleep(300)  # Esperar 5 minutos antes de volver a notificar
            
        time.sleep(CHECK_INTERVAL_SECONDS)

def start_monitoring():
    """Inicia el hilo de monitoreo de bienestar"""
    monitor_thread = threading.Thread(target=wellbeing_loop, daemon=True)
    monitor_thread.start()
    print("✓ Monitoreo de bienestar iniciado")
    stats = monitor.get_stats()
    print(f"  - Tiempo activo total: {stats['total_active_minutes']} minutos")
    print(f"  - Trabajo continuo: {stats['continuous_work_minutes']} minutos")

if __name__ == "__main__":
    print("\n🚀 Iniciando AI Productivity Booster...")
    print("-" * 50)
    
    # Iniciar monitoreo en segundo plano
    start_monitoring()
    
    # Abrir ventana de dashboard mini
    print("✓ Abriendo dashboard minimalista...")
    dashboard = MiniDashboard()
    dashboard.run()
