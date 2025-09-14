import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinterdnd2 as tkdnd
from PIL import Image, ImageTk
import mutagen
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import moviepy.editor as mp
import os
import datetime
import threading
from pathlib import Path
import json
import tempfile

class MP3toMP4Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 to MP4 Converter")
        self.root.geometry("800x600")
        
        # 設定ファイル
        self.config_file = "config.json"
        self.load_config()
        
        # ファイルリスト
        self.file_list = []
        
        self.create_widgets()
        
    def load_config(self):
        """設定を読み込む"""
        default_config = {
            "output_folder": "",
            "video_format": "1:1",
            "filename_format": "original",
            "quality": "720p"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
        except:
            self.config = default_config
            
    def save_config(self):
        """設定を保存する"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
            
    def create_widgets(self):
        """GUI要素を作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ファイル選択エリア
        file_frame = ttk.LabelFrame(main_frame, text="MP3ファイル選択", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # ドラッグ&ドロップエリア
        self.drop_area = tk.Listbox(file_frame, height=8, selectmode=tk.EXTENDED)
        self.drop_area.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # ドラッグ&ドロップ機能を追加
        self.drop_area.drop_target_register(tkdnd.DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
        
        # ボタン
        ttk.Button(file_frame, text="ファイル選択", command=self.select_files).grid(row=1, column=0, padx=(0, 5))
        ttk.Button(file_frame, text="クリア", command=self.clear_files).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="削除", command=self.remove_selected).grid(row=1, column=2, padx=(5, 0))
        
        # 設定エリア
        settings_frame = ttk.LabelFrame(main_frame, text="設定", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 動画形式設定
        ttk.Label(settings_frame, text="動画形式:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.format_var = tk.StringVar(value=self.config["video_format"])
        format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var, values=["1:1", "16:9"], state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # 品質設定
        ttk.Label(settings_frame, text="品質:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=(0, 5))
        self.quality_var = tk.StringVar(value=self.config["quality"])
        quality_combo = ttk.Combobox(settings_frame, textvariable=self.quality_var, values=["1080p", "720p", "480p", "360p"], state="readonly", width=10)
        quality_combo.grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # 出力フォルダ設定
        ttk.Label(settings_frame, text="出力フォルダ:").grid(row=1, column=0, sticky=tk.W, pady=(5, 5))
        self.output_var = tk.StringVar(value=self.config["output_folder"])
        output_entry = ttk.Entry(settings_frame, textvariable=self.output_var, width=40)
        output_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 5), pady=(5, 5))
        ttk.Button(settings_frame, text="参照", command=self.select_output_folder).grid(row=1, column=3, padx=(5, 0), pady=(5, 5))
        
        # ファイル名設定
        ttk.Label(settings_frame, text="ファイル名:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.filename_var = tk.StringVar(value=self.config["filename_format"])
        filename_combo = ttk.Combobox(settings_frame, textvariable=self.filename_var, 
                                    values=["original", "original_date", "original_creation"], 
                                    state="readonly", width=20)
        filename_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # 変換ボタンとプログレスバー
        convert_frame = ttk.Frame(main_frame)
        convert_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.convert_btn = ttk.Button(convert_frame, text="変換開始", command=self.start_conversion)
        self.convert_btn.grid(row=0, column=0, pady=(0, 10))
        
        self.progress = ttk.Progressbar(convert_frame, mode='determinate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(convert_frame, text="準備完了")
        self.status_label.grid(row=2, column=0)
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        convert_frame.columnconfigure(0, weight=1)
        
    def on_drop(self, event):
        """ドラッグ&ドロップ処理"""
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            if file_path.lower().endswith('.mp3') and file_path not in self.file_list:
                self.file_list.append(file_path)
                self.drop_area.insert(tk.END, os.path.basename(file_path))
                
    def select_files(self):
        """ファイル選択ダイアログ"""
        files = filedialog.askopenfilenames(
            title="MP3ファイルを選択",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        for file_path in files:
            if file_path not in self.file_list:
                self.file_list.append(file_path)
                self.drop_area.insert(tk.END, os.path.basename(file_path))
                
    def clear_files(self):
        """ファイルリストをクリア"""
        self.file_list.clear()
        self.drop_area.delete(0, tk.END)
        
    def remove_selected(self):
        """選択したファイルを削除"""
        selected = self.drop_area.curselection()
        for i in reversed(selected):
            del self.file_list[i]
            self.drop_area.delete(i)
            
    def select_output_folder(self):
        """出力フォルダ選択"""
        folder = filedialog.askdirectory(title="出力フォルダを選択")
        if folder:
            self.output_var.set(folder)
            
    def get_video_dimensions(self):
        """動画の解像度を取得"""
        format_type = self.format_var.get()
        quality = self.quality_var.get()
        
        if format_type == "1:1":
            dimensions = {
                "1080p": (1080, 1080),
                "720p": (720, 720),
                "480p": (480, 480),
                "360p": (360, 360)
            }
        else:  # 16:9
            dimensions = {
                "1080p": (1920, 1080),
                "720p": (1280, 720),
                "480p": (854, 480),
                "360p": (640, 360)
            }
            
        return dimensions.get(quality, (720, 720))
        
    def extract_album_art(self, mp3_path):
        """MP3からアルバムアートを抽出"""
        try:
            audio_file = MP3(mp3_path, ID3=ID3)
            
            for tag in audio_file.tags.values():
                if hasattr(tag, 'type') and tag.type == 3:  # Front cover
                    # 一時ファイルに画像を保存
                    temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    temp_image.write(tag.data)
                    temp_image.close()
                    return temp_image.name
                    
        except Exception as e:
            print(f"アルバムアート抽出エラー: {e}")
            
        return None
        
    def create_default_image(self, width, height):
        """デフォルト画像を作成"""
        image = Image.new('RGB', (width, height), color='black')
        temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image.save(temp_image.name, 'JPEG')
        temp_image.close()
        return temp_image.name
        
    def generate_output_filename(self, mp3_path):
        """出力ファイル名を生成"""
        base_name = os.path.splitext(os.path.basename(mp3_path))[0]
        format_type = self.filename_var.get()
        
        if format_type == "original":
            return f"{base_name}.mp4"
        elif format_type == "original_date":
            mod_time = os.path.getmtime(mp3_path)
            date_str = datetime.datetime.fromtimestamp(mod_time).strftime("%Y%m%d_%H%M%S")
            return f"{base_name}_{date_str}.mp4"
        elif format_type == "original_creation":
            creation_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{base_name}_{creation_time}.mp4"
            
        return f"{base_name}.mp4"
        
    def convert_single_file(self, mp3_path):
        """単一ファイルを変換"""
        try:
            # アルバムアートを抽出
            image_path = self.extract_album_art(mp3_path)
            width, height = self.get_video_dimensions()
            
            if image_path is None:
                # デフォルト画像を作成
                image_path = self.create_default_image(width, height)
                default_image = True
            else:
                default_image = False
                
            # 画像をリサイズ
            try:
                image = Image.open(image_path)
                image = image.resize((width, height), Image.Resampling.LANCZOS)
                resized_image_path = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                image.save(resized_image_path.name, 'JPEG')
                resized_image_path.close()
                
                if not default_image:
                    os.unlink(image_path)  # 元の一時ファイルを削除
                    
                image_path = resized_image_path.name
            except Exception as e:
                print(f"画像リサイズエラー: {e}")
                
            # 出力パスを決定
            output_folder = self.output_var.get() or os.path.dirname(mp3_path)
            output_filename = self.generate_output_filename(mp3_path)
            output_path = os.path.join(output_folder, output_filename)
            
            # MoviePyで動画を作成
            audio_clip = mp.AudioFileClip(mp3_path)
            image_clip = mp.ImageClip(image_path, duration=audio_clip.duration)
            
            final_clip = image_clip.set_audio(audio_clip)
            final_clip.write_videofile(
                output_path,
                fps=1,  # 静止画なので低いFPSで十分
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # クリーンアップ
            audio_clip.close()
            image_clip.close()
            final_clip.close()
            os.unlink(image_path)
            
            return True, output_path
            
        except Exception as e:
            return False, str(e)
            
    def start_conversion(self):
        """変換処理を開始"""
        if not self.file_list:
            messagebox.showwarning("警告", "MP3ファイルを選択してください。")
            return
            
        # 設定を保存
        self.config["output_folder"] = self.output_var.get()
        self.config["video_format"] = self.format_var.get()
        self.config["filename_format"] = self.filename_var.get()
        self.config["quality"] = self.quality_var.get()
        self.save_config()
        
        # 変換を別スレッドで実行
        self.convert_btn.config(state='disabled')
        self.progress['maximum'] = len(self.file_list)
        self.progress['value'] = 0
        
        thread = threading.Thread(target=self.conversion_worker)
        thread.daemon = True
        thread.start()
        
    def conversion_worker(self):
        """変換処理のワーカー"""
        success_count = 0
        failed_files = []
        
        for i, mp3_path in enumerate(self.file_list):
            self.root.after(0, lambda i=i, path=mp3_path: self.status_label.config(
                text=f"変換中... ({i+1}/{len(self.file_list)}) {os.path.basename(path)}"))
            
            success, result = self.convert_single_file(mp3_path)
            
            if success:
                success_count += 1
            else:
                failed_files.append(f"{os.path.basename(mp3_path)}: {result}")
                
            self.root.after(0, lambda: self.progress.step())
            
        # 完了メッセージ
        self.root.after(0, self.conversion_complete, success_count, failed_files)
        
    def conversion_complete(self, success_count, failed_files):
        """変換完了処理"""
        self.convert_btn.config(state='normal')
        self.status_label.config(text="変換完了")
        
        message = f"変換が完了しました。\n成功: {success_count}件"
        
        if failed_files:
            message += f"\n失敗: {len(failed_files)}件\n\n失敗したファイル:\n"
            message += "\n".join(failed_files[:5])  # 最初の5件のみ表示
            if len(failed_files) > 5:
                message += f"\n... 他{len(failed_files)-5}件"
                
        messagebox.showinfo("変換完了", message)

def main():
    # tkinterdnd2が利用できない場合の代替処理
    try:
        root = tkdnd.TkinterDnD.Tk()
    except:
        root = tk.Tk()
        messagebox.showwarning("警告", "ドラッグ&ドロップ機能が利用できません。ファイル選択ボタンを使用してください。")
    
    app = MP3toMP4Converter(root)
    root.mainloop()

if __name__ == "__main__":
    main()