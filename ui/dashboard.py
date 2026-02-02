"""
Dashboard Widget Premium HD - Ventana lateral con información de productividad
Diseño moderno y minimalista de alta calidad con soporte DPI alto y gestión de tareas
"""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import threading
import time
from datetime import datetime
from wellbeing import WellbeingMonitor
from notifier import NotificationManager
from task_manager import TaskManager
import ctypes

class ProductivityDashboard:
    def __init__(self):
        # Habilitar DPI alto para mejor calidad visual en Windows
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass
        
        self.root = tk.Tk()
        self.root.title("AI Productivity Booster")
        
        # Configurar icono de la aplicación
        try:
            self.root.iconbitmap('app_icon.ico')
        except:
            pass  # Si no se encuentra el icono, usar el predeterminado
        
        # Configuración de la ventana
        self.collapsed_width = 320
        self.expanded_width = 700
        self.collapsed_height = 120
        self.expanded_height = 600
        
        # Posicionar en el lado izquierdo de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = 15  # Margen izquierdo
        y = 40
        
        self.root.geometry(f"{self.collapsed_width}x{self.collapsed_height}+{x}+{y}")
        
        # Configuración de estilo premium
        self.root.configure(bg='#0a0e27')
        
        # Efectos visuales
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.97)
        
        # Componentes
        self.monitor = WellbeingMonitor()
        self.notifier = NotificationManager()
        self.task_manager = TaskManager()
        
        # Estado
        self.expanded = False
        self.running = True
        self.dragging = False
        self.drag_x = 0
        self.drag_y = 0
        
        # Crear interfaz
        self.create_widgets()
        
        # Iniciar actualización
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Mostrar bienvenida y notificación inicial
        self.root.after(500, self.show_welcome)
        
    def create_widgets(self):
        """Crear interfaz premium"""
        
        # Container principal
        container = tk.Frame(self.root, bg='#0f172a')
        container.pack(fill=tk.BOTH, expand=True)
        
        # Borde superior
        top_border = tk.Frame(container, bg='#6366f1', height=4)
        top_border.pack(fill=tk.X)
        
        # === HEADER ===
        header = tk.Frame(container, bg='#1e293b')
        header.pack(fill=tk.X)
        
        header.bind('<Button-1>', self.start_drag)
        header.bind('<B1-Motion>', self.on_drag)
        header.bind('<ButtonRelease-1>', self.stop_drag)
        
        # Container del título
        title_container = tk.Frame(header, bg='#1e293b')
        title_container.pack(fill=tk.X, padx=14, pady=12)
        
        # Icono y título
        title_frame = tk.Frame(title_container, bg='#1e293b')
        title_frame.pack(side=tk.LEFT)
        
        title = tk.Label(
            title_frame,
            text="⚡ AI Productivity",
            font=('Segoe UI', 11, 'bold'),
            bg='#1e293b',
            fg='#818cf8',
            cursor='fleur'
        )
        title.pack(side=tk.LEFT)
        title.bind('<Button-1>', self.start_drag)
        title.bind('<B1-Motion>', self.on_drag)
        title.bind('<ButtonRelease-1>', self.stop_drag)
        
        # Badge de estado
        self.status_badge = tk.Label(
            title_frame,
            text="●",
            font=('Segoe UI', 10),
            bg='#1e293b',
            fg='#10b981',
            padx=5
        )
        self.status_badge.pack(side=tk.LEFT)
        
        # Botones de control
        btn_frame = tk.Frame(title_container, bg='#1e293b')
        btn_frame.pack(side=tk.RIGHT)
        
        # Botón expandir/contraer
        self.toggle_btn = tk.Button(
            btn_frame,
            text="◀",
            command=self.toggle_expand,
            font=('Segoe UI', 10, 'bold'),
            bg='#334155',
            fg='#94a3b8',
            activebackground='#475569',
            activeforeground='#818cf8',
            relief=tk.FLAT,
            cursor='hand2',
            width=3,
            height=1,
            bd=0
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=2)
        
        # Botón cerrar
        close_btn = tk.Button(
            btn_frame,
            text="✕",
            command=self.on_closing,
            font=('Segoe UI', 11, 'bold'),
            bg='#334155',
            fg='#94a3b8',
            activebackground='#ef4444',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            width=3,
            height=1,
            bd=0
        )
        close_btn.pack(side=tk.LEFT)
        
        # === CONTENIDO EXPANDIBLE ===
        self.content_frame = tk.Frame(container, bg='#0f172a')
        
        # Tiempo trabajado
        self.create_work_time_section(self.content_frame)
        
        # Separador
        tk.Frame(self.content_frame, bg='#334155', height=1).pack(fill=tk.X, padx=12, pady=10)
        
        # Estado y progreso
        self.create_status_section(self.content_frame)
        
        # Separador
        tk.Frame(self.content_frame, bg='#334155', height=1).pack(fill=tk.X, padx=12, pady=10)
        
        # Tareas pendientes
        self.create_tasks_section(self.content_frame)
        
        # Botones de acción
        self.create_action_buttons(self.content_frame)
        
    def create_work_time_section(self, parent):
        """Sección de tiempo trabajado"""
        section = tk.Frame(parent, bg='#0f172a')
        section.pack(fill=tk.X, padx=12, pady=10)
        
        # Card de tiempo trabajado
        card = tk.Frame(section, bg='#1e293b', highlightbackground='#334155', highlightthickness=1)
        card.pack(fill=tk.X)
        
        # Icono
        tk.Label(
            card,
            text="⏰",
            font=('Segoe UI', 18),
            bg='#1e293b',
            fg='#818cf8'
        ).pack(pady=(12, 0))
        
        # Label
        tk.Label(
            card,
            text="Tiempo Trabajado",
            font=('Segoe UI', 9),
            bg='#1e293b',
            fg='#64748b'
        ).pack()
        
        # Valor
        self.work_time_label = tk.Label(
            card,
            text="0h 0m",
            font=('Segoe UI', 16, 'bold'),
            bg='#1e293b',
            fg='#818cf8'
        )
        self.work_time_label.pack(pady=(4, 12))
        
    def create_status_section(self, parent):
        """Sección de estado con barra de progreso"""
        section = tk.Frame(parent, bg='#0f172a')
        section.pack(fill=tk.X, padx=12)
        
        # Título
        tk.Label(
            section,
            text="📊 Estado de Productividad",
            font=('Segoe UI', 9, 'bold'),
            bg='#0f172a',
            fg='#94a3b8',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Estado actual
        self.status_label = tk.Label(
            section,
            text="● Buen ritmo de trabajo",
            font=('Segoe UI', 10, 'bold'),
            bg='#0f172a',
            fg='#10b981',
            anchor='w'
        )
        self.status_label.pack(fill=tk.X)
        
        # Barra de progreso
        progress_container = tk.Frame(section, bg='#1e293b', height=10)
        progress_container.pack(fill=tk.X, pady=(8, 0))
        progress_container.pack_propagate(False)
        
        self.progress_bar = tk.Frame(progress_container, bg='#818cf8', width=0)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.Y)
        
    def create_tasks_section(self, parent):
        """Sección de tareas pendientes"""
        section = tk.Frame(parent, bg='#0f172a')
        section.pack(fill=tk.BOTH, expand=True, padx=12)
        
        # Header de tareas con contador
        header_frame = tk.Frame(section, bg='#0f172a')
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            header_frame,
            text="📋 Tareas Pendientes",
            font=('Segoe UI', 9, 'bold'),
            bg='#0f172a',
            fg='#94a3b8',
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.task_count_label = tk.Label(
            header_frame,
            text="(0)",
            font=('Segoe UI', 8),
            bg='#0f172a',
            fg='#64748b',
            anchor='w'
        )
        self.task_count_label.pack(side=tk.LEFT, padx=5)
        
        # Botón añadir tarea
        add_task_btn = tk.Button(
            header_frame,
            text="+",
            command=self.add_task_dialog,
            font=('Segoe UI', 10, 'bold'),
            bg='#334155',
            fg='#10b981',
            activebackground='#475569',
            activeforeground='#10b981',
            relief=tk.FLAT,
            cursor='hand2',
            width=2,
            bd=0
        )
        add_task_btn.pack(side=tk.RIGHT)
        
        # Container de tareas con scroll
        tasks_container = tk.Frame(section, bg='#1e293b', highlightbackground='#334155', highlightthickness=1)
        tasks_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scroll
        canvas = tk.Canvas(tasks_container, bg='#1e293b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tasks_container, orient="vertical", command=canvas.yview)
        
        self.tasks_frame = tk.Frame(canvas, bg='#1e293b')
        
        self.tasks_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tasks_canvas = canvas
        
    def create_action_buttons(self, parent):
        """Botones de acción"""
        btn_container = tk.Frame(parent, bg='#0f172a')
        btn_container.pack(fill=tk.X, padx=12, pady=(10, 12))
        
        # Botón descanso
        break_btn = tk.Button(
            btn_container,
            text="☕  Tomar Descanso",
            command=self.take_break,
            font=('Segoe UI', 9, 'bold'),
            bg='#dc2626',
            fg='white',
            activebackground='#b91c1c',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8,
            bd=0
        )
        break_btn.pack(fill=tk.X, pady=(0, 4))
        
        # Botón estadísticas
        stats_btn = tk.Button(
            btn_container,
            text="📊  Ver Estadísticas",
            command=self.show_stats,
            font=('Segoe UI', 9, 'bold'),
            bg='#2563eb',
            fg='white',
            activebackground='#1d4ed8',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8,
            bd=0
        )
        stats_btn.pack(fill=tk.X)
        
    def update_tasks_display(self):
        """Actualizar display de tareas"""
        # Limpiar tareas actuales
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        
        # Obtener tareas pendientes
        tasks = self.task_manager.get_pending_tasks(5)
        
        # Actualizar contador
        all_pending = self.task_manager.get_pending_tasks()
        self.task_count_label.config(text=f"({len(all_pending)})")
        
        if not tasks:
            # Mensaje sin tareas
            tk.Label(
                self.tasks_frame,
                text="¡Sin tareas pendientes!\n✨ Buen trabajo",
                font=('Segoe UI', 9),
                bg='#1e293b',
                fg='#64748b',
                pady=20
            ).pack()
            return
        
        # Mostrar tareas
        for task in tasks:
            self.create_task_item(self.tasks_frame, task)
            
    def create_task_item(self, parent, task):
        """Crear item de tarea"""
        # Container de la tarea
        task_frame = tk.Frame(parent, bg='#0f172a')
        task_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Indicador de prioridad (color lateral)
        priority_colors = {
            'urgent': '#ef4444',
            'high': '#f59e0b',
            'medium': '#3b82f6',
            'low': '#6b7280'
        }
        color = priority_colors.get(task.priority, '#6b7280')
        
        priority_bar = tk.Frame(task_frame, bg=color, width=4)
        priority_bar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Contenido de la tarea
        content = tk.Frame(task_frame, bg='#1e293b')
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # Título de la tarea
        title_label = tk.Label(
            content,
            text=task.title[:40] + "..." if len(task.title) > 40 else task.title,
            font=('Segoe UI', 9, 'bold'),
            bg='#1e293b',
            fg='#e2e8f0',
            anchor='w',
            cursor='hand2'
        )
        title_label.pack(fill=tk.X)
        title_label.bind('<Button-1>', lambda e, t=task: self.complete_task_click(t.id))
        
        # Info de la tarea (tiempo estimado)
        info_text = f"⏱ {task.estimated_time}min"
        if task.deadline:
            info_text += f" • ⏰ Deadline"
        
        tk.Label(
            content,
            text=info_text,
            font=('Segoe UI', 8),
            bg='#1e293b',
            fg='#64748b',
            anchor='w'
        ).pack(fill=tk.X)
        
        # Botón eliminar
        del_btn = tk.Button(
            task_frame,
            text="✓",
            command=lambda: self.complete_task_click(task.id),
            font=('Segoe UI', 9, 'bold'),
            bg='#1e293b',
            fg='#10b981',
            activebackground='#22c55e',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            width=3,
            bd=0
        )
        del_btn.pack(side=tk.RIGHT, padx=4)
        
    def complete_task_click(self, task_id):
        """Completar tarea al hacer click"""
        self.task_manager.complete_task(task_id)
        self.update_tasks_display()
        
    def add_task_dialog(self):
        """Diálogo para añadir tarea"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nueva Tarea")
        dialog.geometry("520x400")
        dialog.configure(bg='#1e293b')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar en la pantalla
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (520 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Container
        container = tk.Frame(dialog, bg='#1e293b')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(
            container,
            text="➕ Nueva Tarea",
            font=('Segoe UI', 12, 'bold'),
            bg='#1e293b',
            fg='#818cf8'
        ).pack(pady=(0, 15))
        
        # Campo título
        tk.Label(container, text="Título:", font=('Segoe UI', 9), bg='#1e293b', fg='#94a3b8').pack(anchor='w')
        title_entry = tk.Entry(container, font=('Segoe UI', 10), bg='#0f172a', fg='white', insertbackground='white')
        title_entry.pack(fill=tk.X, pady=(2, 10))
        title_entry.focus()
        
        # Campo prioridad
        tk.Label(container, text="Prioridad:", font=('Segoe UI', 9), bg='#1e293b', fg='#94a3b8').pack(anchor='w')
        priority_var = tk.StringVar(value="medium")
        priority_frame = tk.Frame(container, bg='#1e293b')
        priority_frame.pack(fill=tk.X, pady=(2, 10))
        
        # Colores para cada prioridad
        priority_colors = {
            'urgent': '#ef4444',
            'high': '#f59e0b',
            'medium': '#3b82f6',
            'low': '#94a3b8'
        }
        
        for pri in [('🔴 Urgente', 'urgent'), ('🟠 Alta', 'high'), ('🔵 Media', 'medium'), ('⚪ Baja', 'low')]:
            tk.Radiobutton(
                priority_frame,
                text=pri[0],
                variable=priority_var,
                value=pri[1],
                font=('Segoe UI', 9, 'bold'),
                bg='#1e293b',
                fg=priority_colors[pri[1]],
                selectcolor='#0f172a',
                activebackground='#1e293b',
                activeforeground=priority_colors[pri[1]]
            ).pack(side=tk.LEFT, padx=5)
        
        # Campo tiempo estimado
        tk.Label(container, text="Tiempo estimado (min):", font=('Segoe UI', 9), bg='#1e293b', fg='#94a3b8').pack(anchor='w')
        time_entry = tk.Entry(container, font=('Segoe UI', 10), bg='#0f172a', fg='white', insertbackground='white')
        time_entry.insert(0, "30")
        time_entry.pack(fill=tk.X, pady=(2, 15))
        
        # Botones
        btn_frame = tk.Frame(container, bg='#1e293b')
        btn_frame.pack(fill=tk.X)
        
        def save_task():
            title = title_entry.get().strip()
            if not title:
                messagebox.showwarning("Error", "El título es obligatorio")
                return
            
            try:
                est_time = int(time_entry.get())
            except:
                est_time = 30
                
            self.task_manager.add_task(
                title=title,
                priority=priority_var.get(),
                estimated_time=est_time
            )
            self.update_tasks_display()
            dialog.destroy()
        
        tk.Button(
            btn_frame,
            text="Guardar",
            command=save_task,
            font=('Segoe UI', 10, 'bold'),
            bg='#22c55e',
            fg='white',
            activebackground='#16a34a',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            font=('Segoe UI', 10, 'bold'),
            bg='#334155',
            fg='white',
            activebackground='#475569',
            relief=tk.FLAT,
            cursor='hand2',
            pady=8
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
    def toggle_expand(self):
        """Expandir/contraer dashboard hacia la derecha"""
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        
        if self.expanded:
            # Contraer a tamaño original
            self.root.geometry(f"{self.collapsed_width}x{self.collapsed_height}+{current_x}+{current_y}")
            self.content_frame.pack_forget()
            self.toggle_btn.config(text="▶")
            self.expanded = False
        else:
            # Expandir hacia la derecha manteniendo posición izquierda
            self.root.geometry(f"{self.expanded_width}x{self.expanded_height}+{current_x}+{current_y}")
            self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.toggle_btn.config(text="◀")
            self.expanded = True
            self.update_tasks_display()
            
    def start_drag(self, event):
        self.dragging = True
        self.drag_x = event.x
        self.drag_y = event.y
        
    def on_drag(self, event):
        if self.dragging:
            x = self.root.winfo_x() + event.x - self.drag_x
            y = self.root.winfo_y() + event.y - self.drag_y
            self.root.geometry(f"+{x}+{y}")
            
    def stop_drag(self, event):
        self.dragging = False
        
    def take_break(self):
        """Tomar descanso"""
        self.monitor.take_break()
        self.notifier.send_notification(
            "Descanso Iniciado",
            "¡Disfruta tu descanso! Te avisaré cuando sea momento de volver."
        )
        
    def show_stats(self):
        """Mostrar estadísticas"""
        stats = self.task_manager.get_stats()
        msg = f"""📊 Estadísticas de Tareas

Total: {stats['total']}
Completadas: {stats['completed']}
Pendientes: {stats['pending']}

Por Prioridad:
🔴 Urgente: {stats['by_priority']['urgent']}
🟠 Alta: {stats['by_priority']['high']}
🔵 Media: {stats['by_priority']['medium']}
⚪ Baja: {stats['by_priority']['low']}

Tasa de Completitud: {stats['completion_rate']:.1f}%"""
        
        messagebox.showinfo("Estadísticas", msg)
        
    def update_loop(self):
        """Loop de actualización"""
        while self.running:
            try:
                # Actualizar tiempo trabajado
                status = self.monitor.get_status()
                work_mins = status.get('work_time_minutes', 0)
                hours = work_mins // 60
                mins = work_mins % 60
                self.work_time_label.config(text=f"{hours}h {mins}m")
                
                # Actualizar estado
                if work_mins > 120:  # Más de 2 horas
                    self.status_label.config(
                        text="⚠ ¡Hora de un descanso!",
                        fg='#f59e0b'
                    )
                    self.status_badge.config(fg='#f59e0b')
                elif work_mins > 60:
                    self.status_label.config(
                        text="● Buen ritmo de trabajo",
                        fg='#10b981'
                    )
                    self.status_badge.config(fg='#10b981')
                else:
                    self.status_label.config(
                        text="● Comenzando jornada",
                        fg='#818cf8'
                    )
                    self.status_badge.config(fg='#818cf8')
                
                # Actualizar barra de progreso (máximo 4 horas)
                progress = min(work_mins / 240, 1.0) * 100
                current_width = self.expanded_width if self.expanded else self.collapsed_width
                self.progress_bar.config(width=int(current_width * progress / 100))
                
                # Actualizar tareas si está expandido
                if self.expanded:
                    self.update_tasks_display()
                
            except Exception as e:
                print(f"Error en update loop: {e}")
            
            time.sleep(5)
            
    def show_welcome(self):
        """Mostrar ventana de bienvenida con información"""
        # Enviar notificación de bienvenida
        self.notifier.send_notification(
            "🚀 AI Productivity Booster",
            "Dashboard iniciado. ¡Haz clic en ▶ para ver más información!"
        )
        
        # Obtener estadísticas
        stats = self.task_manager.get_stats()
        pending = stats['pending']
        
        # Mensaje en consola con información relevante
        print("\n" + "="*60)
        print("🚀 AI PRODUCTIVITY BOOSTER - DASHBOARD INICIADO")
        print("="*60)
        print(f"\n📊 Información del Sistema:")
        print(f"   • Tareas Pendientes: {pending}")
        print(f"   • Tareas Completadas: {stats['completed']}")
        print(f"   • Tasa de Completitud: {stats['completion_rate']:.1f}%")
        print(f"\n💡 Características Disponibles:")
        print(f"   • Monitoreo de tiempo en tiempo real")
        print(f"   • Gestión inteligente de tareas")
        print(f"   • Notificaciones de productividad")
        print(f"   • Recordatorios de descanso")
        print(f"\n🎯 Próximos Pasos:")
        if pending > 0:
            print(f"   • Revisa tus {pending} tareas pendientes")
            print(f"   • Haz clic en ▶ para expandir el dashboard")
        else:
            print(f"   • Añade nuevas tareas con el botón +")
            print(f"   • Comienza a trabajar en tus objetivos")
        print("\n" + "="*60 + "\n")
    
    def on_closing(self):
        """Cerrar aplicación"""
        self.running = False
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Ejecutar dashboard"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ProductivityDashboard()
    app.run()
