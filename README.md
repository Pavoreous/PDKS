![face_recognition](https://github.com/user-attachments/assets/e5f04531-3892-4e9c-b713-92bf5cbc5d3d)
![Gui](https://github.com/user-attachments/assets/ad3fa915-cf32-4af6-a513-7aecc0ac4682)
--TÜRKÇE---
Gereklilikler
Bilgisayarınıza uygun Cmake kurulumunu yapın. https://cmake.org/download/  
Python 3.9.x sürümlerinde denenmiştir çalışıyor.
Python ortamı için gerekli paketler
  pip install cmake
  pip install dlib==19.24.0
  pip install face_recognition==1.3.0
  pip install opencv-python==4.7.0.72
  pip install numpy
  pip install pillow
Bütün kurulum işlemleri tamamlandıysa main.py yi derleyip çalıştırın.
Known_Face klasörüne eklenen resimler ile kamera görüntülerini karşılaştırıp yoklama.csv dosyasına tarih, saat ve giriş olarak kayıt eder.
start_attendance_function.txt dosyasında 2 fonksiyon vardır. Kafanızın etrafında kutu görmek istiyorsanız Green_face_recognition fonksiyonunu start_attendance fonksiyonu ile değiştirin.
-------------------------------------------------------------------------------
--English--
Requirements
Install the appropriate Cmake installation on your computer. https://cmake.org/download/ 
Tested on Python 3.9.x versions works.
Required packages for Python environment
 pip install cmake
 pip install dlib==19.24.0
 pip install face_recognition==1.3.0
 pip install opencv-python==4.7.0.72
 pip install numpy
 pip install pillow
If all installation processes are completed, compile and run main.py.
It compares the camera images with the images added to the Known_Face folder and saves them in the attendance.csv file as date, time and entry.
start_attendance_function.txt has 2 functions. If you want to see a box around your head, replace the Green_face_recognition function with the start_attendance function.
