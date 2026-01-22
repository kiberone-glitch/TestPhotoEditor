from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

class PhotoEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Editor - Pillow")
        self.root.geometry("1200x700")
        
        # Инициализация переменных
        self.image = None
        self.original_image = None
        self.display_image = None
        self.history = []
        self.current_scale = 1.0
        
        # Создание интерфейса
        self.create_widgets()
        
        # Установка минимального размера окна
        self.root.minsize(900, 600)
        
        # Связывание горячих клавиш
        self.root.bind('<Control-o>', lambda e: self.load_image())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-r>', lambda e: self.reset_image())
        
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Главный контейнер
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - инструменты
        left_panel = tk.Frame(main_container, width=250, bg='#f0f0f0')
        main_container.add(left_panel)
        
        # Правая панель - изображение
        right_panel = tk.Frame(main_container, bg='#2c3e50')
        main_container.add(right_panel)
        
        # Создание панели инструментов
        self.create_tool_panel(left_panel)
        
        # Создание панели изображения
        self.create_image_panel(right_panel)
        
    def create_tool_panel(self, parent):
        """Создание панели инструментов"""
        # Заголовок
        title_label = tk.Label(parent, text="ФОТОРЕДАКТОР", 
                              font=('Arial', 14, 'bold'), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)
        
        # Разделитель
        tk.Frame(parent, height=2, bg='#3498db').pack(fill=tk.X, padx=10, pady=5)
        
        # Кнопки файловых операций
        file_frame = tk.LabelFrame(parent, text="Файл", bg='#f0f0f0', font=('Arial', 10, 'bold'))
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(file_frame, text="📁 Загрузить (Ctrl+O)", command=self.load_image,
                 bg='#3498db', fg='white', font=('Arial', 10), height=2).pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(file_frame, text="💾 Сохранить (Ctrl+S)", command=self.save_image,
                 bg='#2ecc71', fg='white', font=('Arial', 10), height=2).pack(fill=tk.X, padx=5, pady=2)
        
        # Информация об изображении
        self.info_frame = tk.LabelFrame(parent, text="Информация", bg='#f0f0f0', font=('Arial', 10, 'bold'))
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_label = tk.Label(self.info_frame, text="Изображение не загружено", 
                                  bg='#f0f0f0', justify=tk.LEFT)
        self.info_label.pack(padx=10, pady=10, fill=tk.X)
        
        # Разделитель
        tk.Frame(parent, height=2, bg='#3498db').pack(fill=tk.X, padx=10, pady=5)
        
        # Панель инструментов редактирования
        tools_frame = tk.LabelFrame(parent, text="Инструменты", bg='#f0f0f0', font=('Arial', 10, 'bold'))
        tools_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Создание вкладок для инструментов
        self.create_tools_tabs(tools_frame)
        
        # Кнопки отмены/сброса
        control_frame = tk.Frame(parent, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="↶ Отменить (Ctrl+Z)", command=self.undo,
                 bg='#e74c3c', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(control_frame, text="🔄 Сброс (Ctrl+R)", command=self.reset_image,
                 bg='#f39c12', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Масштаб
        scale_frame = tk.Frame(parent, bg='#f0f0f0')
        scale_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(scale_frame, text="Масштаб:", bg='#f0f0f0').pack(side=tk.LEFT)
        
        tk.Button(scale_frame, text="+", command=self.zoom_in, width=3,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(scale_frame, text="-", command=self.zoom_out, width=3,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(scale_frame, text="100%", command=self.zoom_reset, width=4,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=2)
        
    def create_tools_tabs(self, parent):
        """Создание вкладок с инструментами"""
        # Ноутбук для вкладок
        notebook = tk.Frame(parent, bg='#f0f0f0')
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка "Размер и поворот"
        size_frame = tk.Frame(notebook, bg='#f0f0f0')
        
        # Изменение размера
        tk.Button(size_frame, text="📐 Изменить размер", command=self.resize_dialog,
                 bg='#9b59b6', fg='white', font=('Arial', 10), height=2).pack(fill=tk.X, pady=2)
        
        # Обрезка
        tk.Button(size_frame, text="✂️ Обрезать", command=self.crop_dialog,
                 bg='#9b59b6', fg='white', font=('Arial', 10), height=2).pack(fill=tk.X, pady=2)
        
        # Поворот
        rotate_frame = tk.Frame(size_frame, bg='#f0f0f0')
        rotate_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(rotate_frame, text="↻ 90°", command=lambda: self.rotate_image(90),
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        tk.Button(rotate_frame, text="↺ -90°", command=lambda: self.rotate_image(-90),
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        tk.Button(rotate_frame, text="🔄 180°", command=lambda: self.rotate_image(180),
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        
        # Отражение
        flip_frame = tk.Frame(size_frame, bg='#f0f0f0')
        flip_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(flip_frame, text="⇄ Горизонтально", command=self.flip_horizontal,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        tk.Button(flip_frame, text="⇅ Вертикально", command=self.flip_vertical,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        
        # Вкладка "Коррекция"
        adjust_frame = tk.Frame(notebook, bg='#f0f0f0')
        
        adjustments = [
            ("☀️ Яркость", self.adjust_brightness_dialog),
            ("⚫ Контраст", self.adjust_contrast_dialog),
            ("🎨 Насыщенность", self.adjust_color_dialog),
            ("🔍 Резкость", self.adjust_sharpness_dialog)
        ]
        
        for text, command in adjustments:
            tk.Button(adjust_frame, text=text, command=command,
                     bg='#2ecc71', fg='white', font=('Arial', 10), height=2).pack(fill=tk.X, pady=2)
        
        # Вкладка "Фильтры"
        filters_frame = tk.Frame(notebook, bg='#f0f0f0')
        
        filters = [
            ("🔄 Размытие", self.apply_blur_dialog),
            ("✨ Резкость", self.apply_sharpen),
            ("🏔️ Тиснение", self.apply_emboss),
            ("🔲 Края", self.apply_edge_enhance)
        ]
        
        for text, command in filters:
            tk.Button(filters_frame, text=text, command=command,
                     bg='#e74c3c', fg='white', font=('Arial', 10), height=2).pack(fill=tk.X, pady=2)
        
        # Вкладка "Эффекты"
        effects_frame = tk.Frame(notebook, bg='#f0f0f0')
        
        effects = [
            ("⚫ Черно-белое", self.convert_to_grayscale),
            ("🟤 Сепия", self.convert_to_sepia),
            ("🌈 Негатив", self.convert_to_negative)
        ]
        
        for text, command in effects:
            tk.Button(effects_frame, text=text, command=command,
                     bg='#f39c12', fg='white', font=('Arial', 10), height=2).pack(fill=tk.X, pady=2)
        
        # Упаковка всех вкладок
        size_frame.pack(fill=tk.BOTH, expand=True)
        adjust_frame.pack(fill=tk.BOTH, expand=True)
        filters_frame.pack(fill=tk.BOTH, expand=True)
        effects_frame.pack(fill=tk.BOTH, expand=True)
        
    def create_image_panel(self, parent):
        """Создание панели для отображения изображения"""
        # Панель для изображения с прокруткой
        self.canvas_frame = tk.Frame(parent, bg='#2c3e50')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Холст для изображения
        self.canvas = tk.Canvas(self.canvas_frame, bg='#2c3e50', highlightthickness=0)
        
        # Полосы прокрутки
        h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Упаковка элементов
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Надпись "Загрузите изображение"
        self.placeholder_label = tk.Label(self.canvas, text="Загрузите изображение (Ctrl+O)",
                                         font=('Arial', 16), fg='#ecf0f1', bg='#2c3e50')
        self.placeholder_label.pack(expand=True)
        
    # === Функции работы с изображением ===
    
    def load_image(self):
        """Загрузка изображения"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Все изображения", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.image = Image.open(file_path)
                self.original_image = self.image.copy()
                self.history = [self.image.copy()]
                self.current_scale = 1.0
                
                self.update_image_display()
                self.update_info()
                
                # Удаляем надпись-заглушку
                if self.placeholder_label.winfo_exists():
                    self.placeholder_label.destroy()
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
    
    def save_image(self):
        """Сохранение изображения"""
        if not self.image:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.image.save(file_path)
                messagebox.showinfo("Успех", f"Изображение сохранено:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изображение:\n{str(e)}")
    
    def update_image_display(self):
        """Обновление отображения изображения на холсте"""
        if self.image:
            # Масштабирование для отображения
            display_width = int(self.image.width * self.current_scale)
            display_height = int(self.image.height * self.current_scale)
            
            if display_width > 0 and display_height > 0:
                display_image = self.image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                self.display_image = ImageTk.PhotoImage(display_image)
                
                # Обновление холста
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.display_image)
                self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
    
    def update_info(self):
        """Обновление информации об изображении"""
        if self.image:
            info_text = f"Размер: {self.image.width} × {self.image.height}\n"
            info_text += f"Формат: {self.image.format or 'Неизвестно'}\n"
            info_text += f"Режим: {self.image.mode}\n"
            info_text += f"Масштаб: {int(self.current_scale * 100)}%"
            self.info_label.config(text=info_text)
        else:
            self.info_label.config(text="Изображение не загружено")
    
    def add_to_history(self):
        """Добавление в историю изменений"""
        if self.image:
            self.history.append(self.image.copy())
            if len(self.history) > 20:  # Ограничиваем историю
                self.history.pop(0)
    
    # === Функции масштабирования ===
    
    def zoom_in(self):
        """Увеличение масштаба"""
        if self.image:
            self.current_scale *= 1.2
            self.update_image_display()
            self.update_info()
    
    def zoom_out(self):
        """Уменьшение масштаба"""
        if self.image:
            self.current_scale /= 1.2
            if self.current_scale < 0.1:
                self.current_scale = 0.1
            self.update_image_display()
            self.update_info()
    
    def zoom_reset(self):
        """Сброс масштаба до 100%"""
        if self.image:
            self.current_scale = 1.0
            self.update_image_display()
            self.update_info()
    
    # === Диалоговые окна для операций ===
    
    def resize_dialog(self):
        """Диалог изменения размера"""
        if not self.image:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменение размера")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Ширина:", font=('Arial', 10)).pack(pady=5)
        width_var = tk.StringVar(value=str(self.image.width))
        width_entry = tk.Entry(dialog, textvariable=width_var, font=('Arial', 10))
        width_entry.pack(pady=5)
        
        tk.Label(dialog, text="Высота:", font=('Arial', 10)).pack(pady=5)
        height_var = tk.StringVar(value=str(self.image.height))
        height_entry = tk.Entry(dialog, textvariable=height_var, font=('Arial', 10))
        height_entry.pack(pady=5)
        
        keep_ratio = tk.BooleanVar(value=True)
        tk.Checkbutton(dialog, text="Сохранять пропорции", variable=keep_ratio).pack(pady=10)
        
        def apply_resize():
            try:
                width = int(width_var.get())
                height = int(height_var.get())
                
                if keep_ratio.get():
                    ratio = width / self.image.width
                    new_width = width
                    new_height = int(self.image.height * ratio)
                else:
                    new_width = width
                    new_height = height
                
                self.image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.add_to_history()
                self.update_image_display()
                self.update_info()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числа!")
        
        tk.Button(dialog, text="Применить", command=apply_resize,
                 bg='#3498db', fg='white', font=('Arial', 10)).pack(pady=10)
    
    def crop_dialog(self):
        """Диалог обрезки изображения"""
        if not self.image:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Обрезка изображения")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Координаты обрезки
        fields = [
            ("Левая граница:", "0"),
            ("Верхняя граница:", "0"),
            ("Правая граница:", str(self.image.width)),
            ("Нижняя граница:", str(self.image.height))
        ]
        
        entries = []
        for i, (label_text, default) in enumerate(fields):
            tk.Label(dialog, text=label_text, font=('Arial', 10)).pack(pady=5)
            var = tk.StringVar(value=default)
            entry = tk.Entry(dialog, textvariable=var, font=('Arial', 10))
            entry.pack(pady=5)
            entries.append(var)
        
        def apply_crop():
            try:
                coords = tuple(int(var.get()) for var in entries)
                self.image = self.image.crop(coords)
                self.add_to_history()
                self.update_image_display()
                self.update_info()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числа!")
        
        tk.Button(dialog, text="Применить", command=apply_crop,
                 bg='#3498db', fg='white', font=('Arial', 10)).pack(pady=10)
    
    def create_slider_dialog(self, title, min_val, max_val, default, command):
        """Создание диалога с ползунком"""
        if not self.image:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        value_var = tk.DoubleVar(value=default)
        
        # Ползунок
        slider = tk.Scale(dialog, from_=min_val, to=max_val, 
                         resolution=0.1, orient=tk.HORIZONTAL,
                         variable=value_var, length=250)
        slider.pack(pady=20)
        
        # Текущее значение
        value_label = tk.Label(dialog, text=f"Значение: {default:.1f}")
        value_label.pack()
        
        def update_label(val):
            value_label.config(text=f"Значение: {float(val):.1f}")
        
        slider.config(command=update_label)
        
        def apply_adjustment():
            command(value_var.get())
            dialog.destroy()
        
        tk.Button(dialog, text="Применить", command=apply_adjustment,
                 bg='#3498db', fg='white', font=('Arial', 10)).pack(pady=10)
    
    # === Операции с изображением ===
    
    def rotate_image(self, degrees):
        """Поворот изображения"""
        if self.image:
            self.image = self.image.rotate(degrees, expand=True)
            self.add_to_history()
            self.update_image_display()
            self.update_info()
    
    def flip_horizontal(self):
        """Отражение по горизонтали"""
        if self.image:
            self.image = ImageOps.mirror(self.image)
            self.add_to_history()
            self.update_image_display()
    
    def flip_vertical(self):
        """Отражение по вертикали"""
        if self.image:
            self.image = ImageOps.flip(self.image)
            self.add_to_history()
            self.update_image_display()
    
    def adjust_brightness_dialog(self):
        """Диалог настройки яркости"""
        self.create_slider_dialog("Яркость", 0.1, 3.0, 1.0, self.adjust_brightness)
    
    def adjust_brightness(self, factor):
        """Настройка яркости"""
        if self.image:
            enhancer = ImageEnhance.Brightness(self.image)
            self.image = enhancer.enhance(factor)
            self.add_to_history()
            self.update_image_display()
    
    def adjust_contrast_dialog(self):
        """Диалог настройки контрастности"""
        self.create_slider_dialog("Контраст", 0.1, 3.0, 1.0, self.adjust_contrast)
    
    def adjust_contrast(self, factor):
        """Настройка контрастности"""
        if self.image:
            enhancer = ImageEnhance.Contrast(self.image)
            self.image = enhancer.enhance(factor)
            self.add_to_history()
            self.update_image_display()
    
    def adjust_color_dialog(self):
        """Диалог настройки насыщенности"""
        self.create_slider_dialog("Насыщенность", 0.0, 3.0, 1.0, self.adjust_color)
    
    def adjust_color(self, factor):
        """Настройка насыщенности"""
        if self.image:
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(factor)
            self.add_to_history()
            self.update_image_display()
    
    def adjust_sharpness_dialog(self):
        """Диалог настройки резкости"""
        self.create_slider_dialog("Резкость", 0.0, 3.0, 1.0, self.adjust_sharpness)
    
    def adjust_sharpness(self, factor):
        """Настройка резкости"""
        if self.image:
            enhancer = ImageEnhance.Sharpness(self.image)
            self.image = enhancer.enhance(factor)
            self.add_to_history()
            self.update_image_display()
    
    def apply_blur_dialog(self):
        """Диалог применения размытия"""
        self.create_slider_dialog("Размытие", 0.5, 10.0, 2.0, self.apply_blur)
    
    def apply_blur(self, radius):
        """Применение размытия"""
        if self.image:
            self.image = self.image.filter(ImageFilter.GaussianBlur(radius))
            self.add_to_history()
            self.update_image_display()
    
    def apply_sharpen(self):
        """Применение усиления резкости"""
        if self.image:
            self.image = self.image.filter(ImageFilter.SHARPEN)
            self.add_to_history()
            self.update_image_display()
    
    def apply_emboss(self):
        """Применение эффекта тиснения"""
        if self.image:
            self.image = self.image.filter(ImageFilter.EMBOSS)
            self.add_to_history()
            self.update_image_display()
    
    def apply_edge_enhance(self):
        """Применение усиления краев"""
        if self.image:
            self.image = self.image.filter(ImageFilter.EDGE_ENHANCE)
            self.add_to_history()
            self.update_image_display()
    
    def convert_to_grayscale(self):
        """Конвертация в черно-белое"""
        if self.image:
            self.image = self.image.convert('L').convert('RGB')
            self.add_to_history()
            self.update_image_display()
    
    def convert_to_sepia(self):
        """Конвертация в сепию"""
        if self.image:
            # Создаем эффект сепии
            grayscale = self.image.convert('L')
            sepia = Image.new('RGB', grayscale.size)
            width, height = grayscale.size
            
            # Оптимизированная версия с использованием point
            r = grayscale.point(lambda g: int(g * 0.9))
            g = grayscale.point(lambda g: int(g * 0.7))
            b = grayscale.point(lambda g: int(g * 0.4))
            
            sepia = Image.merge('RGB', (r, g, b))
            self.image = sepia
            self.add_to_history()
            self.update_image_display()
    
    def convert_to_negative(self):
        """Конвертация в негатив"""
        if self.image:
            self.image = ImageOps.invert(self.image.convert('RGB'))
            self.add_to_history()
            self.update_image_display()
    
    def undo(self):
        """Отмена последнего действия"""
        if len(self.history) > 1:
            self.history.pop()
            self.image = self.history[-1].copy()
            self.update_image_display()
            self.update_info()
    
    def reset_image(self):
        """Сброс всех изменений"""
        if self.original_image:
            self.image = self.original_image.copy()
            self.history = [self.image.copy()]
            self.current_scale = 1.0
            self.update_image_display()
            self.update_info()


def main():
    """Основная функция"""
    root = tk.Tk()
    app = PhotoEditorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()