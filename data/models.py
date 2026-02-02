"""
Modelos de datos para AIProductivityBooster
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum


class TaskPriority(Enum):
    """Niveles de prioridad"""
    URGENT_IMPORTANT = 1      # Hacer ahora
    NOT_URGENT_IMPORTANT = 2  # Planificar
    URGENT_NOT_IMPORTANT = 3  # Delegar
    NOT_URGENT_NOT_IMPORTANT = 4  # Eliminar


class TaskStatus(Enum):
    """Estados de tarea"""
    PENDING = "pendiente"
    IN_PROGRESS = "en_progreso"
    COMPLETED = "completada"
    BLOCKED = "bloqueada"
    CANCELLED = "cancelada"


class TaskCategory(Enum):
    """Categorías de tareas"""
    CREATIVE = "creativo"
    ANALYTICAL = "analítico"
    ROUTINE = "rutinario"
    MEETING = "reunión"
    LEARNING = "aprendizaje"
    COMMUNICATION = "comunicación"
    BREAK = "descanso"


@dataclass
class Task:
    """Modelo de tarea mejorado"""
    id: str
    title: str
    description: str = ""
    category: TaskCategory = TaskCategory.ROUTINE
    priority: TaskPriority = TaskPriority.NOT_URGENT_IMPORTANT
    status: TaskStatus = TaskStatus.PENDING
    
    # Tiempo
    estimated_minutes: int = 30
    actual_minutes: int = 0
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Organización
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # IDs de tareas requeridas
    subtasks: List['Task'] = field(default_factory=list)
    
    # Contexto
    energy_level_required: int = 3  # 1-5, 5 = máxima energía requerida
    focus_required: int = 3  # 1-5, 5 = máximo foco requerido
    best_time_of_day: Optional[str] = None  # "morning", "afternoon", "evening"
    
    # Métricas
    times_postponed: int = 0
    importance_score: float = 0.5  # 0-1
    urgency_score: float = 0.5  # 0-1
    
    def calculate_priority_score(self) -> float:
        """Calcula un score de prioridad basado en múltiples factores"""
        score = 0.0
        
        # Factor de urgencia (40%)
        if self.deadline:
            days_until_deadline = (self.deadline - datetime.now()).days
            if days_until_deadline < 0:
                urgency = 1.0  # Vencida
            elif days_until_deadline == 0:
                urgency = 0.9  # Hoy
            elif days_until_deadline == 1:
                urgency = 0.7  # Mañana
            elif days_until_deadline <= 3:
                urgency = 0.5  # Esta semana
            else:
                urgency = max(0.1, 1.0 / days_until_deadline)
            score += urgency * 0.4
        
        # Factor de importancia (40%)
        score += self.importance_score * 0.4
        
        # Factor de tiempo estimado (10%) - tareas cortas tienen ventaja
        time_factor = 1.0 - min(self.estimated_minutes / 120, 1.0)
        score += time_factor * 0.1
        
        # Penalización por postergación (10%)
        postponement_penalty = min(self.times_postponed * 0.02, 0.1)
        score += postponement_penalty
        
        return min(score, 1.0)
    
    def is_ready(self, completed_task_ids: List[str]) -> bool:
        """Verifica si la tarea está lista para ejecutarse"""
        if self.status != TaskStatus.PENDING:
            return False
        
        # Verificar dependencias
        for dep_id in self.dependencies:
            if dep_id not in completed_task_ids:
                return False
        
        return True
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'estimated_minutes': self.estimated_minutes,
            'actual_minutes': self.actual_minutes,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'energy_level_required': self.energy_level_required,
            'focus_required': self.focus_required,
            'best_time_of_day': self.best_time_of_day,
            'times_postponed': self.times_postponed,
            'importance_score': self.importance_score,
            'urgency_score': self.urgency_score
        }


@dataclass
class CalendarEvent:
    """Evento de calendario"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    location: str = ""
    attendees: List[str] = field(default_factory=list)
    is_all_day: bool = False
    source: str = "manual"  # "google", "outlook", "manual"
    
    def duration_minutes(self) -> int:
        """Duración en minutos"""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def conflicts_with(self, other: 'CalendarEvent') -> bool:
        """Verifica si hay conflicto con otro evento"""
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)


@dataclass
class TimeSlot:
    """Hueco de tiempo disponible"""
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    energy_level: int = 3  # Nivel de energía esperado en este slot
    
    def can_fit_task(self, task: Task) -> bool:
        """Verifica si una tarea cabe en este slot"""
        return self.duration_minutes >= task.estimated_minutes


@dataclass
class ProductivityPattern:
    """Patrón de productividad del usuario"""
    user_id: str
    hour_of_day: int  # 0-23
    day_of_week: int  # 0-6 (lunes-domingo)
    avg_focus_level: float = 0.5  # 0-1
    avg_energy_level: float = 0.5  # 0-1
    tasks_completed: int = 0
    tasks_started: int = 0
    preferred_categories: List[TaskCategory] = field(default_factory=list)
    
    def is_good_time_for_category(self, category: TaskCategory) -> bool:
        """Determina si es buen momento para una categoría"""
        return category in self.preferred_categories


@dataclass
class WorkSession:
    """Sesión de trabajo"""
    id: str
    task_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    breaks_taken: int = 0
    focus_score: float = 0.0  # 0-1, medido por actividad
    interruptions: int = 0
    notes: str = ""
    
    def duration_minutes(self) -> int:
        """Duración en minutos"""
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return int((datetime.now() - self.start_time).total_seconds() / 60)
