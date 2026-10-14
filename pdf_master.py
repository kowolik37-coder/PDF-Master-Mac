# -*- coding: utf-8 -*-
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PDFMasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Master by Kriss")
        self.root.geometry("630x650")
        self.root.minsize(590, 590)

        ikona_path = resource_path("ikona.ico")
        if os.path.exists(ikona_path):
            try:
                self.root.iconbitmap(ikona_path)
            except Exception:
                pass

        self._zbuduj_naglowek()
        self._zbuduj_zakladki()
        self._zbuduj_stopke()

    def _zbuduj_naglowek(self):
        f_top = tk.Frame(self.root, bg="#23272a", pady=10, padx=15)
        f_top.pack(fill="x")

        logo_path = resource_path("logo.png")
        if os.path.exists(logo_path):
            try:
                self.logo_img = tk.PhotoImage(file=logo_path)
                lbl_logo = tk.Label(f_top, image=self.logo_img, bg="#23272a")
                lbl_logo.pack(side="left", padx=(0, 12))
            except Exception:
                pass

        f_tytuly = tk.Frame(f_top, bg="#23272a")
        f_tytuly.pack(side="left")

        lbl_tytul = tk.Label(f_tytuly, text="PDF Master", font=("Segoe UI", 16, "bold"), fg="#f3f4f6", bg="#23272a")
        lbl_tytul.pack(anchor="w")

        lbl_autor = tk.Label(f_tytuly, text="Made by Kriss", font=("Segoe UI", 9, "italic"), fg="#9ca3af", bg="#23272a")
        lbl_autor.pack(anchor="w")

    def _zbuduj_stopke(self):
        f_bot = ttk.Frame(self.root, padding="6")
        f_bot.pack(side="bottom", fill="x")
        self.prog_bar = ttk.Progressbar(f_bot, mode="determinate")
        self.prog_bar.pack(fill="x", padx=10, pady=(2, 2))
        self.lbl_status = ttk.Label(f_bot, text="Gotowy do pracy.", font=("Segoe UI", 9))
        self.lbl_status.pack(anchor="w", padx=10)

    def _zbuduj_zakladki(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_merge = ttk.Frame(notebook, padding="10")
        self.tab_split = ttk.Frame(notebook, padding="10")
        self.tab_pdf2jpg = ttk.Frame(notebook, padding="10")
        self.tab_jpg2pdf = ttk.Frame(notebook, padding="10")
        self.tab_compress = ttk.Frame(notebook, padding="10")

        notebook.add(self.tab_merge, text=" 1. Łączenie PDF ")
        notebook.add(self.tab_split, text=" 2. Rozdzielanie ")
        notebook.add(self.tab_pdf2jpg, text=" 3. PDF -> JPG ")
        notebook.add(self.tab_jpg2pdf, text=" 4. JPG -> PDF ")
        notebook.add(self.tab_compress, text=" 5. Kompresja ")

        self._setup_tab_merge()
        self._setup_tab_split()
        self._setup_tab_pdf2jpg()
        self._setup_tab_jpg2pdf()
        self._setup_tab_compress()

    # ================= 1. ŁĄCZENIE PDF =================
    def _setup_tab_merge(self):
        ttk.Label(self.tab_merge, text="Dodaj pliki PDF i ułóż je w odpowiedniej kolejności:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        
        f_list = ttk.Frame(self.tab_merge)
        f_list.pack(fill="both", expand=True, pady=6)

        self.lb_merge = tk.Listbox(f_list, selectmode="single", font=("Segoe UI", 9))
        self.lb_merge.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(f_list, orient="vertical", command=self.lb_merge.yview)
        sb.pack(side="right", fill="y")
        self.lb_merge.config(yscrollcommand=sb.set)

        f_btns = ttk.Frame(self.tab_merge)
        f_btns.pack(fill="x", pady=4)
        ttk.Button(f_btns, text="+ Dodaj pliki", command=self._merge_add).pack(side="left", padx=2)
        ttk.Button(f_btns, text="W górę", command=lambda: self._list_move(self.lb_merge, -1)).pack(side="left", padx=2)
        ttk.Button(f_btns, text="W dół", command=lambda: self._list_move(self.lb_merge, 1)).pack(side="left", padx=2)
        ttk.Button(f_btns, text="Usuń", command=lambda: self._list_del(self.lb_merge)).pack(side="left", padx=2)
        ttk.Button(f_btns, text="Wyczyść", command=lambda: self.lb_merge.delete(0, tk.END)).pack(side="left", padx=2)

        ttk.Button(self.tab_merge, text="Połącz pliki w jeden PDF", command=self._merge_wykonaj).pack(fill="x", pady=8, ipady=3)

    def _merge_add(self):
        pliki = filedialog.askopenfilenames(filetypes=[("Pliki PDF", "*.pdf")])
        for p in pliki:
            self.lb_merge.insert(tk.END, p)

    def _list_move(self, lb, kierunek):
        sel = lb.curselection()
        if not sel: return
        idx = sel[0]
        n_idx = idx + kierunek
        if 0 <= n_idx < lb.size():
            tekst = lb.get(idx)
            lb.delete(idx)
            lb.insert(n_idx, tekst)
            lb.selection_set(n_idx)

    def _list_del(self, lb):
        sel = lb.curselection()
        if sel: lb.delete(sel[0])

    def _merge_wykonaj(self):
        pliki = list(self.lb_merge.get(0, tk.END))
        if len(pliki) < 2:
            messagebox.showwarning("Uwaga", "Dodaj co najmniej 2 pliki PDF do połączenia.")
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Plik PDF", "*.pdf")])
        if not out: return

        def watek():
            self._set_busy(True, "Łączenie plików...")
            try:
                merged = fitz.open()
                for i, p in enumerate(pliki):
                    doc = fitz.open(p)
                    merged.insert_pdf(doc)
                    doc.close()
                    self.prog_bar["value"] = ((i + 1) / len(pliki)) * 100
                merged.save(out)
                merged.close()
                messagebox.showinfo("Sukces", f"Pliki połączone pomyślnie!\nZapisano w: {out}")
            except Exception as e:
                messagebox.showerror("Błąd", str(e))
            finally:
                self._set_busy(False, "Gotowy.")
        threading.Thread(target=watek, daemon=True).start()

    # ================= 2. ROZDZIELANIE =================
    def _setup_tab_split(self):
        ttk.Label(self.tab_split, text="Wybierz plik PDF do rozdzielenia:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        f_p = ttk.Frame(self.tab_split)
        f_p.pack(fill="x", pady=4)
        self.split_in = ttk.Entry(f_p)
        self.split_in.pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(f_p, text="Przeglądaj...", command=self._split_browse).pack(side="right")
        self.split_info = ttk.Label(self.tab_split, text="Liczba stron: -", foreground="gray")
        self.split_info.pack(anchor="w")

        f_tryb = ttk.LabelFrame(self.tab_split, text=" Tryb rozdzielania ", padding=10)
        f_tryb.pack(fill="x", pady=10)
        self.split_mode = tk.IntVar(value=1)
        ttk.Radiobutton(f_tryb, text="Rozdziel wszystkie strony na osobne pliki PDF", variable=self.split_mode, value=1).pack(anchor="w", pady=2)
        ttk.Radiobutton(f_tryb, text="Wyodrębnij wybrane strony", variable=self.split_mode, value=2).pack(anchor="w", pady=2)

        f_zakres = ttk.Frame(f_tryb)
        f_zakres.pack(fill="x", padx=20, pady=4)
        ttk.Label(f_zakres, text="Strony (np. 3 lub 4, 7, 9 lub 2-6):").pack(side="left")
        self.split_pages_entry = ttk.Entry(f_zakres, width=25)
        self.split_pages_entry.pack(side="left", padx=6)

        self.split_osobne = tk.BooleanVar(value=True)
        ttk.Checkbutton(f_tryb, text="Zapisz każdą wybraną stronę jako osobny plik (jeśli odznaczysz: połączy w jeden wyciąg)", variable=self.split_osobne).pack(anchor="w", padx=20, pady=4)

        ttk.Button(self.tab_split, text="Rozdziel / Wyodrębnij", command=self._split_wykonaj).pack(fill="x", pady=10, ipady=3)

    def _split_browse(self):
        p = filedialog.askopenfilename(filetypes=[("Pliki PDF", "*.pdf")])
        if p:
            self.split_in.delete(0, tk.END)
            self.split_in.insert(0, p)
            try:
                doc = fitz.open(p)
                self.split_info.config(text=f"Liczba stron w pliku: {len(doc)}")
                doc.close()
            except Exception:
                self.split_info.config(text="Błąd odczytu pliku.")

    def _split_wykonaj(self):
        plik = self.split_in.get().strip()
        if not plik or not os.path.exists(plik):
            messagebox.showwarning("Uwaga", "Wskaż prawidłowy plik PDF.")
            return

        mode = self.split_mode.get()
        doc = fitz.open(plik)
        total = len(doc)
        nazwa_baza = os.path.splitext(os.path.basename(plik))[0]

        if mode == 1:
            folder = filedialog.askdirectory(title="Wybierz folder zapisu pojedynczych stron")
            if not folder: 
                doc.close(); return
            def watek1():
                self._set_busy(True, "Zapisywanie stron...")
                try:
                    for i in range(total):
                        n = fitz.open()
                        n.insert_pdf(doc, from_page=i, to_page=i)
                        n.save(os.path.join(folder, f"{nazwa_baza}_strona_{i+1}.pdf"))
                        n.close()
                        self.prog_bar["value"] = ((i + 1) / total) * 100
                    doc.close()
                    messagebox.showinfo("Sukces", f"Wyodrębniono {total} stron do folderu:\n{folder}")
                except Exception as e:
                    messagebox.showerror("Błąd", str(e))
                finally:
                    self._set_busy(False, "Gotowy.")
            threading.Thread(target=watek1, daemon=True).start()
        else:
            tekst = self.split_pages_entry.get().strip()
            strony = self._parsuj_strony(tekst, total)
            if not strony:
                doc.close()
                messagebox.showwarning("Uwaga", f"Błędny format stron. Wpisz np. 3 lub 4, 7, 9 (zakres 1 do {total}).")
                return

            if self.split_osobne.get():
                folder = filedialog.askdirectory(title="Wybierz folder zapisu stron")
                if not folder: 
                    doc.close(); return
                def watek2():
                    self._set_busy(True, "Wyodrębnianie...")
                    try:
                        for nr, s_idx in enumerate(strony):
                            n = fitz.open()
                            n.insert_pdf(doc, from_page=s_idx, to_page=s_idx)
                            n.save(os.path.join(folder, f"{nazwa_baza}_strona_{s_idx+1}.pdf"))
                            n.close()
                            self.prog_bar["value"] = ((nr + 1) / len(strony)) * 100
                        doc.close()
                        messagebox.showinfo("Sukces", f"Wyodrębniono {len(strony)} stron do folderu:\n{folder}")
                    except Exception as e:
                        messagebox.showerror("Błąd", str(e))
                    finally:
                        self._set_busy(False, "Gotowy.")
                threading.Thread(target=watek2, daemon=True).start()
            else:
                out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"{nazwa_baza}_wyciag.pdf")
                if not out: 
                    doc.close(); return
                def watek3():
                    self._set_busy(True, "Tworzenie wyciągu...")
                    try:
                        n = fitz.open()
                        for s_idx in strony:
                            n.insert_pdf(doc, from_page=s_idx, to_page=s_idx)
                        n.save(out)
                        n.close()
                        doc.close()
                        messagebox.showinfo("Sukces", f"Wyciąg zapisany w:\n{out}")
                    except Exception as e:
                        messagebox.showerror("Błąd", str(e))
                    finally:
                        self._set_busy(False, "Gotowy.")
                threading.Thread(target=watek3, daemon=True).start()

    def _parsuj_strony(self, tekst, max_s):
        wynik = []
        try:
            czesi = tekst.replace(" ", "").split(",")
            for c in czesi:
                if "-" in c:
                    od, do = c.split("-")
                    for x in range(int(od), int(do) + 1):
                        if 1 <= x <= max_s and (x - 1) not in wynik:
                            wynik.append(x - 1)
                else:
                    x = int(c)
                    if 1 <= x <= max_s and (x - 1) not in wynik:
                        wynik.append(x - 1)
            return sorted(wynik)
        except Exception:
            return []

    # ================= 3. PDF -> JPG =================
    def _setup_tab_pdf2jpg(self):
        ttk.Label(self.tab_pdf2jpg, text="Wybierz plik PDF do eksportu do obrazów JPG:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        f_p = ttk.Frame(self.tab_pdf2jpg)
        f_p.pack(fill="x", pady=4)
        self.p2j_in = ttk.Entry(f_p)
        self.p2j_in.pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(f_p, text="Przeglądaj...", command=lambda: self._proste_przegladaj(self.p2j_in, [("Pliki PDF", "*.pdf")])).pack(side="right")

        f_opt = ttk.LabelFrame(self.tab_pdf2jpg, text=" Parametry obrazu ", padding=10)
        f_opt.pack(fill="x", pady=10)
        f_d = ttk.Frame(f_opt)
        f_d.pack(fill="x")
        ttk.Label(f_d, text="Rozdzielczość (DPI):").pack(side="left")
        self.lbl_p2j_dpi = ttk.Label(f_d, text="150 DPI", font=("Segoe UI", 9, "bold"))
        self.lbl_p2j_dpi.pack(side="right")
        self.p2j_dpi = ttk.Scale(f_opt, from_=100, to=300, command=lambda v: self.lbl_p2j_dpi.config(text=f"{int(float(v))} DPI"))
        self.p2j_dpi.set(150)
        self.p2j_dpi.pack(fill="x", pady=(2, 8))

        ttk.Button(self.tab_pdf2jpg, text="Konwertuj strony do JPG", command=self._pdf2jpg_wykonaj).pack(fill="x", pady=10, ipady=3)

    def _pdf2jpg_wykonaj(self):
        plik = self.p2j_in.get().strip()
        if not plik or not os.path.exists(plik):
            messagebox.showwarning("Uwaga", "Wybierz plik PDF.")
            return
        folder = filedialog.askdirectory(title="Wybierz folder zapisu plików JPG")
        if not folder: return
        dpi = int(self.p2j_dpi.get())
        nazwa_baza = os.path.splitext(os.path.basename(plik))[0]

        def watek():
            self._set_busy(True, "Renderowanie do JPG...")
            try:
                doc = fitz.open(plik)
                total = len(doc)
                skala = dpi / 72
                m = fitz.Matrix(skala, skala)
                for i, page in enumerate(doc):
                    pix = page.get_pixmap(matrix=m, alpha=False)
                    pix.save(os.path.join(folder, f"{nazwa_baza}_strona_{i+1:03d}.jpg"))
                    self.prog_bar["value"] = ((i + 1) / total) * 100
                doc.close()
                messagebox.showinfo("Sukces", f"Zapisano {total} plików JPG w:\n{folder}")
            except Exception as e:
                messagebox.showerror("Błąd", str(e))
            finally:
                self._set_busy(False, "Gotowy.")
        threading.Thread(target=watek, daemon=True).start()

    # ================= 4. JPG -> PDF =================
    def _setup_tab_jpg2pdf(self):
        ttk.Label(self.tab_jpg2pdf, text="Dodaj obrazy JPG/PNG do połączenia w jeden plik PDF:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        f_list = ttk.Frame(self.tab_jpg2pdf)
        f_list.pack(fill="both", expand=True, pady=6)
        self.lb_jpg = tk.Listbox(f_list, selectmode="single", font=("Segoe UI", 9))
        self.lb_jpg.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(f_list, orient="vertical", command=self.lb_jpg.yview)
        sb.pack(side="right", fill="y")
        self.lb_jpg.config(yscrollcommand=sb.set)

        f_btns = ttk.Frame(self.tab_jpg2pdf)
        f_btns.pack(fill="x", pady=4)
        ttk.Button(f_btns, text="+ Dodaj obrazy", command=self._jpg2pdf_add).pack(side="left", padx=2)
        ttk.Button(f_btns, text="W górę", command=lambda: self._list_move(self.lb_jpg, -1)).pack(side="left", padx=2)
        ttk.Button(f_btns, text="W dół", command=lambda: self._list_move(self.lb_jpg, 1)).pack(side="left", padx=2)
        ttk.Button(f_btns, text="Usuń", command=lambda: self._list_del(self.lb_jpg)).pack(side="left", padx=2)
        ttk.Button(f_btns, text="Wyczyść", command=lambda: self.lb_jpg.delete(0, tk.END)).pack(side="left", padx=2)

        ttk.Button(self.tab_jpg2pdf, text="Stwórz PDF ze wskazanych obrazów", command=self._jpg2pdf_wykonaj).pack(fill="x", pady=8, ipady=3)

    def _jpg2pdf_add(self):
        pliki = filedialog.askopenfilenames(filetypes=[("Obrazy", "*.jpg *.jpeg *.png *.bmp")])
        for p in pliki:
            self.lb_jpg.insert(tk.END, p)

    def _jpg2pdf_wykonaj(self):
        pliki = list(self.lb_jpg.get(0, tk.END))
        if not pliki:
            messagebox.showwarning("Uwaga", "Dodaj co najmniej jeden obraz.")
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Plik PDF", "*.pdf")])
        if not out: return

        def watek():
            self._set_busy(True, "Tworzenie PDF z obrazów...")
            try:
                nowy_doc = fitz.open()
                total = len(pliki)
                for i, img_path in enumerate(pliki):
                    img_doc = fitz.open(img_path)
                    pdf_bytes = img_doc.convert_to_pdf()
                    img_doc.close()
                    page_pdf = fitz.open("pdf", pdf_bytes)
                    nowy_doc.insert_pdf(page_pdf)
                    page_pdf.close()
                    self.prog_bar["value"] = ((i + 1) / total) * 100
                nowy_doc.save(out, deflate=True)
                nowy_doc.close()
                messagebox.showinfo("Sukces", f"PDF utworzony pomyślnie!\nZapisano w: {out}")
            except Exception as e:
                messagebox.showerror("Błąd", str(e))
            finally:
                self._set_busy(False, "Gotowy.")
        threading.Thread(target=watek, daemon=True).start()

    # ================= 5. KOMPRESJA =================
    def _setup_tab_compress(self):
        ttk.Label(self.tab_compress, text="Wybierz plik PDF do kompresji (optymalizacja wizualna):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        f_p = ttk.Frame(self.tab_compress)
        f_p.pack(fill="x", pady=4)
        self.cmp_in = ttk.Entry(f_p)
        self.cmp_in.pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(f_p, text="Przeglądaj...", command=lambda: self._proste_przegladaj(self.cmp_in, [("Pliki PDF", "*.pdf")])).pack(side="right")

        f_opt = ttk.LabelFrame(self.tab_compress, text=" Ustawienia jakości kompresji ", padding=10)
        f_opt.pack(fill="x", pady=10)

        f_d = ttk.Frame(f_opt)
        f_d.pack(fill="x")
        ttk.Label(f_d, text="Rozdzielczość (DPI):").pack(side="left")
        self.lbl_cmp_dpi = ttk.Label(f_d, text="130 DPI (zalecane)", font=("Segoe UI", 9, "bold"))
        self.lbl_cmp_dpi.pack(side="right")
        self.cmp_dpi = ttk.Scale(f_opt, from_=72, to=200, command=lambda v: self.lbl_cmp_dpi.config(text=f"{int(float(v))} DPI"))
        self.cmp_dpi.set(130)
        self.cmp_dpi.pack(fill="x", pady=(2, 8))

        f_q = ttk.Frame(f_opt)
        f_q.pack(fill="x")
        ttk.Label(f_q, text="Jakość obrazu JPEG:").pack(side="left")
        self.lbl_cmp_q = ttk.Label(f_q, text="65%", font=("Segoe UI", 9, "bold"))
        self.lbl_cmp_q.pack(side="right")
        self.cmp_q = ttk.Scale(f_opt, from_=20, to=95, command=lambda v: self.lbl_cmp_q.config(text=f"{int(float(v))}%"))
        self.cmp_q.set(65)
        self.cmp_q.pack(fill="x", pady=(2, 0))

        ttk.Button(self.tab_compress, text="Kompresuj PDF", command=self._compress_wykonaj).pack(fill="x", pady=10, ipady=3)

    def _compress_wykonaj(self):
        plik = self.cmp_in.get().strip()
        if not plik or not os.path.exists(plik):
            messagebox.showwarning("Uwaga", "Wskaż prawidłowy plik PDF.")
            return

        katalog, nazwa = os.path.split(plik)
        nazwa_baza, ext = os.path.splitext(nazwa)
        out = filedialog.asksaveasfilename(
            title="Gdzie zapisać odchudzony plik?",
            initialfile=f"{nazwa_baza}_lekki.pdf",
            defaultextension=".pdf",
            filetypes=[("Pliki PDF", "*.pdf")]
        )
        if not out: return

        dpi = int(self.cmp_dpi.get())
        q = int(self.cmp_q.get())

        def watek():
            self._set_busy(True, "Kompresowanie pliku...")
            try:
                doc = fitz.open(plik)
                nowy_doc = fitz.open()
                total = len(doc)
                skala = dpi / 72
                m = fitz.Matrix(skala, skala)

                for i, page in enumerate(doc):
                    pix = page.get_pixmap(matrix=m, alpha=False)
                    jpg_data = pix.tobytes(output="jpeg", jpg_quality=q)
                    np = nowy_doc.new_page(width=page.rect.width, height=page.rect.height)
                    np.insert_image(np.rect, stream=jpg_data)
                    self.prog_bar["value"] = ((i + 1) / total) * 100

                nowy_doc.save(out, garbage=4, deflate=True)
                nowy_doc.close()
                doc.close()

                r_przed = os.path.getsize(plik) / (1024 * 1024)
                r_po = os.path.getsize(out) / (1024 * 1024)
                messagebox.showinfo("Sukces", f"Gotowe!\n\nPrzed: {r_przed:.2f} MB\nPo: {r_po:.2f} MB\n\nZapisano w:\n{out}")
            except Exception as e:
                messagebox.showerror("Błąd", str(e))
            finally:
                self._set_busy(False, "Gotowy.")
        threading.Thread(target=watek, daemon=True).start()

    # ================= POMOCNICZE =================
    def _proste_przegladaj(self, entry, ft):
        p = filedialog.askopenfilename(filetypes=ft)
        if p:
            entry.delete(0, tk.END)
            entry.insert(0, p)

    def _set_busy(self, zajety, msg):
        self.lbl_status.config(text=msg)
        if not zajety:
            self.prog_bar["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMasterApp(root)
    root.mainloop()