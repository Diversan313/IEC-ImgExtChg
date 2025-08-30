import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path
import threading

class FileExtensionChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("Массовое изменение расширений файлов")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Список выбранных файлов
        self.selected_files = []
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="🔄 Массовое изменение расширений файлов", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # Фрейм для выбора файлов
        file_frame = tk.Frame(self.root, bg='#f0f0f0')
        file_frame.pack(pady=10, padx=20, fill='x')
        
        # Кнопка выбора файлов
        select_btn = tk.Button(
            file_frame,
            text="📁 Выбрать файлы",
            command=self.select_files,
            font=("Arial", 12),
            bg='#3498db',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        select_btn.pack(side='left', padx=10)
        
        # Кнопка очистки списка
        clear_btn = tk.Button(
            file_frame,
            text="🗑️ Очистить список",
            command=self.clear_files,
            font=("Arial", 12),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        clear_btn.pack(side='left', padx=10)
        
        # Список выбранных файлов
        list_frame = tk.Frame(self.root, bg='#f0f0f0')
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(
            list_frame, 
            text="Выбранные файлы:", 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        ).pack(anchor='w')
        
        # Treeview для отображения файлов
        self.file_tree = ttk.Treeview(
            list_frame, 
            columns=('name', 'extension', 'size'), 
            show='headings',
            height=10
        )
        
        self.file_tree.heading('name', text='Имя файла')
        self.file_tree.heading('extension', text='Текущее расширение')
        self.file_tree.heading('size', text='Размер')
        
        self.file_tree.column('name', width=400)
        self.file_tree.column('extension', width=150)
        self.file_tree.column('size', width=100)
        
        # Скроллбар для списка файлов
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Фрейм для настроек изменения
        settings_frame = tk.Frame(self.root, bg='#f0f0f0')
        settings_frame.pack(pady=20, padx=20, fill='x')
        
        # Выбор нового расширения
        tk.Label(
            settings_frame, 
            text="Новое расширение:", 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        ).pack(anchor='w')
        
        extension_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        extension_frame.pack(fill='x', pady=5)
        
        self.extension_var = tk.StringVar(value='png')
        extension_entry = tk.Entry(
            extension_frame,
            textvariable=self.extension_var,
            font=("Arial", 12),
            width=10
        )
        extension_entry.pack(side='left', padx=(0, 10))
        
        # Кнопки быстрого выбора расширений
        quick_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff']
        for ext in quick_extensions:
            btn = tk.Button(
                extension_frame,
                text=ext.upper(),
                command=lambda e=ext: self.extension_var.set(e),
                font=("Arial", 10),
                bg='#95a5a6',
                fg='white',
                relief='flat',
                padx=10,
                pady=5,
                cursor='hand2'
            )
            btn.pack(side='left', padx=2)
        
        # Опции
        options_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        options_frame.pack(fill='x', pady=10)
        
        self.backup_var = tk.BooleanVar(value=True)
        backup_check = tk.Checkbutton(
            options_frame,
            text="Создать резервные копии оригинальных файлов",
            variable=self.backup_var,
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        backup_check.pack(anchor='w')
        
        self.overwrite_var = tk.BooleanVar(value=False)
        overwrite_check = tk.Checkbutton(
            options_frame,
            text="Перезаписывать существующие файлы",
            variable=self.overwrite_var,
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        overwrite_check.pack(anchor='w')
        
        # Кнопка запуска
        convert_btn = tk.Button(
            self.root,
            text="🚀 ИЗМЕНИТЬ РАСШИРЕНИЯ",
            command=self.convert_files,
            font=("Arial", 14, "bold"),
            bg='#27ae60',
            fg='white',
            relief='flat',
            padx=30,
            pady=15,
            cursor='hand2'
        )
        convert_btn.pack(pady=20)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(
            self.root, 
            mode='determinate',
            length=400
        )
        self.progress.pack(pady=10)
        
        # Статус
        self.status_label = tk.Label(
            self.root,
            text="Готов к работе",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        self.status_label.pack(pady=5)
    
    def select_files(self):
        """Выбор файлов для изменения расширений"""
        files = filedialog.askopenfilenames(
            title="Выберите файлы для изменения расширений",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Изображения", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff"),
                ("Видео", "*.mp4 *.avi *.mov *.webm *.mkv"),
                ("Документы", "*.pdf *.doc *.docx *.txt"),
            ]
        )
        
        if files:
            self.selected_files.extend(files)
            self.update_file_list()
            self.status_label.config(text=f"Выбрано файлов: {len(self.selected_files)}")
    
    def clear_files(self):
        """Очистка списка выбранных файлов"""
        self.selected_files.clear()
        self.update_file_list()
        self.status_label.config(text="Список файлов очищен")
    
    def update_file_list(self):
        """Обновление списка файлов в интерфейсе"""
        # Очистка текущего списка
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Добавление файлов в список
        for file_path in self.selected_files:
            try:
                path = Path(file_path)
                name = path.name
                extension = path.suffix.lower() if path.suffix else "без расширения"
                size = self.get_file_size(path)
                
                self.file_tree.insert('', 'end', values=(name, extension, size))
            except Exception as e:
                self.file_tree.insert('', 'end', values=(file_path, "ошибка", "N/A"))
    
    def get_file_size(self, path):
        """Получение размера файла в удобном формате"""
        try:
            size = path.stat().st_size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except:
            return "N/A"
    
    def convert_files(self):
        """Изменение расширений файлов"""
        if not self.selected_files:
            messagebox.showwarning("Предупреждение", "Сначала выберите файлы!")
            return
        
        new_extension = self.extension_var.get().strip()
        if not new_extension:
            messagebox.showwarning("Предупреждение", "Введите новое расширение!")
            return
        
        # Добавление точки к расширению если её нет
        if not new_extension.startswith('.'):
            new_extension = '.' + new_extension
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self._convert_files_thread, args=(new_extension,))
        thread.daemon = True
        thread.start()
    
    def _convert_files_thread(self, new_extension):
        """Поток для изменения расширений файлов"""
        try:
            total_files = len(self.selected_files)
            self.progress['maximum'] = total_files
            self.progress['value'] = 0
            
            converted_count = 0
            error_count = 0
            
            for i, file_path in enumerate(self.selected_files):
                try:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Обработка файла {i+1} из {total_files}..."
                    ))
                    
                    path = Path(file_path)
                    
                    # Создание резервной копии если нужно
                    if self.backup_var.get():
                        backup_path = path.with_suffix(path.suffix + '.backup')
                        shutil.copy2(file_path, backup_path)
                    
                    # Новое имя файла
                    new_path = path.with_suffix(new_extension)
                    
                    # Проверка на существование файла
                    if new_path.exists() and not self.overwrite_var.get():
                        error_count += 1
                        continue
                    
                    # Переименование файла
                    path.rename(new_path)
                    converted_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Ошибка при обработке {file_path}: {e}")
                
                # Обновление прогресс бара
                self.root.after(0, lambda v=i+1: self.progress.config(value=v))
            
            # Завершение
            self.root.after(0, lambda: self._conversion_complete(converted_count, error_count))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка: {e}"))
    
    def _conversion_complete(self, converted_count, error_count):
        """Завершение процесса конвертации"""
        self.progress['value'] = 0
        self.status_label.config(text="Готов к работе")
        
        message = f"Конвертация завершена!\n\n"
        message += f"✅ Успешно обработано: {converted_count} файлов\n"
        if error_count > 0:
            message += f"❌ Ошибок: {error_count} файлов"
        
        messagebox.showinfo("Результат", message)
        
        # Очистка списка после успешной конвертации
        if converted_count > 0:
            self.clear_files()

def main():
    root = tk.Tk()
    app = FileExtensionChanger(root)
    root.mainloop()

if __name__ == "__main__":
    main()