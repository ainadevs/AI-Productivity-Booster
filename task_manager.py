"""
Task Manager - Gestión Inteligente de Tareas y Priorización
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class Task:
    """Representa una tarea con metadatos"""
    def __init__(self, title, description="", priority="medium", deadline=None, 
                 estimated_time=30, task_type="general", tags=None):
        self.id = datetime.now().timestamp()
        self.title = title
        self.description = description
        self.priority = priority  # urgent, high, medium, low
        self.deadline = deadline
        self.estimated_time = estimated_time  # minutos
        self.task_type = task_type  # email, meeting, work, personal
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.completed = False
        self.completed_at = None
        self.postponed_count = 0
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'deadline': self.deadline,
            'estimated_time': self.estimated_time,
            'task_type': self.task_type,
            'tags': self.tags,
            'created_at': self.created_at,
            'completed': self.completed,
            'completed_at': self.completed_at,
            'postponed_count': self.postponed_count
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            deadline=data.get('deadline'),
            estimated_time=data.get('estimated_time', 30),
            task_type=data.get('task_type', 'general'),
            tags=data.get('tags', [])
        )
        task.id = data['id']
        task.created_at = data['created_at']
        task.completed = data.get('completed', False)
        task.completed_at = data.get('completed_at')
        task.postponed_count = data.get('postponed_count', 0)
        return task
    
    def get_priority_score(self):
        """Calcular puntuación de prioridad para ordenamiento"""
        priority_weights = {
            'urgent': 1000,
            'high': 100,
            'medium': 10,
            'low': 1
        }
        
        score = priority_weights.get(self.priority, 10)
        
        # Aumentar prioridad si hay deadline cercano
        if self.deadline:
            try:
                deadline_dt = datetime.fromisoformat(self.deadline)
                days_until = (deadline_dt - datetime.now()).days
                if days_until <= 0:
                    score *= 10  # Vencido
                elif days_until <= 1:
                    score *= 5   # Vence hoy/mañana
                elif days_until <= 3:
                    score *= 2   # Vence pronto
            except:
                pass
        
        # Penalizar si se ha pospuesto mucho
        score -= (self.postponed_count * 2)
        
        return score


class TaskManager:
    """Gestor de tareas con priorización inteligente"""
    
    def __init__(self, data_file='tasks.json'):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.user_state = {
            'current_activity': 'free',  # free, meeting, focused, break
            'focus_level': 'normal',  # high, normal, low
            'last_interruption': None
        }
        self.load_tasks()
        
    def load_tasks(self):
        """Cargar tareas desde archivo"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data.get('tasks', [])]
                    self.user_state = data.get('user_state', self.user_state)
            except Exception as e:
                print(f"Error cargando tareas: {e}")
                
    def save_tasks(self):
        """Guardar tareas a archivo"""
        try:
            data = {
                'tasks': [t.to_dict() for t in self.tasks],
                'user_state': self.user_state,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando tareas: {e}")
            
    def add_task(self, title, description="", priority="medium", deadline=None,
                 estimated_time=30, task_type="general", tags=None):
        """Añadir nueva tarea"""
        task = Task(title, description, priority, deadline, estimated_time, task_type, tags)
        self.tasks.append(task)
        self.save_tasks()
        return task
        
    def complete_task(self, task_id):
        """Marcar tarea como completada"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                task.completed_at = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False
        
    def postpone_task(self, task_id):
        """Posponer tarea (reduce prioridad temporalmente)"""
        for task in self.tasks:
            if task.id == task_id:
                task.postponed_count += 1
                self.save_tasks()
                return True
        return False
        
    def delete_task(self, task_id):
        """Eliminar tarea"""
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save_tasks()
        
    def get_pending_tasks(self, limit=None):
        """Obtener tareas pendientes ordenadas por prioridad"""
        pending = [t for t in self.tasks if not t.completed]
        pending.sort(key=lambda x: x.get_priority_score(), reverse=True)
        return pending[:limit] if limit else pending
        
    def get_tasks_by_priority(self, priority):
        """Obtener tareas por nivel de prioridad"""
        return [t for t in self.tasks if not t.completed and t.priority == priority]
        
    def get_urgent_tasks(self):
        """Obtener tareas urgentes que requieren atención inmediata"""
        urgent = []
        for task in self.tasks:
            if task.completed:
                continue
                
            # Tareas marcadas como urgentes
            if task.priority == 'urgent':
                urgent.append(task)
                continue
                
            # Tareas con deadline vencido o muy cercano
            if task.deadline:
                try:
                    deadline_dt = datetime.fromisoformat(task.deadline)
                    hours_until = (deadline_dt - datetime.now()).total_seconds() / 3600
                    if hours_until <= 4:  # Menos de 4 horas
                        urgent.append(task)
                except:
                    pass
                    
        return urgent
        
    def update_user_state(self, activity=None, focus_level=None):
        """Actualizar estado del usuario"""
        if activity:
            self.user_state['current_activity'] = activity
        if focus_level:
            self.user_state['focus_level'] = focus_level
        self.save_tasks()
        
    def should_interrupt(self, task):
        """Determinar si se debe interrumpir al usuario con esta tarea"""
        # No interrumpir si está en reunión
        if self.user_state['current_activity'] == 'meeting':
            return False
            
        # No interrumpir si está muy concentrado y la tarea no es urgente
        if self.user_state['focus_level'] == 'high' and task.priority != 'urgent':
            return False
            
        # Limitar frecuencia de interrupciones
        if self.user_state['last_interruption']:
            try:
                last_int = datetime.fromisoformat(self.user_state['last_interruption'])
                if (datetime.now() - last_int).total_seconds() < 600:  # 10 minutos
                    return task.priority == 'urgent'
            except:
                pass
                
        # Permitir interrupciones para tareas urgentes o de alta prioridad
        if task.priority in ['urgent', 'high']:
            self.user_state['last_interruption'] = datetime.now().isoformat()
            self.save_tasks()
            return True
            
        # Para tareas normales, solo si el usuario está libre
        if self.user_state['current_activity'] == 'free':
            return True
            
        return False
        
    def get_next_recommended_task(self):
        """Obtener la siguiente tarea recomendada según contexto"""
        pending = self.get_pending_tasks()
        if not pending:
            return None
            
        # Filtrar según el estado actual
        activity = self.user_state['current_activity']
        
        if activity == 'break':
            # Durante descanso, sugerir tareas cortas y sencillas
            short_tasks = [t for t in pending if t.estimated_time <= 15]
            return short_tasks[0] if short_tasks else None
            
        elif activity == 'focused':
            # Durante concentración, tareas que requieren más tiempo
            long_tasks = [t for t in pending if t.estimated_time >= 30]
            return long_tasks[0] if long_tasks else pending[0]
            
        else:  # free, normal
            # Devolver la de mayor prioridad
            return pending[0]
            
    def add_email_task(self, subject, sender, importance='normal'):
        """Añadir tarea de correo con priorización automática"""
        # Determinar prioridad basada en importancia del correo
        priority_map = {
            'high': 'high',
            'normal': 'medium',
            'low': 'low'
        }
        
        priority = priority_map.get(importance, 'medium')
        
        # Palabras clave que indican urgencia
        urgent_keywords = ['urgente', 'asap', 'inmediato', 'hoy', 'ahora']
        if any(kw in subject.lower() for kw in urgent_keywords):
            priority = 'urgent'
            
        title = f"📧 {subject[:50]}"
        description = f"De: {sender}"
        
        return self.add_task(
            title=title,
            description=description,
            priority=priority,
            task_type='email',
            estimated_time=10,
            tags=['email']
        )
        
    def get_stats(self):
        """Obtener estadísticas de tareas"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.completed])
        pending = total - completed
        
        by_priority = {
            'urgent': len(self.get_tasks_by_priority('urgent')),
            'high': len(self.get_tasks_by_priority('high')),
            'medium': len(self.get_tasks_by_priority('medium')),
            'low': len(self.get_tasks_by_priority('low'))
        }
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'by_priority': by_priority,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }


# Ejemplo de uso
if __name__ == "__main__":
    manager = TaskManager()
    
    # Añadir tareas de ejemplo
    manager.add_task(
        "Revisar propuesta de cliente",
        priority="high",
        estimated_time=45,
        deadline=(datetime.now() + timedelta(hours=2)).isoformat()
    )
    
    manager.add_task(
        "Actualizar documentación",
        priority="medium",
        estimated_time=60
    )
    
    manager.add_email_task(
        "Reunión urgente - Confirmar asistencia",
        "jefe@empresa.com",
        importance='high'
    )
    
    print("Tareas pendientes:")
    for task in manager.get_pending_tasks(5):
        print(f"  [{task.priority}] {task.title}")
        
    print("\nEstadísticas:")
    stats = manager.get_stats()
    print(f"  Total: {stats['total']}")
    print(f"  Pendientes: {stats['pending']}")
    print(f"  Completadas: {stats['completed']}")
