# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
import os
from PIL import Image
import io

class PDFCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 압축 프로그램")
        self.root.geometry("500x400")
        
        self.selected_file = None
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="PDF 압축 프로그램", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(main_frame, text="선택된 파일:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_label = ttk.Label(main_frame, text="파일을 선택하세요", foreground="gray")
        self.file_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Button(main_frame, text="PDF 파일 선택", command=self.select_file).grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Label(main_frame, text="압축 품질:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value="높음")
        quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var, values=["높음", "보통", "낮음"], state="readonly")
        quality_combo.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Button(main_frame, text="압축 시작", command=self.compress_pdf).grid(row=4, column=0, columnspan=2, pady=20)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.status_label = ttk.Label(main_frame, text="준비됨")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        for child in main_frame.winfo_children():
            child.grid_configure(padx=5, pady=2)
    
    def select_file(self):
        # Ensure file dialog is called on the main thread
        self.root.after(0, self._select_file_dialog)
    
    def _select_file_dialog(self):
        file_path = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=os.path.basename(file_path), foreground="black")
            self.status_label.config(text=f"파일 선택됨: {os.path.basename(file_path)}")
    
    def compress_pdf(self):
        if not self.selected_file:
            messagebox.showerror("오류", "PDF 파일을 먼저 선택하세요!")
            return
        
        self.progress.start()
        self.status_label.config(text="압축 중...")
        self.root.update()
        
        try:
            output_path = self.selected_file.replace('.pdf', '_compressed.pdf')
            self.compress_pdf_file(self.selected_file, output_path)
            
            original_size = os.path.getsize(self.selected_file)
            compressed_size = os.path.getsize(output_path)
            reduction_percent = ((original_size - compressed_size) / original_size) * 100
            
            self.progress.stop()
            self.status_label.config(text=f"압축 완료! 크기 감소: {reduction_percent:.1f}%")
            
            messagebox.showinfo("완료", 
                f"압축이 완료되었습니다!\n"
                f"원본 크기: {self.format_size(original_size)}\n"
                f"압축 후 크기: {self.format_size(compressed_size)}\n"
                f"파일 저장 위치: {output_path}")
                
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="압축 실패")
            messagebox.showerror("오류", f"압축 중 오류가 발생했습니다:\n{str(e)}")
    
    def compress_pdf_file(self, input_path, output_path):
        quality_settings = {
            "높음": 85,
            "보통": 70,
            "낮음": 50
        }
        quality = quality_settings[self.quality_var.get()]
        
        with open(input_path, 'rb') as input_file:
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()
            
            for page in reader.pages:
                page.compress_content_streams()
                
                if "/Resources" in page and "/XObject" in page["/Resources"]:
                    xObject = page["/Resources"]["/XObject"].get_object()
                    
                    for obj in xObject:
                        if xObject[obj]["/Subtype"] == "/Image":
                            try:
                                self.compress_image_in_page(xObject[obj], quality)
                            except Exception:
                                pass
                
                writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
    
    def compress_image_in_page(self, img_obj, quality):
        try:
            img_data = img_obj._data
            img = Image.open(io.BytesIO(img_data))
            
            output = io.BytesIO()
            img.save(output, format='JPEG', optimize=True, quality=quality)
            
            img_obj._data = output.getvalue()
        except Exception:
            pass
    
    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

def main():
    root = tk.Tk()
    PDFCompressor(root)
    root.mainloop()

if __name__ == "__main__":
    main()