"""
Base de datos SQLite para AIProductivityBooster
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from data.models import Task, CalendarEvent, WorkSession, ProductivityPattern, TaskStatus, TaskCategory, TaskPriority


class Database:
    """Gestor de base de datos"""
    
    def __init__(self, db_path: str = "data/productivity.db"):
        self.db_path = db_path
        Path("data").mkdir(exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Obtiene conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de tareas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority INTEGER,
                status TEXT,
                estimated_minutes INTEGER,
                actual_minutes INTEGER,
                deadline TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                tags TEXT,
                dependencies TEXT,
                energy_level_required INTEGER,
                focus_required INTEGER,
                best_time_of_day TEXT,
                times_postponed INTEGER,
                importance_score REAL,
                urgency_score REAL
            )
        ''')
        
        # Tabla de eventos de calendario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                description TEXT,
                location TEXT,
                attendees TEXT,
                is_all_day INTEGER,
                source TEXT
            )
        ''')
        
        # Tabla de sesiones de trabajo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_sessions (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                start_time TEXT,
                end_time TEXT,
                breaks_taken INTEGER,
                focus_score REAL,
                interruptions INTEGER,
                notes TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')
        
        # Tabla de patrones de productividad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productivity_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                hour_of_day INTEGER,
                day_of_week INTEGER,
                avg_focus_level REAL,
                avg_energy_level REAL,
                tasks_completed INTEGER,
                tasks_started INTEGER,
                preferred_categories TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # === OPERACIONES CON TAREAS ===
    
    def add_task(self, task: Task) -> bool:
        """Agrega una nueva tarea"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.id,
                task.title,
                task.description,
                task.category.value,
                task.priority.value,
                task.status.value,
                task.estimated_minutes,
                task.actual_minutes,
                task.deadline.isoformat() if task.deadline else None,
                task.created_at.isoformat(),
                task.started_at.isoformat() if task.started_at else None,
                task.completed_at.isoformat() if task.completed_at else None,
                json.dumps(task.tags),
                json.dumps(task.dependencies),
                task.energy_level_required,
                task.focus_required,
                task.best_time_of_day,
                task.times_postponed,
                task.importance_score,
                task.urgency_score
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al agregar tarea: {e}")
            return False
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """Obtiene todas las tareas, opcionalmente filtradas por estado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM tasks WHERE status = ?', (status.value,))
        else:
            cursor.execute('SELECT * FROM tasks')
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append(self._row_to_task(row))
        
        conn.close()
        return tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Obtiene una tarea por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return self._row_to_task(row)
        return None
    
    def update_task(self, task: Task) -> bool:
        """Actualiza una tarea existente"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks SET
                    title = ?, description = ?, category = ?, priority = ?, status = ?,
                    estimated_minutes = ?, actual_minutes = ?, deadline = ?,
                    started_at = ?, completed_at = ?, tags = ?, dependencies = ?,
                    energy_level_required = ?, focus_required = ?, best_time_of_day = ?,
                    times_postponed = ?, importance_score = ?, urgency_score = ?
                WHERE id = ?
            ''', (
                task.title, task.description, task.category.value, task.priority.value,
                task.status.value, task.estimated_minutes, task.actual_minutes,
                task.deadline.isoformat() if task.deadline else None,
                task.started_at.isoformat() if task.started_at else None,
                task.completed_at.isoformat() if task.completed_at else None,
                json.dumps(task.tags), json.dumps(task.dependencies),
                task.energy_level_required, task.focus_required, task.best_time_of_day,
                task.times_postponed, task.importance_score, task.urgency_score,
                task.id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al actualizar tarea: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Elimina una tarea"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al eliminar tarea: {e}")
            return False
    
    def _row_to_task(self, row) -> Task:
        """Convierte una fila de BD a objeto Task"""
        return Task(
            id=row[0],
            title=row[1],
            description=row[2] or "",
            category=TaskCategory(row[3]),
            priority=TaskPriority(row[4]),
            status=TaskStatus(row[5]),
            estimated_minutes=row[6],
            actual_minutes=row[7],
            deadline=datetime.fromisoformat(row[8]) if row[8] else None,
            created_at=datetime.fromisoformat(row[9]),
            started_at=datetime.fromisoformat(row[10]) if row[10] else None,
            completed_at=datetime.fromisoformat(row[11]) if row[11] else None,
            tags=json.loads(row[12]) if row[12] else [],
            dependencies=json.loads(row[13]) if row[13] else [],
            energy_level_required=row[14],
            focus_required=row[15],
            best_time_of_day=row[16],
            times_postponed=row[17],
            importance_score=row[18],
            urgency_score=row[19]
        )
    
    # === OPERACIONES CON EVENTOS ===
    
    def add_calendar_event(self, event: CalendarEvent) -> bool:
        """Agrega un evento de calendario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO calendar_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.id,
                event.title,
                event.start_time.isoformat(),
                event.end_time.isoformat(),
                event.description,
                event.location,
                json.dumps(event.attendees),
                1 if event.is_all_day else 0,
                event.source
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al agregar evento: {e}")
            return False
    
    def get_events_for_date(self, date: datetime) -> List[CalendarEvent]:
        """Obtiene eventos para una fecha específica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_of_day = date.replace(hour=0, minute=0, second=0)
        end_of_day = date.replace(hour=23, minute=59, second=59)
        
        cursor.execute('''
            SELECT * FROM calendar_events 
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time
        ''', (start_of_day.isoformat(), end_of_day.isoformat()))
        
        events = []
        for row in cursor.fetchall():
            events.append(self._row_to_event(row))
        
        conn.close()
        return events
    
    def _row_to_event(self, row) -> CalendarEvent:
        """Convierte una fila de BD a objeto CalendarEvent"""
        return CalendarEvent(
            id=row[0],
            title=row[1],
            start_time=datetime.fromisoformat(row[2]),
            end_time=datetime.fromisoformat(row[3]),
            description=row[4] or "",
            location=row[5] or "",
            attendees=json.loads(row[6]) if row[6] else [],
            is_all_day=bool(row[7]),
            source=row[8]
        )
    
    # === OPERACIONES CON SESIONES ===
    
    def add_work_session(self, session: WorkSession) -> bool:
        """Agrega una sesión de trabajo"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO work_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.id,
                session.task_id,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else None,
                session.breaks_taken,
                session.focus_score,
                session.interruptions,
                session.notes
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al agregar sesión: {e}")
            return False
    
    def get_sessions_for_task(self, task_id: str) -> List[WorkSession]:
        """Obtiene todas las sesiones de una tarea"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM work_sessions WHERE task_id = ?', (task_id,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append(self._row_to_session(row))
        
        conn.close()
        return sessions
    
    def _row_to_session(self, row) -> WorkSession:
        """Convierte una fila de BD a objeto WorkSession"""
        return WorkSession(
            id=row[0],
            task_id=row[1],
            start_time=datetime.fromisoformat(row[2]),
            end_time=datetime.fromisoformat(row[3]) if row[3] else None,
            breaks_taken=row[4],
            focus_score=row[5],
            interruptions=row[6],
            notes=row[7] or ""
        )
