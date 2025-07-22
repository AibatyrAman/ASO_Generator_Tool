import flet as ft
from flet import Colors, Icons, FontWeight, TextAlign, ThemeMode, ScrollMode, KeyboardType
import os
import pandas as pd
import json
import re
import itertools
from collections import Counter
import logging
import asyncio
from typing import Optional, List, Dict, Any

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

class color():
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

# Mevcut Df_Get sınıfını aynı şekilde kopyalayıp paste ediyorum
class Df_Get():
    def merged_noduplicate_df(klasor_yolu):
        """
        Klasördeki tüm .csv dosyalarını birleştirir,
        tekrarlı satırları silmez, tüm verileri korur.
        CSV dosya adlarından kategori bilgisini çıkarır.
        """
        print("DEBUG: merged_noduplicate_df() başlatıldı. Klasör:", klasor_yolu)
        try:
            csv_dosyalar = [f for f in os.listdir(klasor_yolu) if f.endswith('.csv')]
            print("DEBUG: Bulunan CSV dosyaları:", csv_dosyalar)
            if not csv_dosyalar:
                raise ValueError("Klasörde hiç .csv dosyası bulunamadı!")
            
            dataframes = []
            for dosya in csv_dosyalar:
                df_temp = pd.read_csv(os.path.join(klasor_yolu, dosya))
                
                # CSV dosya adından kategori bilgisini çıkar
                # Örnek: "trending-keywords-US-Health & Fitness.csv" -> "Health & Fitness"
                kategori = dosya.replace('.csv', '').replace('trending-keywords-', '')
                if '-' in kategori:
                    # US-Health & Fitness -> Health & Fitness
                    kategori = kategori.split('-', 1)[1] if kategori.count('-') > 0 else kategori
                
                # Kategori sütunu ekle
                df_temp['Category'] = kategori
                
                print(f"DEBUG: {dosya} okundu, şekli: {df_temp.shape}, kategori: {kategori}")
                dataframes.append(df_temp)

            # Bütün CSV'ler birleştiriliyor - tekrarlar silinmiyor
            birlesik_df = pd.concat(dataframes, ignore_index=True)
            
            print("DEBUG: Birleştirilmiş DataFrame şekli:", birlesik_df.shape)
            return birlesik_df

        except Exception as e:
            raise ValueError(f"CSV birleştirme hatası: {e}")
        
    def kvd_df(df,limit):
        # Difficulty filtresini düzgün uygula
        filtered_df = df[(df["Volume"] >= 20) & (df["Difficulty"] <= limit)].copy()
        
        # Volume sütununu numeric'e çevir
        filtered_df.loc[:, "Volume"] = pd.to_numeric(filtered_df["Volume"], errors="coerce")
        filtered_df = filtered_df.dropna(subset=["Volume"])  
        filtered_df["Volume"] = filtered_df["Volume"].astype(int)
        
        # Volume'a göre sırala
        filtered_df.sort_values(by="Volume", ascending=False, inplace=True)
        
        # Tüm sütunları koru, sadece NaN değerleri temizle
        filtered_df = filtered_df.dropna(subset=["Keyword", "Volume", "Difficulty"])
        
        print("DEBUG: Filtrelenmiş ve sıralanmış KVD CSV:\n", filtered_df)
        return filtered_df

    def kelime_frekans_df(df):
        print("DEBUG: kelime_frekans_df() başlatıldı.")
        kelimeler = " ".join(df["Keyword"].astype(str)).split()
        print("DEBUG: Birleştirilmiş kelimeler:", kelimeler)
        kelime_sayaci = Counter(kelimeler)
        df_kf = pd.DataFrame(kelime_sayaci.items(), columns=["Kelime", "Frekans"]).sort_values(by="Frekans", ascending=False)
        print("DEBUG: Frekans DataFrame'i:\n", df_kf)
        return df_kf

    def without_branded_kf_df_get(df_kf):
        """
        Yasaklı kelimeleri DataFrame'den filtreler.
        """
        try:
            yasakli_kelimeler = [
                "free", "new", "best", "top", "iphone", "ipad", "android", "google", "store", 
                "download", "downloads", "for", "apple", "with", "yours", "a", "about", "above", "after", "again", "against", "all", 
                "am", "an", "and", "any", "app", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", 
                "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
                "doing", "don't", "down", "during", "each", "few", "from", "further", "had", "hadn't", "has", "hasn't", "have", 
                "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", 
                "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", 
                "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", 
                "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", 
                "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", 
                "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", 
                "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", 
                "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", 
                "whom", "why", "why's", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", 
                "yourself", "yourselves"]
            
            # Kelime filtresi oluştur ve mask ile filtreleme yap
            mask = ~(df_kf['Kelime'].str.lower().isin(yasakli_kelimeler))
            
            # Filtrelenmiş DataFrame'i oluştur
            filtered_df = df_kf[mask].copy()
            
            print(f"DEBUG: Filtrelenmiş kelime sayısı: {len(filtered_df)}")
            return filtered_df
            
        except Exception as e:
            print(f"HATA: {str(e)}")
            return pd.DataFrame(columns=['Kelime', 'Frekans'])

    def aggregate_frequencies(df):
        """
        Aynı kelimeleri birleştirerek frekans değerlerini toplar.
        """
        try:
            if df is None or df.empty:
                print("\033[31mHATA: Boş veya geçersiz DataFrame\033[0m")
                return pd.DataFrame(columns=['Kelime', 'Frekans'])

            aggregated_df = df.groupby("Kelime", as_index=False)["Frekans"].sum()
            print("\033[32mDEBUG: Frekanslar birleştirildi.\033[0m")
            return aggregated_df
        
        except Exception as e:
            print(f"\033[31mHATA: Genel hata: {str(e)}\033[0m")
            return pd.DataFrame(columns=['Kelime', 'Frekans'])
        
    def without_suffixes_df_get(kf_df):
        """
        Kelimeleri olduğu gibi döndürür (API kullanmadan).
        """
        try:
            if kf_df is None or kf_df.empty:
                print("\033[31mHATA: Boş veya geçersiz DataFrame\033[0m")
                return pd.DataFrame(columns=['Kelime', 'Frekans'])
            
            print(f"\033[32mDEBUG: Kelimeler olduğu gibi döndürülüyor: {len(kf_df)}\033[0m")
            return kf_df.copy()

        except Exception as e:
            print(f"\033[31mHATA: Genel hata: {str(e)}\033[0m")
            return pd.DataFrame(columns=['Kelime', 'Frekans'])

    def gpt_Title_Subtitle_df_get(df, app_name, selected_country):
        print(f"DEBUG: gpt_Title_Subtitle_df() başlatıldı.")
        print(f"{color.YELLOW}gpt_Title_Subtitle_df_get için kullanılan df:\n{df}{color.RESET}")
        df_sorted = df.sort_values(by='Frekans', ascending=False)
        top_keywords = df_sorted['Kelime'].tolist()[:10]  # İlk 10 kelimeyi al
        print("DEBUG: En sık kullanılan kelimeler:", top_keywords)
        
        # Basit title ve subtitle oluştur
        titles = []
        subtitles = []
        
        for i in range(5):
            if i < len(top_keywords):
                title = f"{app_name} {top_keywords[i]}"
                subtitle = f"{top_keywords[i+1] if i+1 < len(top_keywords) else top_keywords[0]} App"
                
                # Uzunluk kontrolü
                if len(title) > 30:
                    title = title[:27] + "..."
                if len(subtitle) > 30:
                    subtitle = subtitle[:27] + "..."
                    
                titles.append(title)
                subtitles.append(subtitle)
            else:
                titles.append(f"{app_name} App")
                subtitles.append("Best App Store")
        
        # DataFrame oluştur
        title_stitle_df = pd.DataFrame({
            "Title": titles,
            "Subtitle": subtitles
        })
        
        # Ek bilgiler ekle
        title_stitle_df["Keywords"] = [",".join(top_keywords)] * 5
        title_stitle_df["Keywords_Lenght"] = [len(",".join(top_keywords))] * 5
        title_stitle_df["Title_Lenght"] = [len(title) for title in titles]
        title_stitle_df["Subtitle_Lenght"] = [len(subtitle) for subtitle in subtitles]
        
        print("DEBUG: Oluşturulan DataFrame:\n", title_stitle_df)
        return title_stitle_df
        
    def find_matching_keywords(title_subtitle_df, merged_df):
        print(f"\033[34mDEBUG: find_matching_keywords() başladı.\033[0m")
        results = []
        matched_keywords_result = []

        for gpt_idx, gpt_row in title_subtitle_df.iterrows():
            title_words = set(str(gpt_row['Title']).lower().split()) if pd.notna(gpt_row['Title']) else set()
            subtitle_words = set(str(gpt_row['Subtitle']).lower().split()) if pd.notna(gpt_row['Subtitle']) else set()
            additional_words = set(str(gpt_row['Keywords']).lower().split(',')) if 'Keywords' in gpt_row and pd.notna(gpt_row['Keywords']) else set()

            combined_words = title_words.union(subtitle_words).union(additional_words)
            print(f"\033[35mDEBUG: İşlenen Title_Subtitle satırı {gpt_idx}, Kelimeler: {combined_words}\033[0m")

            matched_keywords = []
            total_volume = 0
            total_difficulty = 0
            ort_volume = 0
            ort_difficulty = 0
            counter = 0

            for _, merged_row in merged_df.iterrows():
                keyword_value = merged_row.get('Keyword')

                if pd.isna(keyword_value) or not isinstance(keyword_value, str):
                    continue
                
                keyword_words = set(keyword_value.lower().split())

                if keyword_words.issubset(combined_words):
                    matched_keywords.append(keyword_value)
                    total_volume += merged_row['Volume']
                    total_difficulty += merged_row['Difficulty']
                    counter += 1
                    ort_difficulty = round(total_difficulty / counter, 3)
                    ort_volume = round(total_volume / counter, 3)
                    matched_keywords_result.append({
                        'Matched Keywords': merged_row['Keyword'],
                        'Volume': merged_row['Volume'],
                        'Difficulty': merged_row['Difficulty']
                    })

                    print(f"\033[32mDEBUG: Eşleşme! '{keyword_value}' (Vol: {merged_row['Volume']}, Diff: {merged_row['Difficulty']})\033[0m")
            
            results.append({
                'Title': gpt_row['Title'],
                'Subtitle': gpt_row['Subtitle'],
                'Keywords': gpt_row['Keywords'],
                'Title Lenght': gpt_row['Title_Lenght'],
                'Subtitle Lenght': gpt_row['Subtitle_Lenght'],
                'Keywords Lenght': gpt_row['Keywords_Lenght'],
                'Total Volume': total_volume,
                'Total Difficulty': total_difficulty,
                'Avarage Volume': ort_volume,
                'Avarage Difficulty': ort_difficulty,
                'Renklenen Keywords Sayısı': counter
            })

        print(f"\033[34mDEBUG: find_matching_keywords() tamamlandı.\033[0m")
        return pd.DataFrame(results), pd.DataFrame(matched_keywords_result)

