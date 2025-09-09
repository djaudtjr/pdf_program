import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import shutil
import sys
import os
from tkinter import font

# --- PDF 압축 핵심 기능 ---
def compress_pdf(input_path, output_path, quality_level):
    """
    Ghostscript를 사용하여 PDF를 압축합니다.
    - quality_level: 'screen', 'ebook', 'printer', 'prepress' 중 하나
    """
    gs_command = find_ghostscript_executable()
    if not gs_command:
        messagebox.showerror(
            "오류",
            "Ghostscript를 찾을 수 없습니다.\n"
            "프로그램을 사용하려면 Ghostscript를 설치하고\n"
            "PATH 환경 변수에 추가해야 합니다."
        )
        return False

    # Ghostscript 명령어 구성
    command = [
        gs_command,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{quality_level}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    try:
        # 서브프로세스로 Ghostscript 실행
        # Windows에서는 CREATE_NO_WINDOW 플래그로 콘솔 창 숨김
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo
        )
        return True
    except FileNotFoundError:
        messagebox.showerror("오류", "Ghostscript를 실행할 수 없습니다. 설치를 확인해주세요.")
        return False
    except subprocess.CalledProcessError as e:
        error_message = f"PDF 압축 중 오류가 발생했습니다.\n{e.stderr.decode('utf-8', errors='ignore')}"
        messagebox.showerror("압축 오류", error_message)
        return False
    except Exception as e:
        messagebox.showerror("알 수 없는 오류", f"예상치 못한 오류가 발생했습니다: {e}")
        return False

def find_ghostscript_executable():
    """
    시스템에서 Ghostscript 실행 파일을 찾습니다.
    (Windows: gswin64c.exe, gswin32c.exe / Linux/macOS: gs)
    """
    if sys.platform == "win32":
        for cmd in ["gswin64c", "gswin32c", "gs"]:
            if shutil.which(cmd):
                return shutil.which(cmd)
    else: # Linux, macOS
        if shutil.which("gs"):
            return shutil.which("gs")
    return None

