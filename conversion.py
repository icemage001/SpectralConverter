import os
import pandas as pd
from plugins import spc_plugin, spa_plugin, dx_plugin
from tkinter import filedialog, messagebox
import time


class FileConverter:
    def __init__(self, translations):
        self.translations = translations
        self.files_info = []
        self.file_paths = []
        self.plugins = {
            'spc': spc_plugin,
            'spa': spa_plugin,
            'dx': dx_plugin
        }
        print("FileConverter initialized")

    def update_files(self, file_paths):
        self.file_paths = file_paths
        self.files_info = [(file, self.translations['statuses']['not_converted']) for file in file_paths]
        print(f"FileConverter updated with files: {self.file_paths}")

    def get_files_info(self):
        return self.files_info

    def update_file_statuses(self, successful_files, failed_files):
        for file_path in self.file_paths:
            if file_path in successful_files:
                status = self.translations['statuses']['success']
            elif file_path in failed_files:
                status = self.translations['statuses']['failure']
            else:
                status = self.translations['statuses']['not_converted']
            
            # 更新 files_info 中的状态
            self.files_info = [(f, status) if f == file_path else (f, s) for f, s in self.files_info]

    def convert_files(self, file_type, output_mode, wavelength_decimal, value_decimal):
        print(f"Converting files. Method called at {time.time()}")
        print(f"Converting files. File paths: {self.file_paths}")
        if not hasattr(self, 'file_paths') or not self.file_paths:
            print("No files to convert")
            return {"summary": "No files to convert", "successful_files": [], "failed_files": []}

        successful_files = []
        failed_files = []
        converted_data = []

        if output_mode == "individual":
            save_directory = filedialog.askdirectory(title=self.translations['dialogs']['choose_directory'])
            if not save_directory:
                return {"summary": "", "successful_files": [], "failed_files": []}

        for file_path in self.file_paths:
            try:
                if file_type == 'spc':
                    data = spc_plugin.read_spc(file_path)
                elif file_type == 'spa':
                    data = spa_plugin.read_spa(file_path)
                elif file_type == 'dx':
                    data = dx_plugin.read_dx(file_path)
                
                # Apply decimal place settings
                if isinstance(data, pd.Series):
                    data = pd.Series(data.values.round(value_decimal), 
                                     index=data.index.round(wavelength_decimal))
                elif isinstance(data, pd.DataFrame):
                    data = pd.DataFrame(data.values.round(value_decimal), 
                                        index=data.index.round(wavelength_decimal),
                                        columns=data.columns)
                else:
                    raise ValueError(f"Unexpected data type: {type(data)}")
                
                series = pd.DataFrame(data).T
                if series.empty:
                    failed_files.append(file_path)
                else:
                    successful_files.append(file_path)
                    if output_mode == "merge":
                        converted_data.append((os.path.basename(file_path), series))
                    else:
                        output_path = os.path.join(save_directory, os.path.basename(file_path).replace(f".{file_type}", ".csv"))
                        series.to_csv(output_path, encoding='utf-8-sig')
            except Exception as e:
                print(f"Error converting file {file_path}: {str(e)}")
                failed_files.append(file_path)

        if output_mode == "merge" and converted_data:
            self.merge_files(converted_data, successful_files, failed_files)

        # 更新文件状态
        self.update_file_statuses(successful_files, failed_files)

        summary_message = self.translations['summary_message'].format(len(successful_files), len(failed_files))
        return {
            "summary": summary_message,
            "successful_files": successful_files,
            "failed_files": failed_files
        }

    def merge_files(self, converted_data, successful_files, failed_files):
        wavelengths_set = {tuple(series.index) for _, series in converted_data}
        if len(wavelengths_set) > 1:
            messagebox.showwarning(self.translations['dialogs']['inconsistent_data'], self.translations['dialogs']['inconsistent_data_warning'])
            return

        merged_df = pd.DataFrame({
            file_name: series for file_name, series in converted_data
        }).T

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if save_path:
            merged_df.to_csv(save_path, encoding='utf-8-sig')
            successful_files.append(save_path)