# Flet ASO App
class ASOApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "ASO Generate Tool - Professional Edition"
        self.page.theme_mode = ThemeMode.LIGHT
        self.page.window_width = 1600
        self.page.window_height = 900
        self.page.window_min_width = 800  # Daha küçük cihazlar için
        self.page.window_min_height = 600  # Daha küçük cihazlar için
        self.page.window_resizable = True
        self.page.window_maximizable = True
        self.page.padding = 20
        
        # Veri storage
        self.folder_path = ""
        self.difficulty_limit = 20
        self.selected_category = "Tümü"
        self.app_name = ""

        
        # DataFrame'ler
        self.merged_noduplicate_df = None
        self.kvd_df = None
        self.kelime_frekans_df = None
        self.without_branded_df = None
        self.without_suffixes_df = None
        self.gpt_title_subtitle_df = None
        self.matching_keywords_df_ts = None
        self.matching_keywords_df = None
        self.current_table = None
        self.current_display_df = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Ana container
        main_container = ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(Icons.ANALYTICS, size=30, color=Colors.BLUE_700),
                        ft.Text(
                            "ASO Generate Tool",
                            size=28,
                            weight=FontWeight.BOLD,
                            color=Colors.BLUE_700
                        ),
                        ft.Text(
                            "Professional Edition",
                            size=16,
                            color=Colors.GREY_600,
                            style=ft.TextThemeStyle.BODY_MEDIUM
                        )
                    ]),
                    bgcolor=Colors.BLUE_50,
                    padding=20,
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Main content - Responsive Layout
                ft.Container(
                    content=ft.Row([
                        # Left Panel - Controls (30% genişlik)
                        ft.Container(
                            content=self.create_left_panel(),
                            bgcolor=Colors.WHITE,
                            border_radius=10,
                            padding=20,
                            expand=3,  # 30% ekran genişliği
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=10,
                                color=Colors.with_opacity(0.1, Colors.GREY_400)
                            )
                        ),
                        
                        # Spacing
                        ft.Container(width=20),
                        
                        # Right Panel - Table (70% genişlik)
                        ft.Container(
                            content=self.create_right_panel(),
                            bgcolor=Colors.WHITE,
                            border_radius=10,
                            padding=20,
                            expand=7,  # 70% ekran genişliği
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=10,
                                color=Colors.with_opacity(0.1, Colors.GREY_400)
                            )
                        )
                    ], 
                    alignment=ft.MainAxisAlignment.START,
                    expand=True)
                )
            ], expand=True),
            expand=True
        )
        
        self.page.add(main_container)
        
    def create_left_panel(self):
        # File picker
        self.folder_picker = ft.FilePicker(on_result=self.on_folder_selected)
        self.page.overlay.append(self.folder_picker)
        
        # Folder selection area - Responsive
        self.folder_display = ft.Container(
            content=ft.Column([
                ft.Icon(Icons.FOLDER_OPEN, size=40, color=Colors.BLUE_400),
                ft.Text(
                    "CSV Klasörü Seç",
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    color=Colors.BLUE_600
                ),
                ft.Text(
                    "Klasör seçmek için tıklayın",
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                    color=Colors.GREY_600
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            height=120,
            bgcolor=Colors.BLUE_50,
            border=ft.border.all(2, Colors.BLUE_200),
            border_radius=10,
            padding=20,
            alignment=ft.alignment.center,
            expand=True,  # Responsive genişlik
            on_click=lambda _: self.folder_picker.get_directory_path()
        )
        

        
        # Filtre bölgesi
        filter_title = ft.Text(
            "🔍 Filtre Ayarları",
            size=16,
            weight=FontWeight.BOLD,
            color=Colors.BLUE_700
        )
        
        # Difficulty filter
        self.difficulty_filter_input = ft.TextField(
            label="Difficulty Sınırı",
            value="20",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self.on_difficulty_filter_changed,
            expand=True
        )
        
        # Category filter dropdown
        self.category_dropdown = ft.Dropdown(
            label="Kategori Filtresi",
            value="Tümü",
            options=[ft.dropdown.Option("Tümü")],
            on_change=self.on_category_changed,
            expand=True
        )
        
        # Apply filters button
        self.apply_filters_button = ft.ElevatedButton(
            "🔍 Filtreleri Uygula",
            on_click=self.apply_filters,
            style=ft.ButtonStyle(
                color=Colors.WHITE,
                bgcolor=Colors.GREEN_600,
                elevation=2,
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            height=45,
            expand=True
        )
        
        # Buttons
        button_style = ft.ButtonStyle(
            color=Colors.WHITE,
            bgcolor=Colors.BLUE_600,
            elevation=2,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
        
        # Responsive Buttons
        buttons = [
            ft.ElevatedButton(
                "Birleştirilmiş Ana Tablo",
                on_click=self.show_merged_table,
                style=button_style,
                height=45,
                expand=True  # Responsive genişlik
            ),
            ft.ElevatedButton(
                "Keyword Volume Difficulty",
                on_click=self.show_kvd_table,
                style=button_style,
                height=45,
                expand=True  # Responsive genişlik
            ),
            ft.ElevatedButton(
                "Kelime Frekansı",
                on_click=self.show_frequency_table,
                style=button_style,
                height=45,
                expand=True  # Responsive genişlik
            ),
            ft.ElevatedButton(
                "Branded Kelimeler Filtrelenmiş",
                on_click=self.show_branded_filtered_table,
                style=button_style,
                height=45,
                expand=True  # Responsive genişlik
            ),
            ft.ElevatedButton(
                "Eklerden Ayrılmış Kelimeler",
                on_click=self.show_suffixes_removed_table,
                style=button_style,
                height=45,
                expand=True  # Responsive genişlik
            ),
            ft.ElevatedButton(
                "Title Subtitle Analiz",
                on_click=self.show_title_subtitle_table,
                style=button_style,
                height=45,
                expand=True  # Responsive genişlik
            )
        ]
        
        return ft.Column([
            self.folder_display,
            ft.Divider(height=20),
            ft.ElevatedButton(
                "Yükle",
                on_click=self.load_data,
                style=ft.ButtonStyle(
                    color=Colors.WHITE,
                    bgcolor=Colors.GREEN_600,
                    elevation=2,
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                height=45,
                expand=True  # Responsive genişlik
            ),
            ft.Divider(height=20),
            # Filtre bölgesi için scroll container
                            ft.Container(
                content=ft.Column([
                    filter_title,
                    ft.Divider(height=10),
                    ft.Row([
                        self.difficulty_filter_input,
                        ft.Container(width=10),
                        self.category_dropdown
                    ]),
                    ft.Divider(height=10),
                    self.apply_filters_button,
                    ft.Container(height=10)  # Bottom padding
                ], spacing=5, scroll=ScrollMode.ALWAYS),
                height=150,  # Sabit yükseklik
                border=ft.border.all(1, Colors.BLUE_200),
                border_radius=8,
                padding=10,
                bgcolor=Colors.BLUE_50
            ),
            ft.Divider(height=20),
            # Butonlar için ayrı scroll container
            ft.Container(
                content=ft.Column([
                    *buttons,
                    ft.Container(height=20)  # Bottom padding
                ], spacing=10, scroll=ScrollMode.ALWAYS),  # Scroll aktif
                height=300,  # Sabit yükseklik
                border=ft.border.all(1, Colors.GREY_200),
                border_radius=8,
                padding=10,
                bgcolor=Colors.GREY_50
            )
        ], spacing=10, expand=True)
    
    def create_right_panel(self):
        # Table title
        self.table_title = ft.Text(
            "Tablo",
            size=20,
            weight=FontWeight.BOLD,
            color=Colors.BLUE_700
        )
        
        # Data table - Responsive
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tablo", weight=FontWeight.BOLD))
            ],
            rows=[
                ft.DataRow(cells=[ft.DataCell(ft.Text("Veri yüklendikten sonra tablolar burada görünecek"))])
            ],
            border=ft.border.all(1, Colors.GREY_300),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, Colors.GREY_300),
            heading_row_color=Colors.BLUE_50,
            heading_row_height=50,
            column_spacing=20,
            show_checkbox_column=False,
            divider_thickness=1
        )
        
        # Table container - Responsive with horizontal and vertical scrolling
        table_container = ft.Container(
            content=ft.Column([
                self.data_table
            ], scroll=ScrollMode.AUTO),
            height=500,
            border=ft.border.all(1, Colors.GREY_300),
            border_radius=10,
            padding=10,
            expand=True  # Responsive genişlik
        )
        
        # Export button - Responsive
        self.export_button = ft.ElevatedButton(
            "Tabloyu Dışa Aktar",
            on_click=self.export_table,
            style=ft.ButtonStyle(
                color=Colors.WHITE,
                bgcolor=Colors.ORANGE_600,
                elevation=2,
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            height=45
            # width kaldırıldı - responsive olacak
        )
        
        return ft.Column([
            self.table_title,
            ft.Divider(height=20),
            table_container,
            ft.Divider(height=20),
            ft.Row([
                self.export_button
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=10, expand=True)
    
    # Event handlers
    def on_folder_selected(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.folder_path = e.path
            self.folder_display.content = ft.Column([
                ft.Icon(Icons.FOLDER, size=40, color=Colors.GREEN_600),
                ft.Text(
                    "Klasör Seçildi",
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    color=Colors.GREEN_600
                ),
                ft.Text(
                    os.path.basename(e.path),
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                    color=Colors.GREY_600
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
            self.folder_display.bgcolor = Colors.GREEN_50
            self.folder_display.border = ft.border.all(2, Colors.GREEN_200)
            self.page.update()
    

    
    def on_difficulty_filter_changed(self, e):
        try:
            self.difficulty_limit = float(e.control.value)
        except ValueError:
            self.difficulty_limit = 20
    
    def on_category_changed(self, e):
        self.selected_category = e.control.value
    
    def apply_filters(self, e):
        """Filtreleri uygular ve mevcut tabloyu günceller"""
        if self.merged_noduplicate_df is None:
            self.show_warning("Önce verileri yükleyin!")
            return
        
        try:
            # Filtrelenmiş DataFrame oluştur
            filtered_df = self.merged_noduplicate_df.copy()
            
            # Difficulty filtresi
            if self.difficulty_limit > 0:
                filtered_df = filtered_df[filtered_df['Difficulty'] <= self.difficulty_limit]
            
            # Kategori filtresi
            if self.selected_category != "Tümü":
                filtered_df = filtered_df[filtered_df['Category'] == self.selected_category]
            
            # Filtrelenmiş veriyi göster
            if filtered_df.empty:
                self.show_warning("Filtre kriterlerine uygun veri bulunamadı!")
                return
            
            self.display_dataframe(filtered_df, f"Filtrelenmiş Tablo ({len(filtered_df)} kayıt)")
            self.current_table = filtered_df
            
            self.show_success(f"Filtreler uygulandı! {len(filtered_df)} kayıt gösteriliyor.")
            
        except Exception as ex:
            self.show_error(f"Filtre uygulama hatası: {str(ex)}")
    
    def load_data(self, e):
        if not self.folder_path:
            self.show_error("Lütfen önce bir klasör seçin!")
            return
        
        try:
            # Show loading
            self.show_loading("Veriler yükleniyor...")
            
            # Load data
            self.merged_noduplicate_df = Df_Get.merged_noduplicate_df(self.folder_path)
            self.kvd_df = Df_Get.kvd_df(self.merged_noduplicate_df, self.difficulty_limit)
            self.kelime_frekans_df = Df_Get.kelime_frekans_df(self.kvd_df)
            self.without_branded_df = Df_Get.without_branded_kf_df_get(self.kelime_frekans_df)
            
            # Kategori dropdown'unu güncelle
            self.update_category_dropdown()
            
            self.hide_loading()
            self.show_success("Veriler başarıyla yüklendi!")
            
        except Exception as ex:
            self.hide_loading()
            self.show_error(f"Veri yükleme hatası: {str(ex)}")
    
    def update_category_dropdown(self):
        """Kategori dropdown'unu mevcut kategorilerle günceller"""
        if self.merged_noduplicate_df is not None and 'Category' in self.merged_noduplicate_df.columns:
            categories = ['Tümü'] + sorted(self.merged_noduplicate_df['Category'].unique().tolist())
            self.category_dropdown.options = [ft.dropdown.Option(cat) for cat in categories]
            self.category_dropdown.value = "Tümü"
            self.page.update()
    
    def show_merged_table(self, e):
        if self.merged_noduplicate_df is None:
            self.show_warning("Önce verileri yükleyin!")
            return
        
        self.display_dataframe(self.merged_noduplicate_df, "Birleştirilmiş Ana Tablo")
        self.current_table = self.merged_noduplicate_df
    
    def show_kvd_table(self, e):
        if self.kvd_df is None:
            self.show_warning("Önce verileri yükleyin!")
            return
        
        self.display_dataframe(self.kvd_df, "Keyword Volume Difficulty Tablosu")
        self.current_table = self.kvd_df
    
    def show_frequency_table(self, e):
        if self.kelime_frekans_df is None:
            self.show_warning("Önce verileri yükleyin!")
            return
        
        self.display_dataframe(self.kelime_frekans_df, "Kelime Frekans Tablosu")
        self.current_table = self.kelime_frekans_df
    
    def show_branded_filtered_table(self, e):
        if self.without_branded_df is None:
            self.show_warning("Önce verileri yükleyin!")
            return
        
        self.display_dataframe(self.without_branded_df, "Branded Kelimeler Filtrelenmiş Tablo")
        self.current_table = self.without_branded_df
    
    def show_suffixes_removed_table(self, e):
        if self.merged_noduplicate_df is None:
            self.show_warning("Önce verileri yükleyin!")
            return
        
        try:
            self.show_loading("Ekler kaldırılıyor...")
            self.without_suffixes_df = Df_Get.without_suffixes_df_get(
                self.without_branded_df
            )
            self.hide_loading()
            
            self.display_dataframe(self.without_suffixes_df, "Eklerden Ayrılmış Kelimeler")
            self.current_table = self.without_suffixes_df
            
        except Exception as ex:
            self.hide_loading()
            self.show_error(f"Ek kaldırma hatası: {str(ex)}")
    
    def show_title_subtitle_table(self, e):
        if self.without_suffixes_df is None:
            self.show_warning("Önce eklerden ayrılmış kelime tablosunu oluşturun!")
            return
        
        try:
            self.show_loading("Title ve Subtitle oluşturuluyor...")
            
            self.gpt_title_subtitle_df = Df_Get.gpt_Title_Subtitle_df_get(
                self.without_suffixes_df, "App Name", "United States"
            )
            
            if self.gpt_title_subtitle_df.empty:
                self.difficulty_limit += 10
                self.page.update()
                self.load_data(None)
                return self.show_title_subtitle_table(e)
            
            self.matching_keywords_df_ts, self.matching_keywords_df = Df_Get.find_matching_keywords(
                self.gpt_title_subtitle_df, self.merged_noduplicate_df
            )
            
            self.hide_loading()
            self.display_dataframe(self.matching_keywords_df_ts, "Title Subtitle Analiz Tablosu")
            self.current_table = self.matching_keywords_df_ts
            
        except Exception as ex:
            self.hide_loading()
            self.show_error(f"Title/Subtitle oluşturma hatası: {str(ex)}")
    
    def display_dataframe(self, df: pd.DataFrame, title: str):
        if df is None or df.empty:
            self.show_warning("Tablo boş!")
            return
        
        # Update table title
        self.table_title.value = title
        
        # Store current dataframe for sorting
        self.current_display_df = df.copy()
        
        # Clear existing data
        self.data_table.columns.clear()
        self.data_table.rows.clear()
        
        # Add columns with clickable headers
        for col in df.columns:
            self.data_table.columns.append(
                ft.DataColumn(
                    ft.Text(
                        str(col),
                        size=12,
                        weight=FontWeight.BOLD,
                        color=Colors.BLUE_700
                    ),
                    on_tap=lambda e, col=col: self.sort_table_by_column(col)
                )
            )
        
        # Add rows (limit to first 100 rows for performance)
        self.add_table_rows(df.head(100))
        
        self.page.update()
    
    def add_table_rows(self, df):
        """Tabloya satırları ekler"""
        self.data_table.rows.clear()
        for idx, row in df.iterrows():
            cells = []
            for value in row:
                cells.append(
                    ft.DataCell(
                        ft.Text(
                            str(value),
                            size=11,
                            color=Colors.BLACK87
                        )
                    )
                )
            self.data_table.rows.append(ft.DataRow(cells=cells))
    
    def sort_table_by_column(self, column_name):
        """Tabloyu belirtilen sütuna göre sıralar"""
        if self.current_display_df is None:
            return
        
        try:
            # Mevcut sıralama durumunu kontrol et
            if hasattr(self, 'current_sort_column') and self.current_sort_column == column_name:
                # Aynı sütuna tekrar tıklandıysa sıralama yönünü değiştir
                self.current_sort_ascending = not getattr(self, 'current_sort_ascending', True)
            else:
                # Yeni sütun seçildiyse artan sıralama yap
                self.current_sort_ascending = True
            
            self.current_sort_column = column_name
            
            # Sıralama yap
            sorted_df = self.current_display_df.sort_values(
                by=column_name, 
                ascending=self.current_sort_ascending,
                na_position='last'
            )
            
            # Tabloyu güncelle
            self.add_table_rows(sorted_df.head(100))
            
            # Sıralama yönünü göster
            direction = "↑" if self.current_sort_ascending else "↓"
            self.show_success(f"Tablo '{column_name}' sütununa göre sıralandı {direction}")
            
            self.page.update()
            
        except Exception as e:
            self.show_error(f"Sıralama hatası: {str(e)}")
    
    def export_table(self, e):
        if self.current_table is None:
            self.show_warning("Dışa aktarılacak tablo yok!")
            return
        
        try:
            # For now, save to desktop with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"aso_table_{timestamp}.csv"
            filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
            
            self.current_table.to_csv(filepath, index=False)
            self.show_success(f"Tablo dışa aktarıldı: {filepath}")
            
        except Exception as ex:
            self.show_error(f"Dışa aktarma hatası: {str(ex)}")
    
    # Utility methods
    def show_loading(self, message: str):
        self.page.splash = ft.ProgressBar()
        self.page.update()
    
    def hide_loading(self):
        self.page.splash = None
        self.page.update()
    
    def show_error(self, message: str):
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color=Colors.WHITE),
                bgcolor=Colors.RED_600
            )
        )
    
    def show_warning(self, message: str):
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color=Colors.WHITE),
                bgcolor=Colors.ORANGE_600
            )
        )
    
    def show_success(self, message: str):
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color=Colors.WHITE),
                bgcolor=Colors.GREEN_600
            )
        )

def main(page: ft.Page):
    ASOApp(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP) 