# --- GUI 애플리케이션 ---
class PDFCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🗜️ PDF 압축기 Pro")
        self.root.geometry("650x700")  # 내용에 맞게 크기 조정
        self.root.resizable(True, True)
        self.root.minsize(500, 600)  # 최소 크기 설정

        # 모던한 색상 테마 정의 (가독성 개선)
        self.colors = {
            'primary': '#2E86AB',      # 메인 블루
            'secondary': '#A23B72',    # 액센트 핑크
            'success': '#F18F01',      # 성공 오렌지
            'background': '#F8FAFC',   # 배경 더 밝은 회색
            'surface': '#FFFFFF',      # 카드 배경 흰색
            'text_primary': '#1A202C', # 메인 텍스트 (더 진한 색상)
            'text_secondary': '#4A5568', # 보조 텍스트 (더 진한 색상)
            'border': '#E2E8F0',       # 테두리 색상
            'focus_bg': '#EBF8FF',     # 포커스 배경색
            'hover_bg': '#F7FAFC'      # 호버 배경색
        }

        # 루트 윈도우 배경색 설정
        self.root.configure(bg=self.colors['background'])

        self.input_file_path = ""

        # 커스텀 폰트 설정 (macOS 호환성을 위해 시스템 폰트 사용)
        try:
            self.fonts = {
                'title': font.Font(family='Helvetica Neue', size=20, weight='bold'),
                'subtitle': font.Font(family='Helvetica Neue', size=14, weight='normal'),
                'body': font.Font(family='Helvetica', size=11, weight='normal'),
                'button': font.Font(family='Helvetica', size=11, weight='bold')
            }
        except:
            # 폰트 로드 실패 시 기본 폰트 사용
            self.fonts = {
                'title': font.Font(size=20, weight='bold'),
                'subtitle': font.Font(size=14, weight='normal'),
                'body': font.Font(size=11, weight='normal'),
                'button': font.Font(size=11, weight='bold')
            }

        # 스타일 설정
        self.setup_styles()

        # 메인 컨테이너
        self.create_main_container()

    def setup_styles(self):
        """모던한 스타일 테마 설정"""
        self.style = ttk.Style()

        # 메인 버튼 스타일
        self.style.configure("Primary.TButton",
                           background=self.colors['primary'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor=self.colors['focus_bg'],
                           padding=(20, 12),
                           font=self.fonts['button'])

        self.style.map("Primary.TButton",
                      background=[('active', '#1E5F7A'),
                                ('pressed', '#1A4F66'),
                                ('focus', self.colors['primary'])])

        # 보조 버튼 스타일
        self.style.configure("Secondary.TButton",
                           background=self.colors['surface'],
                           foreground=self.colors['text_primary'],
                           borderwidth=1,
                           relief='solid',
                           focuscolor='none',
                           padding=(15, 8),
                           font=self.fonts['body'])

        self.style.map("Secondary.TButton",
                      background=[('active', self.colors['hover_bg']),
                                ('pressed', '#EDF2F7'),
                                ('focus', self.colors['focus_bg'])])

        # 카드 프레임 스타일
        self.style.configure("Card.TFrame",
                           background=self.colors['surface'],
                           relief='flat',
                           borderwidth=1)

        # 제목 라벨 스타일
        self.style.configure("Title.TLabel",
                           background=self.colors['background'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['title'])

        # 부제목 라벨 스타일
        self.style.configure("Subtitle.TLabel",
                           background=self.colors['surface'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['subtitle'])

        # 본문 라벨 스타일
        self.style.configure("Body.TLabel",
                           background=self.colors['surface'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['body'])

    def create_main_container(self):
        """메인 컨테이너와 UI 요소들 생성"""
        # 메인 컨테이너 프레임 (스크롤 없이 고정 크기)
        self.main_frame = ttk.Frame(self.root, padding="30 25")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 헤더 섹션
        self.create_header()

        # 파일 선택 섹션
        self.create_file_selection()

        # 품질 설정 섹션
        self.create_quality_settings()

        # 진행률 섹션
        self.create_progress_section()

        # 액션 버튼 섹션
        self.create_action_buttons()

    def create_header(self):
        """헤더 섹션 생성"""
        header_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding="25 20")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # 메인 제목
        title_label = ttk.Label(header_frame, text="🗜️ PDF 압축기 Pro", style="Title.TLabel")
        title_label.pack(pady=(0, 5))

        # 부제목
        subtitle_label = ttk.Label(header_frame,
                                 text="고품질 PDF 압축으로 파일 크기를 효율적으로 줄여보세요",
                                 style="Subtitle.TLabel")
        subtitle_label.pack()

    def create_file_selection(self):
        """파일 선택 섹션 생성"""
        file_card = ttk.Frame(self.main_frame, style="Card.TFrame", padding="20 15")
        file_card.pack(fill=tk.X, pady=(0, 12))

        # 섹션 제목
        section_title = ttk.Label(file_card, text="📁 파일 선택", style="Subtitle.TLabel")
        section_title.pack(anchor="w", pady=(0, 15))

        # 파일 선택 영역
        file_selection_frame = ttk.Frame(file_card)
        file_selection_frame.pack(fill=tk.X)

        # 파일 정보 표시 영역
        self.file_info_frame = ttk.Frame(file_selection_frame, style="Card.TFrame")
        self.file_info_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_label = ttk.Label(self.file_info_frame,
                                  text="📄 선택된 파일이 없습니다",
                                  style="Body.TLabel",
                                  padding="12 8")
        self.file_label.pack(anchor="w")

        # 파일 찾기 버튼
        browse_button = ttk.Button(file_selection_frame,
                                 text="🔍 파일 찾기",
                                 command=self.browse_file,
                                 style="Secondary.TButton")
        browse_button.pack(anchor="w")

    def create_quality_settings(self):
        """품질 설정 섹션 생성"""
        quality_card = ttk.Frame(self.main_frame, style="Card.TFrame", padding="20 15")
        quality_card.pack(fill=tk.X, pady=(0, 12))

        # 섹션 제목
        section_title = ttk.Label(quality_card, text="⚙️ 압축 품질 설정", style="Subtitle.TLabel")
        section_title.pack(anchor="w", pady=(0, 15))

        self.quality_var = tk.StringVar(value="ebook")

        # 품질 옵션들
        qualities = [
            ("🖥️ 화면용 (최대 압축)", "screen", "파일 크기 최소화, 화면 보기용"),
            ("📱 전자책용 (권장)", "ebook", "균형잡힌 품질과 크기"),
            ("🖨️ 인쇄용 (고품질)", "printer", "인쇄 품질 유지"),
            ("📚 출판용 (최고품질)", "prepress", "전문 출판용 최고 품질")
        ]

        for i, (text, value, description) in enumerate(qualities):
            option_frame = ttk.Frame(quality_card)
            option_frame.pack(fill=tk.X, pady=5)

            rb = ttk.Radiobutton(option_frame, text=text, variable=self.quality_var, value=value)
            rb.pack(anchor="w")

            desc_label = ttk.Label(option_frame, text=f"   {description}",
                                 foreground=self.colors['text_secondary'],
                                 font=('Helvetica', 9))
            desc_label.pack(anchor="w", padx=(20, 0))

    def create_progress_section(self):
        """진행률 표시 섹션 생성"""
        self.progress_card = ttk.Frame(self.main_frame, style="Card.TFrame", padding="20 15")

        # 진행률 바
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_card,
                                          variable=self.progress_var,
                                          maximum=100,
                                          length=400,
                                          mode='determinate')

        # 상태 라벨
        self.status_label = ttk.Label(self.progress_card,
                                    text="",
                                    style="Body.TLabel")

    def create_action_buttons(self):
        """액션 버튼 섹션 생성"""
        button_frame = ttk.Frame(self.main_frame, padding="0 5")
        button_frame.pack(fill=tk.X, pady=15)

        # 압축 시작 버튼
        self.compress_button = ttk.Button(button_frame,
                                        text="🚀 압축 시작하기",
                                        command=self.start_compression,
                                        style="Primary.TButton")
        self.compress_button.pack(fill=tk.X, ipady=5)

    def browse_file(self):
        # Ensure file dialog is called on the main thread
        self.root.after(0, self._browse_file_dialog)

    def _browse_file_dialog(self):
        """파일 선택 다이얼로그 처리"""
        file_path = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=(("PDF 파일", "*.pdf"), ("모든 파일", "*.*"))
        )
        if file_path:
            self.input_file_path = file_path

            # 파일 정보 업데이트
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB 단위

            # 파일 이름이 너무 길면 잘라서 표시
            display_name = file_name
            if len(display_name) > 40:
                display_name = display_name[:20] + "..." + display_name[-17:]

            # 파일 정보 표시 업데이트
            file_info_text = f"📄 {display_name}\n💾 크기: {file_size:.2f} MB"
            self.file_label.config(text=file_info_text)

    def start_compression(self):
        """압축 프로세스 시작"""
        if not self.input_file_path:
            messagebox.showwarning("⚠️ 알림", "먼저 압축할 PDF 파일을 선택해주세요.")
            return

        # 진행률 섹션 표시
        self.show_progress_section()

        # 파일 저장 다이얼로그 호출
        self.root.after(0, self._save_file_dialog)

    def show_progress_section(self):
        """진행률 섹션 표시"""
        self.progress_card.pack(fill=tk.X, pady=(0, 15))

        # 섹션 제목
        progress_title = ttk.Label(self.progress_card, text="📊 압축 진행률", style="Subtitle.TLabel")
        progress_title.pack(anchor="w", pady=(0, 15))

        # 진행률 바 표시
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # 상태 라벨 표시
        self.status_label.pack(anchor="w")

        # 파일 크기 정보 표시 프레임
        self.size_info_frame = ttk.Frame(self.progress_card)
        self.size_info_frame.pack(fill=tk.X, pady=(10, 0))

        # 원본 크기 라벨
        self.original_size_label = ttk.Label(self.size_info_frame,
                                           text="📄 원본 크기: 계산 중...",
                                           style="Body.TLabel")
        self.original_size_label.pack(anchor="w", pady=2)

        # 압축 후 크기 라벨
        self.compressed_size_label = ttk.Label(self.size_info_frame,
                                             text="🗜️ 압축 후 크기: 대기 중...",
                                             style="Body.TLabel")
        self.compressed_size_label.pack(anchor="w", pady=2)

        # 압축률 라벨
        self.compression_ratio_label = ttk.Label(self.size_info_frame,
                                               text="📈 압축률: 계산 중...",
                                               style="Body.TLabel")
        self.compression_ratio_label.pack(anchor="w", pady=2)

    def hide_progress_section(self):
        """진행률 섹션 숨기기"""
        self.progress_card.pack_forget()

    def update_progress(self, value, status_text):
        """진행률 업데이트"""
        self.progress_var.set(value)
        self.status_label.config(text=status_text)
        self.root.update()

    def _save_file_dialog(self):
        """저장 파일 다이얼로그 처리"""
        output_path = filedialog.asksaveasfilename(
            title="압축된 PDF 파일 저장",
            defaultextension=".pdf",
            filetypes=(("PDF 파일", "*.pdf"),),
            initialfile=f"{os.path.splitext(os.path.basename(self.input_file_path))[0]}_compressed.pdf"
        )

        if not output_path:
            self.hide_progress_section()
            return # 사용자가 저장을 취소한 경우

        # 압축 실행
        self.execute_compression(output_path)

    def execute_compression(self, output_path):
        """실제 압축 실행"""
        quality = self.quality_var.get()

        # UI 상태 업데이트
        self.compress_button.config(state='disabled', text="🔄 압축 중...")
        self.root.config(cursor="wait")

        # 원본 파일 크기 계산 및 표시
        try:
            original_size = os.path.getsize(self.input_file_path) / (1024 * 1024)  # MB
            self.original_size_label.config(text=f"📄 원본 크기: {original_size:.2f} MB")
            self.root.update()
        except Exception as e:
            self.original_size_label.config(text="📄 원본 크기: 계산 실패")

        # 진행률 업데이트
        self.update_progress(10, "🔍 파일 분석 중...")

        # 압축 실행
        self.update_progress(30, "🗜️ PDF 압축 중...")
        success = compress_pdf(self.input_file_path, output_path, quality)

        if success:
            # 압축 후 파일 크기 계산 및 표시
            try:
                compressed_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                self.compressed_size_label.config(text=f"🗜️ 압축 후 크기: {compressed_size:.2f} MB")

                # 압축률 계산 및 표시
                if original_size > 0:
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    self.compression_ratio_label.config(text=f"📈 압축률: {reduction:.1f}% 감소")
                else:
                    self.compression_ratio_label.config(text="📈 압축률: 계산 실패")

                self.root.update()
            except Exception as e:
                self.compressed_size_label.config(text="🗜️ 압축 후 크기: 계산 실패")
                self.compression_ratio_label.config(text="📈 압축률: 계산 실패")

        # UI 상태 복원
        self.root.config(cursor="")
        self.compress_button.config(state='normal', text="🚀 압축 시작하기")

        if success:
            self.update_progress(100, "✅ 압축 완료!")
            self.show_compression_result(output_path)
        else:
            self.update_progress(0, "❌ 압축 실패")
            self.compressed_size_label.config(text="🗜️ 압축 후 크기: 압축 실패")
            self.compression_ratio_label.config(text="📈 압축률: 압축 실패")
            self.hide_progress_section()

    def show_compression_result(self, output_path):
        """압축 결과 표시"""
        try:
            original_size = os.path.getsize(self.input_file_path) / (1024 * 1024) # MB
            compressed_size = os.path.getsize(output_path) / (1024 * 1024) # MB
            reduction = ((original_size - compressed_size) / original_size) * 100

            # 결과 메시지 생성
            result_message = (
                f"🎉 압축이 성공적으로 완료되었습니다!\n\n"
                f"📊 압축 결과:\n"
                f"   • 원본 크기: {original_size:.2f} MB\n"
                f"   • 압축 후 크기: {compressed_size:.2f} MB\n"
                f"   • 파일 크기 감소율: {reduction:.1f}%\n\n"
                f"💾 저장 위치: {os.path.basename(output_path)}"
            )

            # 결과 다이얼로그 표시
            messagebox.showinfo("✅ 압축 완료", result_message)

            # 진행률 섹션 숨기기
            self.root.after(3000, self.hide_progress_section)  # 3초 후 숨기기

        except Exception as e:
            messagebox.showerror("❌ 오류", f"결과 확인 중 오류가 발생했습니다: {e}")
            self.hide_progress_section()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFCompressorApp(root)
    root.mainloop()