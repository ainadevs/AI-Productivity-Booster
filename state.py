import time
import threading

class AppState:
    """Gestiona el estado global de la aplicación de forma thread-safe"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._last_active = time.time()
        self._last_break = time.time()
        self._pending_tasks = []
    
    def update_last_active(self):
        """Actualiza el timestamp de última actividad"""
        with self._lock:
            self._last_active = time.time()
    
    def get_last_active(self):
        """Obtiene el timestamp de última actividad"""
        with self._lock:
            return self._last_active
    
    def reset_break_timer(self):
        """Reinicia el timer del último descanso"""
        with self._lock:
            self._last_break = time.time()
    
    def is_user_active(self):
        """Verifica si el usuario está activo recientemente (últimos 60 segundos)"""
        with self._lock:
            return (time.time() - self._last_active) < 60
    
    def get_working_time(self):
        """Calcula el tiempo transcurrido desde el último descanso"""
        with self._lock:
            return time.time() - self._last_break
    
    def register_break(self):
        """Registra que el usuario tomó un descanso"""
        with self._lock:
            self._last_break = time.time()
    
    def get_last_break(self):
        """Obtiene el timestamp del último descanso"""
        with self._lock:
            return self._last_break
    
    def add_pending_task(self, task):
        """Añade una tarea pendiente"""
        with self._lock:
            self._pending_tasks.append(task)
    
    def get_pending_tasks(self):
        """Obtiene la lista de tareas pendientes"""
        with self._lock:
            return self._pending_tasks.copy()
    
    def clear_pending_tasks(self):
        """Limpia todas las tareas pendientes"""
        with self._lock:
            self._pending_tasks.clear()

# Instancia global del estado
state = AppState()
