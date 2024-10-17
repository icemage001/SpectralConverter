import os
import pandas as pd
from plugins import spc_plugin, spa_plugin, dx_plugin
from tkinter import filedialog, messagebox


class FileConverter:
    def __init__(self, translations):
        self.translations = translations
        self.files_info = []
        self.plugins = {
            'spc': spc_plugin,
            'spa': spa_plugin,
            'dx': dx_plugin
        }

    def update_files(self, file_paths):
        self.files_info = [(file, self.translations['statuses']['not_converted']) for file in file_paths]

    def get_files_info(self):
        return self.files_info

    def convert_files(self, file_type, output_mode):
        successful_files = []
        failed_files = []
        converted_data = []

        if output_mode == "individual":
            save_directory = filedialog.askdirectory(title=self.translations['dialogs']['choose_directory'])
            if not save_directory:
                return {"summary": ""}

        for idx, (file_path, _) in enumerate(self.files_info):
            if not file_path.lower().endswith(file_type):
                continue

            plugin = self.plugins.get(file_type)
            if not plugin:
                self.files_info[idx] = (file_path, self.translations['statuses']['failure'])
                failed_files.append(file_path)
                continue

            series = plugin.convert(file_path)
            if series.empty:
                self.files_info[idx] = (file_path, self.translations['statuses']['failure'])
                failed_files.append(file_path)
            else:
                self.files_info[idx] = (file_path, self.translations['statuses']['success'])
                successful_files.append(file_path)
                if output_mode == "merge":
                    converted_data.append((os.path.basename(file_path), series))
                else:
                    output_path = os.path.join(save_directory, os.path.basename(file_path).replace(f".{file_type}", ".csv"))
                    series.to_csv(output_path, encoding='utf-8-sig')

        if output_mode == "merge" and converted_data:
            self.merge_files(converted_data, successful_files, failed_files)

        summary_message = self.translations['summary_message'].format(len(successful_files), len(failed_files))
        return {"summary": summary_message}

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
