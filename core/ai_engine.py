"""
Motor de IA para priorización inteligente de tareas
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from data.models import Task, CalendarEvent, TimeSlot, TaskStatus, TaskCategory
from data.database import Database


class AITaskPrioritizer:
    """Motor de priorización inteligente"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_next_task_recommendation(self, 
                                     available_minutes: int = 60,
                                     current_energy: int = 3) -> Optional[Tuple[Task, str]]:
        """
        Recomienda la siguiente tarea a realizar
        
        Returns:
            Tupla de (Task, razón) o None si no hay tareas
        """
        # Obtener tareas pendientes
        pending_tasks = self.db.get_all_tasks(status=TaskStatus.PENDING)
        
        if not pending_tasks:
            return None
        
        # Obtener IDs de tareas completadas para verificar dependencias
        completed_tasks = self.db.get_all_tasks(status=TaskStatus.COMPLETED)
        completed_ids = [t.id for t in completed_tasks]
        
        # Filtrar tareas que están listas (sin dependencias bloqueadas)
        ready_tasks = [t for t in pending_tasks if t.is_ready(completed_ids)]
        
        if not ready_tasks:
            return None
        
        # Filtrar por tiempo disponible
        fitting_tasks = [t for t in ready_tasks if t.estimated_minutes <= available_minutes]
        
        if not fitting_tasks:
            # Si no caben tareas, recomendar la más corta
            shortest = min(ready_tasks, key=lambda t: t.estimated_minutes)
            reason = f"No tienes suficiente tiempo. Necesitas {shortest.estimated_minutes} min para la tarea más corta."
            return (shortest, reason)
        
        # Filtrar por nivel de energía
        energy_suitable_tasks = [t for t in fitting_tasks 
                                if t.energy_level_required <= current_energy]
        
        if not energy_suitable_tasks:
            energy_suitable_tasks = fitting_tasks  # Usar todas si no hay coincidencias
        
        # Calcular scores y ordenar
        scored_tasks = []
        for task in energy_suitable_tasks:
            score = self._calculate_comprehensive_score(task, current_energy, available_minutes)
            scored_tasks.append((task, score))
        
        # Ordenar por score descendente
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        
        # La mejor tarea
        best_task, best_score = scored_tasks[0]
        
        # Generar razón
        reason = self._generate_recommendation_reason(best_task, available_minutes, current_energy)
        
        return (best_task, reason)
    
    def _calculate_comprehensive_score(self, task: Task, current_energy: int, available_minutes: int) -> float:
        """Calcula un score comprensivo para la tarea"""
        score = 0.0
        
        # Score base de prioridad (40%)
        priority_score = task.calculate_priority_score()
        score += priority_score * 0.4
        
        # Score de energía (20%)
        energy_match = 1.0 - abs(task.energy_level_required - current_energy) / 5.0
        score += energy_match * 0.2
        
        # Score de tiempo (20%)
        time_utilization = min(task.estimated_minutes / available_minutes, 1.0)
        score += time_utilization * 0.2
        
        # Score de momento del día (10%)
        current_hour = datetime.now().hour
        time_of_day_score = self._get_time_of_day_score(task, current_hour)
        score += time_of_day_score * 0.1
        
        # Score de categoría (10%) - priorizar tareas creativas/analíticas en horas pico
        category_score = self._get_category_score(task, current_hour)
        score += category_score * 0.1
        
        return score
    
    def _get_time_of_day_score(self, task: Task, current_hour: int) -> float:
        """Evalúa qué tan bien coincide el momento del día con la tarea"""
        if not task.best_time_of_day:
            return 0.5  # Neutral si no hay preferencia
        
        if task.best_time_of_day == "morning" and 6 <= current_hour < 12:
            return 1.0
        elif task.best_time_of_day == "afternoon" and 12 <= current_hour < 18:
            return 1.0
        elif task.best_time_of_day == "evening" and 18 <= current_hour < 23:
            return 1.0
        else:
            return 0.3  # Penalización si no es el mejor momento
    
    def _get_category_score(self, task: Task, current_hour: int) -> float:
        """Evalúa qué tan apropiada es la categoría para la hora actual"""
        # Horas pico de energía (mañana): mejor para tareas creativas/analíticas
        if 9 <= current_hour < 12:
            if task.category in [TaskCategory.CREATIVE, TaskCategory.ANALYTICAL]:
                return 1.0
            elif task.category == TaskCategory.ROUTINE:
                return 0.5
        
        # Post-comida (tarde): mejor para tareas rutinarias
        elif 14 <= current_hour < 16:
            if task.category == TaskCategory.ROUTINE:
                return 1.0
            elif task.category in [TaskCategory.CREATIVE, TaskCategory.ANALYTICAL]:
                return 0.6
        
        # Tarde: bueno para reuniones y comunicación
        elif 16 <= current_hour < 18:
            if task.category in [TaskCategory.MEETING, TaskCategory.COMMUNICATION]:
                return 1.0
        
        return 0.7  # Score neutral por defecto
    
    def _generate_recommendation_reason(self, task: Task, available_minutes: int, current_energy: int) -> str:
        """Genera una explicación humana de por qué se recomienda esta tarea"""
        reasons = []
        
        # Razón por prioridad
        priority_score = task.calculate_priority_score()
        if priority_score > 0.8:
            reasons.append("es muy urgente o importante")
        elif priority_score > 0.6:
            reasons.append("tiene alta prioridad")
        
        # Razón por deadline
        if task.deadline:
            days_until = (task.deadline - datetime.now()).days
            if days_until < 0:
                reasons.append("está vencida")
            elif days_until == 0:
                reasons.append("vence hoy")
            elif days_until == 1:
                reasons.append("vence mañana")
            elif days_until <= 3:
                reasons.append(f"vence en {days_until} días")
        
        # Razón por tiempo
        if task.estimated_minutes <= available_minutes * 0.5:
            reasons.append(f"es corta ({task.estimated_minutes} min)")
        
        # Razón por energía
        if task.energy_level_required <= current_energy:
            reasons.append("se ajusta a tu nivel de energía actual")
        
        # Razón por momento del día
        current_hour = datetime.now().hour
        if task.best_time_of_day:
            if (task.best_time_of_day == "morning" and 6 <= current_hour < 12) or \
               (task.best_time_of_day == "afternoon" and 12 <= current_hour < 18) or \
               (task.best_time_of_day == "evening" and 18 <= current_hour < 23):
                reasons.append("es el mejor momento del día para esta tarea")
        
        if not reasons:
            return "Es una buena opción para este momento."
        
        return "Te la recomiendo porque " + ", ".join(reasons) + "."
    
    def find_time_slots(self, date: datetime, min_duration_minutes: int = 30) -> List[TimeSlot]:
        """
        Encuentra huecos de tiempo libre en un día
        
        Args:
            date: Día a analizar
            min_duration_minutes: Duración mínima del hueco
            
        Returns:
            Lista de TimeSlots disponibles
        """
        # Obtener eventos del día
        events = self.db.get_events_for_date(date)
        
        if not events:
            # Día completamente libre
            start = date.replace(hour=8, minute=0, second=0)
            end = date.replace(hour=20, minute=0, second=0)
            duration = int((end - start).total_seconds() / 60)
            return [TimeSlot(start, end, duration)]
        
        # Ordenar eventos por hora de inicio
        events.sort(key=lambda e: e.start_time)
        
        slots = []
        day_start = date.replace(hour=8, minute=0, second=0)
        day_end = date.replace(hour=20, minute=0, second=0)
        
        # Hueco antes del primer evento
        if events[0].start_time > day_start:
            duration = int((events[0].start_time - day_start).total_seconds() / 60)
            if duration >= min_duration_minutes:
                slots.append(TimeSlot(day_start, events[0].start_time, duration))
        
        # Huecos entre eventos
        for i in range(len(events) - 1):
            gap_start = events[i].end_time
            gap_end = events[i + 1].start_time
            duration = int((gap_end - gap_start).total_seconds() / 60)
            
            if duration >= min_duration_minutes:
                slots.append(TimeSlot(gap_start, gap_end, duration))
        
        # Hueco después del último evento
        if events[-1].end_time < day_end:
            duration = int((day_end - events[-1].end_time).total_seconds() / 60)
            if duration >= min_duration_minutes:
                slots.append(TimeSlot(events[-1].end_time, day_end, duration))
        
        return slots
    
    def suggest_task_for_slot(self, slot: TimeSlot) -> Optional[Tuple[Task, str]]:
        """Sugiere una tarea para un hueco de tiempo específico"""
        # Estimar nivel de energía basado en la hora
        hour = slot.start_time.hour
        if 8 <= hour < 12:
            energy = 5  # Mañana: máxima energía
        elif 12 <= hour < 14:
            energy = 3  # Mediodía: energía media
        elif 14 <= hour < 16:
            energy = 2  # Post-comida: baja energía
        elif 16 <= hour < 18:
            energy = 4  # Tarde: energía recuperada
        else:
            energy = 3  # Noche: energía media
        
        return self.get_next_task_recommendation(
            available_minutes=slot.duration_minutes,
            current_energy=energy
        )
    
    def plan_day(self, date: datetime) -> List[Tuple[TimeSlot, Optional[Task], str]]:
        """
        Planifica un día completo con tareas sugeridas
        
        Returns:
            Lista de (TimeSlot, Task sugerida, razón)
        """
        slots = self.find_time_slots(date)
        plan = []
        
        for slot in slots:
            suggestion = self.suggest_task_for_slot(slot)
            if suggestion:
                task, reason = suggestion
                plan.append((slot, task, reason))
            else:
                plan.append((slot, None, "No hay tareas pendientes para este hueco."))
        
        return plan
