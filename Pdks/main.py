# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os
import shutil
import cv2
import face_recognition
import csv
import datetime
# === Klasör Kontrolü ===
if not os.path.exists("known_faces"):
    os.makedirs("known_faces")
if not os.path.exists("yoklama.csv"):
    with open("yoklama.csv", "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["İsim Soyisim", "Saat", "Tarih", "İşlem"])
# === MODÜL 1: Bilgisayardan yüz resmi ekle ===
def add_face_from_pc():
    filepath = filedialog.askopenfilename(
        title="Yüz resmi seç",
        filetypes=[("Resim dosyaları", "*.jpg *.jpeg *.png")]
    )

    if not filepath:
        return

    name = simpledialog.askstring("İsim Girişi", "Lütfen 'İsim Soyisim' şeklinde girin:")

    if not name or len(name.strip().split()) < 2:
        messagebox.showerror("Hata", "Lütfen geçerli bir 'İsim Soyisim' girin.")
        return

    ext = os.path.splitext(filepath)[1]
    new_filename = f"{name.strip()}{ext}"
    dest_path = os.path.join("known_faces", new_filename)

    try:
        shutil.copy(filepath, dest_path)
        messagebox.showinfo("Başarılı", f"{name} başarıyla eklendi.")
    except Exception as e:
        messagebox.showerror("Hata", f"Dosya kopyalanamadı: {str(e)}")
# === MODÜL 2: Kameradan yüz resmi ekle ===
def add_face_from_camera():
    cap = cv2.VideoCapture(0)
    messagebox.showinfo("Bilgi", "Yüz eklemek için 'P' tuşuna bas.\n'Q' ile çıkabilirsin.")

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Hata", "Kamera açılamadı.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        # Yüz kutularını çiz
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow("Kameradan Yuz Ekleme (P: Kaydet, Q: Cik)", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('p'):
            if len(face_locations) != 1:
                messagebox.showwarning("Uyari", "Lütfen yalnızca bir yüzle kameraya bakın.")
                continue

            name = simpledialog.askstring("İsim Girişi", "Yüz algılandı. Lütfen 'İsim Soyisim' girin:")
            if not name or len(name.strip().split()) < 2:
                messagebox.showerror("Hata", "Geçersiz isim formatı.")
                continue

            filename = f"{name.strip()}.jpg"
            filepath = os.path.join("known_faces", filename)
            cv2.imwrite(filepath, frame)
            messagebox.showinfo("Başarılı", f"{name} başarıyla kaydedildi.")
            break

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
# === MODÜL 3: Yoklama alma  ===
def start_attendance():
    cap = cv2.VideoCapture(0)
    messagebox.showinfo("Bilgi", "GİRİŞ kaydı başladı. Bilinen yüzler otomatik GİRİŞ yapılır.\nBilinmeyen yüz için 'P', çıkış için 'Q' tuşu kullanılabilir.")

    known_encodings = []
    known_names = []

    for filename in os.listdir("known_faces"):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join("known_faces", filename)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])

    last_recorded_name = None
    frame_count = 0  # 👈 Frame sayacı

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Hata", "Kamera görüntüsü alınamadı.")
            break

        frame_count += 1
        if frame_count % 5 != 0:
            # Sadece her 5 karede bir işlem yap
            cv2.imshow("Giris Kamerasi (Bilinmeyen icin P, Cikis icin Q)", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # 👈 Görüntüyü küçült
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        current_names = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            name = "Bilinmeyen"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

            current_names.append(name)

            # Koordinatları geri büyüt (çünkü küçültmüştük)
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Ekranda çizim
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 20), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 0), 1)

            # Bilinen ve son kayıttan farklı ise kayıt yap
            if name != "Bilinmeyen" and name != last_recorded_name:
                now = datetime.datetime.now()
                date_str = now.strftime("%d.%m.%Y")
                time_str = now.strftime("%H:%M:%S")

                with open("yoklama.csv", "a", newline="", encoding="utf-8-sig") as file:
                    writer = csv.writer(file)
                    writer.writerow([name, time_str, date_str, "Giriş"])

                messagebox.showinfo("Yoklama", f"{name} için GİRİŞ işlemi kaydedildi.")
                last_recorded_name = name

        cv2.imshow("Giris Kamerasi (Bilinmeyen icin P, Cikis icin Q)", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('p'):
            if len(face_encodings) != 1:
                messagebox.showwarning("Uyarı", "Lütfen yalnızca bir yüzle kameraya bakın.")
                continue

            face_encoding = face_encodings[0]
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            name = "Bilinmeyen"

            if True in matches:
                continue  # Zaten biliniyor, tekrar kayıt etme

            name_input = simpledialog.askstring("Yeni Kişi", "Bilinmeyen yüz tespit edildi. İsim Soyisim girin:")
            if not name_input or len(name_input.strip().split()) < 2:
                messagebox.showerror("Hata", "Geçersiz isim.")
                continue

            name = name_input.strip()
            filename = f"{name}.jpg"
            filepath = os.path.join("known_faces", filename)
            cv2.imwrite(filepath, frame)
            messagebox.showinfo("Kayıt Başarılı", f"{name} klasöre eklendi.")
            known_encodings.append(face_encoding)
            known_names.append(name)

            now = datetime.datetime.now()
            date_str = now.strftime("%d.%m.%Y")
            time_str = now.strftime("%H:%M:%S")

            with open("yoklama.csv", "a", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow([name, time_str, date_str, "Giriş"])

            messagebox.showinfo("Yoklama", f"{name} için GİRİŞ işlemi kaydedildi.")
            last_recorded_name = name

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



# === MODÜL 4: Yoklama listesi Giriş ===
def show_attendance_list():
    if not os.path.exists("yoklama.csv"):
        messagebox.showerror("Hata", "yoklama.csv dosyası bulunamadı.")
        return

    table_window = tk.Toplevel()
    table_window.title("Yoklama Listesi")
    table_window.geometry("700x600")

    with open("yoklama.csv", newline='', encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if not rows:
        tk.Label(table_window, text="Yoklama kaydı bulunamadı.").pack()
        return

    header = rows[0]
    data_rows = rows[1:]

    for col, h in enumerate(header):
        e = tk.Label(table_window, text=h, relief="solid", width=20, bg="lightblue", font=('Helvetica', 10, 'bold'))
        e.grid(row=0, column=col, sticky="nsew")

    for row_idx, row_data in enumerate(data_rows):
        for col_idx, cell_data in enumerate(row_data):
            e = tk.Label(table_window, text=cell_data, relief="solid", width=20, font=('Helvetica', 10))
            e.grid(row=row_idx + 1, column=col_idx, sticky="nsew")

# === MODÜL 5: Son giriş çıkış paneli ===
def show_recent_attendance(root_frame):
    # Önceki içeriği temizle
    for widget in root_frame.winfo_children():
        widget.destroy()

    # Başlık
    title = tk.Label(root_frame, text="Son Giriş ve Çıkışlar", font=("Helvetica", 13, "bold"), bg="#f0f0f0")
    title.grid(row=0, column=0, columnspan=4, pady=(0, 10))

    # Dosya yoksa
    if not os.path.exists("yoklama.csv"):
        tk.Label(root_frame, text="Kayıt bulunamadı", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=1, column=0, columnspan=4)
        return

    # Dosya okunur
    with open("yoklama.csv", newline='', encoding="utf-8-sig") as file:
        reader = list(csv.reader(file))

    # Sadece başlık varsa
    if len(reader) <= 1:
        tk.Label(root_frame, text="Henüz kayıt yapılmadı", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=1, column=0, columnspan=4)
        return

    header = reader[0]
    data_rows = reader[1:][-5:]  # Son 5 kayıt alınır

    # Kolon genişlikleri (sırasıyla: İsim, Saat, Tarih, İşlem)
    column_widths = [30, 10, 12, 10]

    # Başlık satırı
    for col_index, h in enumerate(header):
        width = column_widths[col_index] if col_index < len(column_widths) else 15
        e = tk.Label(root_frame, text=h, relief="solid", width=width, bg="lightblue", font=("Helvetica", 10, "bold"))
        e.grid(row=1, column=col_index, padx=1, pady=1)

    # Veri satırları
    for row_index, row_data in enumerate(data_rows, start=2):
        for col_index, cell_data in enumerate(row_data):
            width = column_widths[col_index] if col_index < len(column_widths) else 15
            e = tk.Label(root_frame, text=cell_data, relief="solid", width=width, font=("Helvetica", 10))
            e.grid(row=row_index, column=col_index, padx=1, pady=1)
def periodic_refresh():
    show_recent_attendance(recent_frame)
    root.after(5000, periodic_refresh)
# === Ana Pencere ===
root = tk.Tk()
root.title("Yüz Tanıma Yoklama Sistemi")

# Pencere boyutu ekran ortasına göre ayarlanır
window_width = 1000
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
root.configure(bg="#f0f0f0")
root.resizable(True, True)

# === İkon Ayarı ===
icon_path = "iconum.ico"
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# === SAĞA HİZALANMIŞ BUTONLAR ===
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.place(relx=0.75, rely=0.2)  # Ekranın %75 sağına hizalanır

button_width = 30
tk.Button(button_frame, text="Bilgisayardan Yüz Ekle", width=button_width, bg="#d0e0f0", command=add_face_from_pc).pack(pady=10)
tk.Button(button_frame, text="Kameradan Yeni Yüz Ekle", width=button_width, bg="#d0e0f0", command=add_face_from_camera).pack(pady=10)
tk.Button(button_frame, text="Yoklama Al (Kamera)", width=button_width, bg="#d0e0f0", command=start_attendance).pack(pady=10)
tk.Button(button_frame, text="Yoklama Listesini Göster", width=button_width, bg="#d0e0f0", command=show_attendance_list).pack(pady=10)

# === BAŞLIK (Buton Grubunun Ortasına) ===
title_label = tk.Label(root, text="ANA KOMUT MENÜSÜ", font=("Helvetica", 14, "bold"), bg="#f0f0f0")
title_label.place(relx=0.87, rely=0.1, anchor="center")  # Buton grubunun ortasına hizalanır

# === SON GİRİŞ & ÇIKIŞLAR PANELİ ===
recent_frame = tk.Frame(root, bg="#f0f0f0")
recent_frame.place(x=10, y=10)  # Sol üst köşeye yaslı

# Görevli fonksiyonlar (tanımlandığını varsayarak)
show_recent_attendance(recent_frame)
periodic_refresh()
root.mainloop()