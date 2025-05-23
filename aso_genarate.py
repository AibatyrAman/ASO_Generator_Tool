import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import pandas as pd
import openai
import json
import re
import itertools
from collections import Counter

open_ai_key = "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"
class color():
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"
class Df_Get():
    def merged_noduplicate_df(klasor_yolu):
        """
        Klasördeki tüm .csv dosyalarını birleştirir,
        Keyword, Volume ve Difficulty sütunlarına göre tekrarlı satırları kaldırır,
        tüm sütunları saklayarak bir DataFrame döndürür.
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
                print(f"DEBUG: {dosya} okundu, şekli: {df_temp.shape}")
                dataframes.append(df_temp)

            # Bütün CSV'ler birleştiriliyor
            birlesik_df = pd.concat(dataframes, ignore_index=True)
            
            # Öncelikle, Difficulty sütununa göre azalan sırayla sıralıyoruz
            birlesik_df.sort_values(by="Difficulty", ascending=False, inplace=True)

            # Sadece Keyword sütunundaki tekrarları kaldırıp,
            # en yüksek Difficulty değerine sahip satırı tutuyoruz
            birlesik_df.drop_duplicates(subset=["Keyword"], keep="first", ignore_index=True, inplace=True)

            print("DEBUG: Birleştirilmiş DataFrame şekli:", birlesik_df.shape)
            return birlesik_df

        except Exception as e:
            raise ValueError(f"CSV birleştirme hatası: {e}")
        
    def kvd_df(df,limit):
        df = df[(df["Volume"] >= 20) & (df["Difficulty"] <= limit)]
        df.loc[:, "Volume"] = pd.to_numeric(df["Volume"], errors="coerce")
        df = df.dropna(subset=["Volume"])  
        df["Volume"] = df["Volume"].astype(int)
        df.sort_values(by="Volume", ascending=False, inplace=True)
        df = df[["Keyword", "Volume", "Difficulty"]].dropna()
        print("DEBUG: Filtrelenmiş ve sıralanmış KVD CSV:\n", df)
        return df
        


    def kelime_frekans_df(df, openai_api_key):
        print("DEBUG: kelime_frekans_df() başlatıldı.")
        openai.api_key = openai_api_key  # Global openai kullanılacak
        kelimeler = " ".join(df["Keyword"].astype(str)).split()
        print("DEBUG: Birleştirilmiş kelimeler:", kelimeler)
        kelime_sayaci = Counter(kelimeler)
        df_kf = pd.DataFrame(kelime_sayaci.items(), columns=["Kelime", "Frekans"]).sort_values(by="Frekans", ascending=False)
        print("DEBUG: Frekans DataFrame'i:\n", df_kf)
        return df_kf


    def without_branded_kf_df_get(df_kf, openai_api_key):
        """
        Branded kelimeleri ve yasaklı kelimeleri DataFrame'den filtreler.
        
        Args:
            df_kf (pd.DataFrame): Kelime ve Frekans sütunları olan DataFrame
            openai_api_key (str): OpenAI API anahtarı
        
        Returns:
            pd.DataFrame: Filtrelenmiş DataFrame
        """
        try:
            word_list = df_kf['Kelime'].tolist()
            
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
            
            openai.api_key = openai_api_key
            
            system_prompt = """
You are an expert in identifying branded words and proper nouns. Your task is to determine if the given words are branded words or proper nouns (like "Williams", "Sherwin", etc.).
You need to identify and return only the words that are branded or proper nouns from the provided list.

Here is the task in detail:
1. Review the following list of words.
2. Identify the branded words and proper nouns.
3. Return the list of identified branded words and proper nouns in the following format:

Example:
- Input: ["Apple", "car", "Sherwin", "painting"]
- Output: ["Apple", "Sherwin"]

