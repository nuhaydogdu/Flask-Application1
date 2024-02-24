import os
import time
import json
from flask import Flask, render_template
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import io
from pathlib import Path
#  Nuh Aydoğdu 190316020 
#  Kadirhan Özen 190316042
#  Mücahit Berat Uçar 180316044

app = Flask(__name__)

def find_duplicate_values(json_file, key):
    values = []
    with open(json_file, encoding="utf8") as file:
        json_data = json.load(file)
        index = 0
    while index < len(json_data):
        item = json_data[index]
        if key in item:
            value = item[key]
            values.append(value)
        index += 2
    return values

def fetch():
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    # options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--incognito")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    link = "https://acikveri.ysk.gov.tr"
    browser.get(link)

    time.sleep(3)


    close_button = browser.find_element(By.XPATH, "/html/body/app-root/div/div/div/div/div/div/button")
    browser.execute_script("arguments[0].click();", close_button)

    
    time.sleep(2)

    
    choose_election_link = browser.find_element(By.XPATH, "/html/body/app-root/div/div/div/app-topbar/nav/ul/li[2]/a")
    choose_election_link.click()



    president_link = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/ngb-modal-window/div/div/div[2]/div/div[7]/div[1]"))
    )
    president_link.click()

    president_date = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//html/body/ngb-modal-window/div/div/div[2]/div/div[7]/div[4]/div/div"))
    )
    president_date.click()

    
    election_results_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//html/body/app-root/div/app-sidebar/ul/li[8]/a"))
    )
    election_results_link.click()

    
    download_json_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-secim-sonuc-yurtici/div/div/div/div[2]/div/div/div[2]/div[2]/div/button[2]"))
    )
    browser.execute_script("arguments[0].click();", download_json_link)

    downloads_path = str(Path.home() / "Downloads/SecimSonucIl.json")
    

    while not os.path.exists(downloads_path):
        time.sleep(1)
    
    browser.quit()
    return downloads_path

def parse(raw_text):

    data = {
        'Candidate': ['İnce', 'Erdoğan', 'Akşener', 'Demirtaş', 'Karamollaoğlu', 'Perinçek'],
        'Percentage': [raw_text['ince'], raw_text['tayyip'], raw_text['aksener'], raw_text['demirtas'], raw_text['karamollaoglu'], raw_text['perincek']]
    }
    df = pd.DataFrame(data)
    return df

def calculate(duplicates):
    total = 0
    for value in duplicates:
        
        cleaned_value = value.replace(".", "")
        total += int(cleaned_value)
    return total

@app.route("/")
def main():
    results = {}
    file_path = fetch()

    ince = find_duplicate_values(file_path, " MUHARREM İNCE ")
    x = calculate(ince)


    tayyip = find_duplicate_values(file_path, " RECEP TAYYİP ERDOĞAN ")
    y = calculate(tayyip)

    

    aksener = find_duplicate_values(file_path, " MERAL AKŞENER ")
    z = calculate(aksener)
  
    

    demirtas = find_duplicate_values(file_path, " SELAHATTİN DEMİRTAŞ ")
    c = calculate(demirtas)

    

    karamollaoglu = find_duplicate_values(file_path, " TEMEL KARAMOLLAOĞLU ")
    v = calculate(karamollaoglu)

    

    perincek = find_duplicate_values(file_path, " DOĞU PERİNÇEK ")
    b = calculate(perincek)

    
    genel_toplam = x + y + z + c + v + b

    results["ince"] = (100 * x) / genel_toplam
    results["tayyip"] = (100 * y) / genel_toplam
    results["aksener"] = (100 * z) / genel_toplam
    results["demirtas"] = (100 * c) / genel_toplam
    results["karamollaoglu"] = (100 * v) / genel_toplam
    results["perincek"] = (100 * b) / genel_toplam

    df = parse(results)
    print(df)
        
    return render_template("index.html",
                            x=df['Candidate'].tolist(),
                            y=df['Percentage'].tolist(),
                            content=df.to_html()
                           )


if __name__ == "__main__":
    app.run()
