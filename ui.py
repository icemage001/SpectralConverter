import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from conversion import FileConverter


class SpectralConverterApp(tk.Tk):
    def __init__(self, translations):
        super().__init__()
        self.filter_combobox = None
        self.language_combobox = None
        self.title("Spectral File Converter")
        self.geometry("700x500")
        self.configure(bg="#F0F0F0")
        self.translations = translations
        self.lang_var = tk.StringVar(value='中文')
        self.file_type_var = tk.StringVar(value='spc')
        self.output_mode = tk.StringVar(value='individual')
        self.filter_var = tk.StringVar(value=self.get_translation('statuses.all'))  # 筛选条件
        self.file_paths = []  # 初始化文件路径列表
        current_language = self.lang_var.get()  # "English" or "中文"
        self.current_translations = self.translations['en'] if current_language == 'English' else self.translations['zh']
        self.file_converter = FileConverter(self.current_translations)  # 文件转换器实例
        self.create_widgets()

    def get_translation(self, key):
        lang_code = 'en' if self.lang_var.get() == "English" else 'zh'
        keys = key.split(".")
        translation = self.translations.get(lang_code, {})
        for k in keys:
            translation = translation.get(k, key)
        return translation

    def update_language(self, event):
        """更新语言后重新加载翻译数据"""
        self.file_converter.translations = self.current_translations
        self.create_widgets()  # 重新生成界面以更新语言
        # 更新筛选状态下拉框的值和默认选项
        self.update_filter_combobox()

    def get_filter_options(self):
        """获取当前语言下的筛选状态选项"""
        return [
            self.get_translation('statuses.all'),
            self.get_translation('statuses.not_converted'),
            self.get_translation('statuses.success'),
            self.get_translation('statuses.failure')
        ]

    def update_filter_combobox(self):
        """更新筛选状态下拉框的值和默认选项"""
        filter_options = self.get_filter_options()
        self.filter_combobox['values'] = filter_options
        self.filter_combobox.set(self.get_translation('statuses.all'))  # 重设默认选项为 "All"

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.pack_forget()

        tk.Label(self, text=self.get_translation('labels.language_select'), font=("Helvetica Neue", 12), bg="#F0F0F0").pack(
            anchor='w', padx=20)
        self.language_combobox = ttk.Combobox(self, textvariable=self.lang_var, values=["English", "中文"],
                                              state="readonly")
        self.language_combobox.pack(anchor='w', padx=20)
        self.language_combobox.bind("<<ComboboxSelected>>", self.update_language)

        self.create_widgets_ui()

    def create_widgets_ui(self):
        tk.Button(self, text=self.get_translation('buttons.select_files'), command=self.select_files,
                  font=("Helvetica Neue", 12), bg="#F0F0F0").pack(pady=10)

        tk.Label(self, text=self.get_translation('labels.file_type'), font=("Helvetica Neue", 12), bg="#F0F0F0").pack(
            anchor='w', padx=20)
        file_types = ["spc", "spa", "dx"]
        self.file_type_combobox = ttk.Combobox(self, textvariable=self.file_type_var, values=file_types,
                                               state="readonly")
        self.file_type_combobox.pack(anchor='w', padx=20)

        tk.Label(self, text=self.get_translation('labels.output_mode'), font=("Helvetica Neue", 12), bg="#F0F0F0").pack(
            anchor='w', padx=20)
        tk.Radiobutton(self, text=self.get_translation('buttons.save_individual'), variable=self.output_mode,
                       value="individual", font=("Helvetica Neue", 12), bg="#F0F0F0").pack(anchor='w', padx=40)
        tk.Radiobutton(self, text=self.get_translation('buttons.merge_files'), variable=self.output_mode, value="merge",
                       font=("Helvetica Neue", 12), bg="#F0F0F0").pack(anchor='w', padx=40)

        tk.Button(self, text=self.get_translation('buttons.convert'), command=self.convert_files,
                  font=("Helvetica Neue", 12), bg="#007AFF", fg="white", borderwidth=0, padx=20, pady=5).pack(pady=20)

        tk.Label(self, text=self.get_translation('labels.filter_by_status'), font=("Helvetica Neue", 12),
                 bg="#F0F0F0").pack(anchor='w', padx=20)
        self.filter_combobox = ttk.Combobox(self, textvariable=self.filter_var, values=self.get_filter_options(),
                                            state="readonly")
        self.filter_combobox.pack(anchor='w', padx=20)
        self.filter_combobox.bind("<<ComboboxSelected>>", self.filter_files)

        # 设置初始选中的值
        self.update_filter_combobox()

        tk.Label(self, text=self.get_translation('labels.selected_files'), font=("Helvetica Neue", 12),
                 bg="#F0F0F0").pack(anchor='w', padx=20)

        columns = ("file", "status")
        self.file_tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.file_tree.heading("file", text=self.get_translation('labels.file'))
        self.file_tree.heading("status", text=self.get_translation('labels.status'))
        self.file_tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def select_files(self):
        file_types = [(f"{self.file_type_var.get().upper()} Files", f"*.{self.file_type_var.get()}")]
        files = filedialog.askopenfilenames(filetypes=file_types)
        self.file_paths = list(files)
        self.file_converter.update_files(self.file_paths)  # 更新文件路径

        self.refresh_file_tree()

    def refresh_file_tree(self):
        for row in self.file_tree.get_children():
            self.file_tree.delete(row)

        for file, status in self.file_converter.get_files_info():
            if self.filter_var.get() == self.get_translation('statuses.all') or status == self.filter_var.get():
                self.file_tree.insert("", tk.END, values=(file, status))

    def filter_files(self, event=None):
        self.refresh_file_tree()

    def convert_files(self):
        # 检查是否选择了文件
        if not self.file_paths:
            messagebox.showwarning(self.get_translation('dialogs.no_files'),
                                   self.get_translation('dialogs.no_files_warning'))
            return  # 如果没有选择文件，则直接返回

        result = self.file_converter.convert_files(self.file_type_var.get(), self.output_mode.get())
        self.refresh_file_tree()

        messagebox.showinfo(self.get_translation('dialogs.conversion_complete'), result['summary'])