*Important*: 
- Only include the branded words and proper nouns in the returned list, and avoid any other words."""  # Mevcut system prompt
            user_prompt = f"""
            Here is the list of words:
            {word_list}

            Return the list of branded words and proper nouns in the following format:
            ["word1", "word2", "word3"]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=150
            )
            
            answer = response["choices"][0]["message"]["content"].strip()
            print(f'{color.RED}DEBUG:BRANDED API yanıtı:{color.RESET} {answer}')
            
            try:
                branded_data = json.loads(answer)
                print("DEBUG: JSON başarıyla ayrıştırıldı:", branded_data)  # JSON çıktısını kontrol et
                branded_words = [str(item).lower() for item in branded_data] if isinstance(branded_data, list) else []
            except json.JSONDecodeError:
                print("DEBUG: JSON ayrıştırma hatası, manuel işleme yapılıyor")
                cleaned = answer.replace("[", "").replace("]", "").replace('"', '').strip()
                branded_words = [w.strip().lower() for w in cleaned.split(",") if w.strip()]
                print("DEBUG: Manuel temizlenmiş veri:", branded_words)  # Manuel işlenen veriyi kontrol et

            
            # Kelime filtresi oluştur ve mask ile filtreleme yap
            mask = ~(df_kf['Kelime'].str.lower().isin(branded_words) | 
                    df_kf['Kelime'].str.lower().isin(yasakli_kelimeler))
            
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
        
        Args:
            df (pd.DataFrame): "Kelime" ve "Frekans" sütunları olan DataFrame.

        Returns:
            pd.DataFrame: Aynı kelimelerin frekanslarının toplandığı yeni DataFrame.
        """
        try:
            if df is None or df.empty:
                print("\033[31mHATA: Boş veya geçersiz DataFrame\033[0m")
                return pd.DataFrame(columns=['Kelime', 'Frekans'])

            # Frekansları aynı kelimeler için toplama
            aggregated_df = df.groupby("Kelime", as_index=False)["Frekans"].sum()
            
            print("\033[32mDEBUG: Frekanslar birleştirildi.\033[0m")
            return aggregated_df
        
        except Exception as e:
            print(f"\033[31mHATA: Genel hata: {str(e)}\033[0m")
            return pd.DataFrame(columns=['Kelime', 'Frekans'])
        
    def without_suffixes_df_get(kf_df, selected_country,openai_api_key):
        """
        Kelimelerin çoğul eklerini kaldırır ve tekil formlarını döndürür.

        Args:
            kf_df (pd.DataFrame): "Kelime" ve "Frekans" sütunları olan DataFrame.
            openai_api_key (str): OpenAI API anahtarı.

        Returns:
            pd.DataFrame: İşlenmiş DataFrame veya hata durumunda orijinal DataFrame.
        """
        try:
            if kf_df is None or kf_df.empty:
                print("\033[31mHATA: Boş veya geçersiz DataFrame\033[0m")
                return pd.DataFrame(columns=['Kelime', 'Frekans'])  # Boş DataFrame döndür
            
            keyword_list = kf_df['Kelime'].dropna().tolist()
            if not keyword_list:
                print("\033[33mUYARI: Kelime listesi boş\033[0m")
                return pd.DataFrame(columns=['Kelime', 'Frekans'])  # Boş DataFrame döndür

            openai.api_key = openai_api_key
            print(f"{color.CYAN}DEBUG: SUFFİXES COUNTRY:{selected_country}{color.RESET}")
            system_prompt = f"""
            You are an expert in language processing. Your task is:
1. Given a Python list of keywords in the language relevant to the market of {selected_country},
2. Remove only the plural suffixes from each word to return the singular/base form. For example, if the keywords are in English (as in the {selected_country} market when applicable), remove plural suffixes such as -s, -es, and -ies. If the keywords are in another language, apply the appropriate plural suffix removal rules according to the language conventions of {selected_country}.
3. If a word does not end with any of these plural suffixes, leave it unchanged.
4. Provide the final answer strictly as a Python list of strings.
Example:
- Input: ["cats", "boxes", "stories", "apple"]
- Output: ["cat", "box", "story", "apple"]

