from cx_Freeze import setup, Executable
import sys

# 依存関係
build_exe_options = {
    "packages": [
        "tkinter", "tkinterdnd2", "PIL", "mutagen", "moviepy", 
        "pathlib", "json", "tempfile", "threading", "datetime", "os"
    ],
    "include_files": [],
    "excludes": ["test", "unittest"],
}

# 実行可能ファイルの設定
executables = [
    Executable(
        "mp3_to_mp4_converter.py",
        base="Win32GUI" if sys.platform == "win32" else None,
        target_name="MP3toMP4Converter.exe",
        icon=None  # アイコンファイルがあれば指定
    )
]

setup(
    name="MP3 to MP4 Converter",
    version="1.0",
    description="MP3ファイルを動画(MP4)に変換するツール",
    options={"build_exe": build_exe_options},
    executables=executables
)