**WARNING**: Only remove plural suffixes. Do not remove any other suffix or modify the word in any other way.
"""

            user_prompt = f"""
            Here is the list of words:
            {keyword_list}

            Return the processed list in JSON list format. For example:
            ["word1","word2","word3"]
            """

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0,
                    request_timeout=60  # API gecikme hatalarına karşı önlem
                )

                answer = response["choices"][0]["message"]["content"].strip()
                print(f"\033[34mDEBUG: Suffixes API yanıtı: {answer}\033[0m")

                # Yanıtın başında ve sonunda üçlü tırnak içeren kod bloğu olup olmadığını kontrol et ve temizle
                if answer.startswith("```json") or answer.startswith("```python"):
                    answer = answer.split("```")[1]  # İlk üçlü tırnağı kaldır
                    answer = answer.replace("json", "").replace("python", "").strip()  # Gereksiz etiketleri kaldır
                    answer = answer.split("```")[0]  # Kapanış üçlü tırnağını kaldır

                try:
                    base_form_list = json.loads(answer)

                    if not isinstance(base_form_list, list) or not base_form_list:
                        raise ValueError("API yanıtı geçerli bir liste değil veya boş.")

                    # Liste uzunluğu ile orijinal kelime listesinin uzunluğu eşleşmiyorsa
                    if len(base_form_list) != len(keyword_list):
                        print(f"\033[33mUYARI: API yanıt uzunluğu ({len(base_form_list)}) keyword listesi uzunluğu ({len(keyword_list)}) ile eşleşmiyor. Orijinal liste kullanılacak.\033[0m")
                        base_form_list = keyword_list  # Orijinal listeyi kullan

                    # Frekans sütunundaki boş değerleri doldur
                    kf_df['Frekans'] = kf_df['Frekans'].fillna(0)

                    # Yeni DataFrame oluştur
                    result_df = pd.DataFrame({
                        'Kelime': base_form_list,
                        'Frekans': kf_df['Frekans']
                    })
                    result_df=Df_Get.aggregate_frequencies(result_df)
                    result_df = result_df.sort_values(by='Frekans', ascending=False)

                    print(f"\033[32mDEBUG: İşlenmiş kelime sayısı: {len(result_df)}\033[0m")
                    return pd.DataFrame(result_df)

                except json.JSONDecodeError as e:
                    print(f"\033[31mHATA: JSON ayrıştırma hatası: {str(e)}\033[0m")
                    return kf_df  # JSON hatası olursa orijinal DataFrame'i döndür

            except Exception as e:
                print(f"\033[31mHATA: API çağrısı veya işleme hatası: {str(e)}\033[0m")
                return kf_df  # API hatasında orijinal DataFrame'i döndür

        except Exception as e:
            print(f"\033[31mHATA: Genel hata: {str(e)}\033[0m")
            return pd.DataFrame(columns=['Kelime', 'Frekans'])  # Genel hata durumunda boş DataFrame döndür



    def gpt_Title_Subtitle_df_get(df, app_name,selected_country ,openai_api_key, retry_count=0, max_retries=3):
        print(f"DEBUG: gpt_Title_Subtitle_df() başlatıldı. retry_count={retry_count}")
        openai.api_key = openai_api_key
        print(f"{color.YELLOW}gpt_Title_Subtitle_df_get için kullanılan df:\n{df}{color.RESET}")
        df_sorted = df.sort_values(by='Frekans', ascending=False)
        top_keywords = df_sorted['Kelime'].tolist()
        print("DEBUG: En sık kullanılan kelimeler:", top_keywords)
        
        prompt_system = f'''
    You are an experienced ASO (App Store Optimization) expert. Your task is to generate optimized Title and Subtitle for an app based on the provided keyword data.
    I will provide you with a list of keywords sorted by frequency. Based on this information, your task is to generate the most optimized Title and Subtitle for an app's App Store page. Here are the detailed rules:
    You are an experienced ASO (App Store Optimization) expert. Your task is to generate optimized Title and Subtitle for an app based on the provided keyword data, taking into account the market characteristics of the selected country: **{selected_country}**.
I will provide you with a list of keywords sorted by frequency. Based on this information, your task is to generate the most optimized Title and Subtitle for an app's App Store page for the {selected_country} market. Here are the detailed rules:

    1. **Title**:
    - Must include the app name: **{app_name}**
    - The title must be no longer than **30 characters** and no shorter than **25 characters**.
    - Use the most frequent keywords first, prioritizing those at the beginning of the provided list.
    - Ensure that the titles are unique and not repetitive; each generated title should use a different combination of keywords.
    - **Do not include any of the following words like: "and", "or", "your", "my", "with", etc.**

    2. **Subtitle**:
    - It must not exceed **30 characters** and no shorter than **25 characters**.
    - Do not repeat any keywords used in the Title.
    - Use the most frequent keywords first, prioritizing those at the beginning of the provided list.
    - Ensure that the subtitles are unique and distinct from each other.
    - **Do not include any of the following words like: "and", "or", "your", "my", "with".**

    3. **Important**:
    - Focus on using keywords from the beginning of the provided list, where the frequency values are higher.
    - Make sure the Title and Subtitle align with these rules to maximize the app's visibility and effectiveness in the App Store.
    - **Do not include any of the following words like: "and", "or", "your", "my", "with".**
    - *Only generate 5 title and 5 subtitle*
    '''
        
        # User Prompt: sadece 1 set başlık ve alt başlık üretmesini istiyoruz
        prompt_user = f'''
    Here are the most frequent keywords:
    {','.join(top_keywords)}
    - **The title and subtitle must be no longer than 30 characters and no shorter than 25 characters.**
    - **Do not include any of the following words like: "and", "or", "your", "my", "with".**
    - *Only generate 5 title and 5 subtitle*
    **Provide the output strictly in the following JSON format:**
    json
    {{
    "data": [
        {{"Title": "Generated Title", "Subtitle": "Generated Subtitle"}},
        {{"Title": "Generated Title", "Subtitle": "Generated Subtitle"}},
        {{"Title": "Generated Title", "Subtitle": "Generated Subtitle"}},
        {{"Title": "Generated Title", "Subtitle": "Generated Subtitle"}},
        {{"Title": "Generated Title", "Subtitle": "Generated Subtitle"}}
    ]
    }}
    '''
        print('\033[31m\033[44mDEBUG: OpenAI isteği hazırlanıyor\033[0m')
        try:
            response = openai.ChatCompletion.create(
                model="chatgpt-4o-latest",
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": prompt_user}
                ],
                temperature=0.7,
                max_tokens=539,
            )
            text_output = response['choices'][0]['message']['content']
            def parse_openai_json(text_output):
                # 1) Üçlü tırnaklar arasını yakala
                match = re.search(r'```json\s*(\{.*?\})\s*```', text_output, re.DOTALL)
                
                if match:
                    json_text = match.group(1)
                    print("DEBUG: JSON formatı bulundu.")
                else:
                    # match yoksa, belki de ChatGPT "json" arasına almadı,
                    # o yüzden tamamını kullan
                    json_text = text_output
                    print("DEBUG: Tüm metin JSON olarak kullanılacak.")
                
                # 2) Temizleme adımları
                json_text = json_text.strip()
                # Çift tırnakları standart ASCII tırnak haline getirelim:
                json_text = json_text.replace("“", "\"").replace("”", "\"")
                # BOM karakteri vs. kaldırmak için encode-decode
                json_text = json_text.encode("utf-8", "ignore").decode("utf-8", "ignore")

                # 3) Parse et
                output_data = json.loads(json_text)
                return output_data

            try:
                parsed = parse_openai_json(text_output)
                print(parsed)
            except json.JSONDecodeError as e:
                print("JSON hatası yakalandı:", e)
                    # Sütun adlarını manuel belirliyoruz

            title_stitle_df = pd.DataFrame(parse_openai_json(text_output)["data"], columns=["Title", "Subtitle"])
            print("DEBUG: API yanıtından oluşturulan DataFrame:\n", title_stitle_df)

            # unused_keywords_list ve diğer listeleri başlatıyoruz
            unused_keywords_list = []  
            title_len_list = []
            subtitle_len_list = []
            toplam_keywords_lenght_list=[]

            # Her bir satır için işlemi başlatıyoruz
            for index, row in title_stitle_df.iterrows():
                # Title ve Subtitle'daki kelimeleri ayırıyoruz
                top_keywords_for_for = set()
                top_keywords_for_for = top_keywords
                title_words = set(row["Title"].split())  
                subtitle_words = set(row["Subtitle"].split())  

                title_len_list.append(len(row["Title"]))
                subtitle_len_list.append(len(row["Subtitle"]))

                # Title ve Subtitle'daki tüm kelimeleri birleştiriyoruz
                used_keywords = title_words.union(subtitle_words)
                used_keywords = set(item.lower() for item in used_keywords)
                print("\033[32mDEBUG: Used_Keyword Çıktısı: \033[0m", used_keywords)

                # unused_keywords listesini top_keywords'tan used_keywords'leri çıkararak oluşturuyoruz
                unused_keywords = [kw for kw in top_keywords_for_for if kw.lower() not in used_keywords]

                print("\033[33mUnused_Keyword:\033[0m", unused_keywords)

                # unused_keywords'i virgülle ayırarak birleştiriyoruz
                result_str = ""
                for keyword in unused_keywords:
                    candidate = keyword if result_str == "" else result_str + "," + keyword
                    try:
                        # candidate 100 karakterden uzun olmasın
                        if len(candidate) <= 100:
                            result_str = candidate
                        else:
                            toplam_keywords_lenght_list.append(len(result_str))
                            break  # 100 karakteri aşarsa, döngü sonlanır
                    except ValueError as e:
                        # Hata mesajında belirli bir ifadeyi kontrol edebilirsiniz
                        if "Length of values" in str(e) and "does not match length of index" in str(e):
                            print("DEBUG: unused_keywords_list uzunluğu DataFrame indeks uzunluğu ile uyuşmuyor!")
                            toplam_keywords_lenght_list.append(len(result_str))
                        else:
                            # Eğer hata farklıysa, hatayı yeniden fırlatıyoruz.
                            raise


                # unused_keywords_list'e her satır için sonuçları ekliyoruz
                print("\033[34mresult_str:\n\033[0m", result_str)
                unused_keywords_list.append(result_str)

            # unused_keywords_list'i df_output'a yeni bir sütun olarak ekliyoruz
            title_stitle_df["Keywords"] = unused_keywords_list
            title_stitle_df["Keywords_Lenght"]=toplam_keywords_lenght_list

            title_stitle_df["Title_Lenght"] = title_len_list
            title_stitle_df["Subtitle_Lenght"] = subtitle_len_list

            # Sonuçları yazdırıyoruz
            print("DEBUG: Son DataFrame (gpt_Title_Subtitle_df()):\n", title_stitle_df)
            
            return title_stitle_df

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print("DEBUG: gpt_Title_Subtitle_df() hatası:", e)
            return pd.DataFrame(columns=["Title", "Subtitle"])
        
    def find_matching_keywords(title_subtitle_df, merged_df):
        print(f"\033[34mDEBUG: find_matching_keywords() başladı.\033[0m")
        results = []
        matched_keywords_result=[]

        # Title_Subtitle tablosundaki HER SATIR için ayrı ayrı işlem yapacağız
        for gpt_idx, gpt_row in title_subtitle_df.iterrows():
            # 📌 Title, Subtitle, ve Keywords sütunundaki kelimeleri al (küçük harfe çevirerek)
            title_words = set(str(gpt_row['Title']).lower().split()) if pd.notna(gpt_row['Title']) else set()
            subtitle_words = set(str(gpt_row['Subtitle']).lower().split()) if pd.notna(gpt_row['Subtitle']) else set()
            additional_words = set(str(gpt_row['Keywords']).lower().split(',')) if 'Keywords' in gpt_row and pd.notna(gpt_row['Keywords']) else set()

            # 📌 Tüm kelimeleri birleştir
            combined_words = title_words.union(subtitle_words).union(additional_words)
            print(f"\033[35mDEBUG: İşlenen Title_Subtitle satırı {gpt_idx}, Kelimeler: {combined_words}\033[0m")

            matched_keywords = []
            total_volume = 0
            total_difficulty = 0
            ort_volume=0
            ort_difficulty=0
            counter=0

            # 📌 merged_df içindeki tüm satırları tek tek kontrol et
            for _, merged_row in merged_df.iterrows():
                keyword_value = merged_row.get('Keyword')

                if pd.isna(keyword_value) or not isinstance(keyword_value, str):
                    continue  # Geçerli bir string değilse atla
                
                # Keyword'ü kelimelere böl ve küçük harf yap
                keyword_words = set(keyword_value.lower().split())

                # Eğer tüm kelimeler combined_words içinde varsa, eşleşme bulduk
                if keyword_words.issubset(combined_words):
                    matched_keywords.append(keyword_value)
                    total_volume += merged_row['Volume']
                    total_difficulty += merged_row['Difficulty']
                    counter+=1
                    ort_difficulty=round(total_difficulty / counter, 3)
                    ort_volume=round(total_volume/counter,3)
                    matched_keywords_result.append({
                    'Matched Keywords': merged_row['Keyword'],
                    'Volume':merged_row['Volume'],
                    'Difficulty':merged_row['Difficulty']
                    })

                    print(f"\033[32mDEBUG: Eşleşme! '{keyword_value}' (Vol: {merged_row['Volume']}, Diff: {merged_row['Difficulty']})\033[0m")

            # 📌 Eğer eşleşme bulunduysa, tabloya ekle
            
            
            results.append({
                'Title': gpt_row['Title'],
                'Subtitle': gpt_row['Subtitle'],
                'Keywords': gpt_row['Keywords'],
                'Title Lenght':gpt_row['Title_Lenght'],
                'Subtitle Lenght':gpt_row['Subtitle_Lenght'],
                'Keywords Lenght':gpt_row['Keywords_Lenght'],
                'Total Volume': total_volume,
                'Total Difficulty': total_difficulty,
                'Avarage Volume': ort_volume,
                'Avarage Difficulty':ort_difficulty,
                'Renklenen Keywords Sayısı':counter


            })

        print(f"\033[34mDEBUG: find_matching_keywords() tamamlandı.\033[0m")
        return pd.DataFrame(results),pd.DataFrame(matched_keywords_result)

        
    
class AutocompleteCombobox(ttk.Combobox):
        def set_completion_list(self, completion_list):
            """ Combobox seçenek listesini ayarlar ve filtreleme için gerekli ayarları yapar. """
            self._completion_list = sorted(completion_list, key=str.lower)
            self['values'] = self._completion_list
            self.bind('<KeyRelease>', self._handle_keyrelease)

        def _handle_keyrelease(self, event):
            current_text = self.get()
            if current_text == '':
                self['values'] = self._completion_list
            else:
                filtered = [item for item in self._completion_list if current_text.lower() in item.lower()]
                self['values'] = filtered if filtered else self._completion_list

class Table_Tool():
    
    def __init__(self,root):
        self.root = root
        self.root.title("ASO Generate Tool")
        self.root.geometry("1000x600")
        self.folder_path = tk.StringVar()
        self.difficulty_limit = tk.StringVar(value="20")
        self.open_ai_key=open_ai_key

        self.current_table_name= tk.StringVar(value="Tablo")
        self.merged_noduplicate_df = None
        self.kvd_df = None
        self.kelime_frekans_df = None
        self.without_branded_df = None
        self.without_suffixes_df = None
        self.gpt_title_subtitle_df = None
        self.matching_keywords_df_ts= None
        self.matching_keywords_df= None
        self.selected_countyr= None
        
        self.setup_ui()
    def setup_ui(self):
        """ Arayüz bileşenlerini oluştur. """
        try:
            # 📌 Sürükle & Bırak Klasör Alanı
            self.dnd_frame = tk.LabelFrame(self.root, text="", width=350, height=150, relief=tk.RIDGE, bd=2)
            self.dnd_frame.place(x=10, y=10)
            self.dnd_frame.drop_target_register(DND_FILES)
            self.dnd_frame.dnd_bind("<<Drop>>", self.drop)
            self.info_label = tk.Label(self.dnd_frame, text="\n\t\t\t\t\t\t\t\n\n\nCSV Dosyasını Sürükle Bırak\n\t\t\t\t\t\t\t\n\n\n", bg="lightgray")
            self.info_label.pack(expand=True)
            
            # 📌 Ülke Seçimi için AutocompleteCombobox
            ttk.Label(self.root, text="Select Country:", font=("Arial", 10, "bold")).place(x=160, y=180)
            self.country_var = tk.StringVar()
            self.countrychoosen = AutocompleteCombobox(self.root, width=27, textvariable=self.country_var)

            # Ülke listesini tanımlıyoruz:
            countries = (
                "Afghanistan", "United Arab Emirates", "Antigua and Barbuda", "Anguilla", "Albania", "Armenia", "Angola",
                "Argentina", "Austria", "Australia", "Azerbaijan", "Barbados", "Belgium", "Bosnia and Herzegovina",
                "Burkina Faso", "Bulgaria", "Bahrain", "Benin", "Bermuda", "Brunei", "Bolivia", "Brazil", "Bahamas", "Bhutan",
                "Botswana", "Belarus", "Belize", "Cameroon", "Canada", "Congo, Republic of the", "Switzerland", "Cote d'Ivoire",
                "Chile", "China mainland", "Colombia", "Congo, Democratic Republic of the", "Costa Rica", "Cape Verde",
                "Cyprus", "Czech Republic", "Germany", "Denmark", "Dominica", "Dominican Republic", "Algeria", "Ecuador",
                "Estonia", "Egypt", "Spain", "Finland", "Fiji", "Micronesia", "France", "Gabon", "United Kingdom", "Grenada",
                "Georgia", "Ghana", "Gambia", "Greece", "Guatemala", "Guinea-Bissau", "Guyana", "Hong Kong", "Honduras",
                "Croatia", "Hungary", "Indonesia", "Ireland", "Israel", "India", "Iraq", "Iceland", "Italy", "Jamaica", "Jordan",
                "Japan", "Kenya", "Kyrgyzstan", "Cambodia", "St. Kitts and Nevis", "Republic of Korea", "Kuwait",
                "Cayman Islands", "Kazakhstan", "Laos", "Lebanon", "Libya", "St. Lucia", "Sri Lanka", "Liberia", "Lithuania",
                "Luxembourg", "Latvia", "Morocco", "Moldova", "Maldives", "Madagascar", "North Macedonia", "Mali", "Myanmar",
                "Mongolia", "Montenegro", "Macau", "Mauritania", "Montserrat", "Malta", "Mauritius", "Malawi", "Mexico",
                "Malaysia", "Mozambique", "Namibia", "Niger", "Nigeria", "Nicaragua", "Netherlands", "Norway", "Nepal", "Nauru",
                "New Zealand", "Oman", "Panama", "Peru", "Papua New Guinea", "Philippines", "Pakistan", "Poland", "Portugal",
                "Palau", "Paraguay", "Qatar", "Romania", "Russia", "Rwanda", "Saudi Arabia", "Solomon Islands", "Seychelles",
                "Sweden", "Singapore", "Slovenia", "Slovakia", "Sierra Leone", "Senegal", "Suriname", "Serbia",
                "Sao Tome and Principe", "El Salvador", "Eswatini", "Turks and Caicos Islands", "Chad", "Thailand", "Tajikistan",
                "Turkmenistan", "Tunisia", "Tonga", "Turkey", "Trinidad and Tobago", "Taiwan", "Tanzania", "Ukraine", "Uganda",
                "United States", "Uruguay", "Uzbekistan", "St. Vincent and the Grenadines", "Venezuela", "British Virgin Islands",
                "Vietnam", "Vanuatu", "Kosovo", "Yemen", "South Africa", "Zambia", "Zimbabwe"
            )
            # Seçenek listesini ayarla:
            self.countrychoosen.set_completion_list(countries)
            self.countrychoosen.place(x=180, y=180)
            self.countrychoosen.current(155)


            # 📌 Difficulty Limit Girişi
            tk.Label(self.root, text="Difficulty Sınır:", font=("Arial", 10, "bold")).place(x=20, y=180)
            self.difficulty_entry = tk.Entry(self.root, textvariable=self.difficulty_limit, width=5)
            self.difficulty_entry.place(x=120, y=183)

           


            # 📌 Butonlar (Tablolar)
            button_width, button_height = 300, 35
            start_y = 220  # Butonların başlangıç Y konumu

            tk.Button(self.root, text="Birleştirilmiş Ana Tablo", command=self.show_merged_noduplicate_table).place(x=20, y=start_y, width=button_width, height=button_height)
            tk.Button(self.root, text="Keyword_Volume_Difficulty Tablosu", command=self.show_kvd_table).place(x=20, y=start_y + 40, width=button_width, height=button_height)
            tk.Button(self.root, text="Kelime Frekansı Göster", command=self.show_kelime_frekans_table).place(x=20, y=start_y + 80, width=button_width, height=button_height)
            tk.Button(self.root, text="Branded Kelimelerden Ayrıştırılmış Tablo", command=self.show_without_branded_df).place(x=20, y=start_y + 120, width=button_width, height=button_height)
            tk.Button(self.root, text="Eklerinden Ayrılmış Kelime Frekans Tablosu", command=self.show_without_suffixes_df).place(x=20, y=start_y + 160, width=button_width, height=button_height)
            tk.Button(self.root, text="Title Subtitle Tablosu", command=lambda: self.show_gpt_title_stitle_df(self.app_name_var.get())).place(x=20, y=start_y + 200, width=button_width, height=button_height)

            # 📌 App Name Girişi
            self.app_name_var = tk.StringVar()  
            tk.Entry(self.root, textvariable=self.app_name_var).place(x=140, y=start_y + 280, width=180, height=30)
            tk.Label(self.root, text="Uygulama İsmi:", font=("Arial", 10, "bold")).place(x=20, y=start_y + 280)

            # 📌 Tablo Başlığı
            self.table_title_label = tk.Label(self.root, textvariable=self.current_table_name, font=("Arial", 14, "bold"))
            self.table_title_label.place(x=380, y=10)

            # 📌 Tablo Gösterme Alanı (Sağ Tarafta)
            self.frame = ttk.Frame(self.root)
            self.frame.place(x=380, y=50, width=600, height=500)

            # 📌 Tablo için Scrollbar
            self.tree_scroll = ttk.Scrollbar(self.frame, orient="vertical")
            self.tree_scroll.pack(side="right", fill="y")

            

            style = ttk.Style()
            style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="lightblue", foreground="black")
            self.tree = ttk.Treeview(self.frame, yscrollcommand=self.tree_scroll.set, style="Treeview")

            self.tree = ttk.Treeview(self.frame, yscrollcommand=self.tree_scroll.set)
            self.tree.pack(expand=True, fill="both")
            self.tree_scroll.config(command=self.tree.yview)

            # 📌 Çift tıklama event'ini bağla
            self.tree.bind("<Double-1>", self.on_double_click)

            # 📌 Tabloyu İndir Butonu
            tk.Button(self.root, text="Tabloyu İndir", command=self.tabloyu_kaydet).place(x=700, y=560, width=200, height=35)

        except Exception as e:
            print(f"\033[31mERROR: setup_ui() işleminde hata: {e}\033[0m")

    
    def display_table(self, df):
        """ Verilen DataFrame'i gösterir. """
        try:
            if df is None or df.empty:
                messagebox.showwarning("Uyarı", "Tablo boş!")
                return
            self.tree.delete(*self.tree.get_children())
            self.tree['columns'] = list(df.columns)
            self.tree['show'] = 'headings'
            for col in df.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, anchor="center")
            for idx, row in df.iterrows():
                self.tree.insert("", "end", values=row.tolist())
        except Exception as e:
            print(f"\033[31mERROR: display_table() işleminde hata: {e}\033[0m")
    
    def drop(self, event):
        """ Kullanıcı sürükleyip klasörü bıraktığında çağrılır. """
        dropped_folder = event.data.strip().replace('{', '').replace('}', '')
        print("DEBUG: Klasör bırakıldı:", dropped_folder)
        if os.path.isdir(dropped_folder):
            self.folder_path.set(dropped_folder)
            print("DEBUG: Folder path set:", dropped_folder)
            self.update_table()
        else:
            messagebox.showerror("Hata", "Geçerli bir klasör bırakınız!")

    def update_table(self):
        """ CSV dosyalarını yükler ve temizler. """
        try:
            df = Df_Get.merged_noduplicate_df(self.folder_path.get())
            self.merged_noduplicate_df = df
            limit = float(self.difficulty_limit.get())
            self.kvd_df = Df_Get.kvd_df(df, limit)
            self.kelime_frekans_df = Df_Get.kelime_frekans_df(self.kvd_df,open_ai_key)
            self.without_branded_df=Df_Get.without_branded_kf_df_get(self.kelime_frekans_df,self.open_ai_key)
            #self.without_suffixes_df=pd.DataFrame(Df_Get.without_suffixes_df_get(self.without_branded_df,self.country_var.get(),self.open_ai_key))
            self.current_table=self.merged_noduplicate_df
        except Exception as e:
            print(f"\033[31mERROR: update_table() işleminde hata: {e}\033[0m")

    def on_double_click(self, event):
        """ Sadece `matching_keywords_df` açıkken çift tıklama olayını işler. """
        try:
            if not self.current_table.equals(self.matching_keywords_df_ts):
                messagebox.showerror("Çift tıklama işlemi devre dışı! (Tablo uygun değil)!")
                return  # Eğer uygun tablo açık değilse çık
            
            selected_item = self.tree.selection()
            if not selected_item:
                return  # Hiçbir satır seçilmediyse çık

            item_values = self.tree.item(selected_item, "values")  # Satırın verilerini al
            title_value = item_values[0]  # İlk sütunun Title olduğu varsayılıyor
            subtitle_value = item_values[1]  # İkinci sütunun Subtitle olduğu varsayılıyor

            # 📌 Title ve Subtitle'a göre eşleşen kelimeleri al
            matched_keywords_df=self.matching_keywords_df

            # 📌 Yeni pencere oluştur
            popup = tk.Toplevel(self.root)
            popup.title("Matched Keywords Table")
            popup.geometry("800x400")

            # 📌 Başlık
            tk.Label(popup, text=f"{title_value}, {subtitle_value} İçin Matched Keywords", font=("Arial")).pack(pady=10)

            # 📌 Treeview (Tablo) oluştur
            tree = ttk.Treeview(popup)
            tree["columns"] = list(matched_keywords_df.columns)
            tree["show"] = "headings"

            # 📌 Sütun başlıklarını ekle
            for col in matched_keywords_df.columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=150)

            # 📌 Verileri tabloya ekle
            for _, row in matched_keywords_df.iterrows():
                tree.insert("", "end", values=list(row))

            # 📌 Scrollbar ekle
            scrollbar = ttk.Scrollbar(popup, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

            tree.pack(expand=True, fill="both")

        except Exception as e:
            print(f"\033[31mERROR: on_double_click() işleminde hata: {e}\033[0m")

    def tabloyu_kaydet(self):
        print("DEBUG: tabloyu_kaydet() başlatıldı.")
        if self.current_table is None or self.current_table.empty:
            messagebox.showwarning("Uyarı", "Önce bir tablo oluşturmalısınız!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.current_table.to_csv(file_path, index=False)
            print("DEBUG: Tablo kaydedildi. Dosya yolu:", file_path)
            messagebox.showinfo("Başarılı", "Tablo başarıyla kaydedildi!")
    

    def show_merged_noduplicate_table(self):
        try:
            if self.merged_noduplicate_df is not None:
                self.display_table(self.merged_noduplicate_df)
                self.current_table=self.merged_noduplicate_df
                self.current_table_name.set("Birleştirilmiş Ana Tablo")
            else:
                messagebox.showerror("Hata", "Birleştirilmiş tablo yüklenemedi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Tablo gösterilirken hata oluştu: {e}")

    def show_kvd_table(self):
        try:
            if self.kvd_df is not None:
                self.display_table(self.kvd_df)
                self.current_table=self.kvd_df
                self.current_table_name.set("Keywords Volume Difficulty Tablosu")
            else:
                messagebox.showerror("Hata", "Birleştirilmiş tablo yüklenemedi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Tablo gösterilirken hata oluştu: {e}")

    def show_kelime_frekans_table(self):
        try:
            if self.kelime_frekans_df is not None:
                self.display_table(self.kelime_frekans_df)
                self.current_table=self.kelime_frekans_df
                self.current_table_name.set("Kelime Frekans Tablosu")
            else:
                messagebox.showerror("Hata", "Birleştirilmiş tablo yüklenemedi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Tablo gösterilirken hata oluştu: {e}")

    def show_without_suffixes_df(self):
        try:
            if self.merged_noduplicate_df is not None:
                self.without_suffixes_df=pd.DataFrame(Df_Get.without_suffixes_df_get(self.without_branded_df,self.country_var.get(),self.open_ai_key))
                self.display_table(self.without_suffixes_df)
                self.current_table=self.without_suffixes_df
                self.current_table_name.set("Eklerinden Ayrılmış Kelime Frekans Tablosu")
            else:
                messagebox.showerror("Hata", "Birleştirilmiş tablo yüklenemedi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Tablo gösterilirken hata oluştu: {e}")

    def show_without_branded_df(self):
        try:
            if self.without_branded_df is not None:
                self.display_table(self.without_branded_df)
                self.current_table=self.without_branded_df
                self.current_table_name.set("Branded Kelimelerin Olmadığı Tablo")
            else:
                messagebox.showerror("Hata", "Birleştirilmiş tablo yüklenemedi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Tablo gösterilirken hata oluştu: {e}")

    def show_gpt_title_stitle_df(self, app_name):
        print("DEBUG: gpt_t_s_k_goster() başlatıldı. App Name:", app_name)
        print("DEBUG: Country :", self.country_var.get())
        if self.kelime_frekans_df is None or self.kelime_frekans_df.empty:
            messagebox.showwarning("Uyarı", "Önce CSV dosyasını yükleyin ve işleyin!")
            return

        # GPT'den gelen DataFrame'i alıyoruz.
        self.gpt_title_subtitle_df = Df_Get.gpt_Title_Subtitle_df_get(
            self.without_suffixes_df, app_name, self.country_var.get(), self.open_ai_key
        )
        print("DEBUG: GPT'den gelen DataFrame:\n", self.gpt_title_subtitle_df)

        # Eğer DataFrame boş ise
        if self.gpt_title_subtitle_df.empty:
            messagebox.showinfo(
                f"{color.RED}Bilgilendirme{color.RESET}\n",
                f"GPT'den dönen DataFrame boş. Difficulty limit {float(self.difficulty_limit.get())+10} artırılıyor ve yeniden deneniyor."
            )
            try:
                current_limit = float(self.difficulty_limit.get())
            except ValueError:
                current_limit = float(self.difficulty_limit.get())
            new_limit = current_limit + 10
            self.difficulty_limit.set(str(new_limit))
            
            # İsteğe bağlı: Arayüzü güncellemek için setup_ui'ı yeniden çağırıyoruz.
            self.update_table()
            print(f"{color.YELLOW}DEBUG:Difficulty Sınır değeri {self.difficulty_limit} olarak değiştirildi{color.RESET}")
            # Fonksiyonu tekrar çağırıyoruz.
            self.show_gpt_title_stitle_df(app_name)
            return

        # DataFrame boş değilse, eşleşen anahtar kelimeleri bulup tabloyu gösteriyoruz.
        self.matching_keywords_df_ts, self.matching_keywords_df = Df_Get.find_matching_keywords(
            self.gpt_title_subtitle_df, self.merged_noduplicate_df
        )
        
        self.display_table(self.matching_keywords_df_ts)
        self.current_table = self.matching_keywords_df_ts
        self.current_table_name.set("Title Subtitle Keywords Tablosu")

    
    def show_matching_keywords(self):
        #if self.gpt_title_subtitle_df is None or self.merged_noduplicate_df is None:
        #    messagebox.showwarning("Uyarı", "Önce gerekli tabloları oluşturmalısınız!")
        #    return

        self.matching_keywords_df_ts,_= Df_Get.find_matching_keywords(self.gpt_title_subtitle_df, self.merged_noduplicate_df)
        self.display_table(self.matching_keywords_df_ts)
        self.current_table=self.matching_keywords_df_ts
        self.current_table_name.set("Eşleşen Anahtar Kelimeler Tablosu")
        

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = Table_Tool(root)
    root.mainloop()