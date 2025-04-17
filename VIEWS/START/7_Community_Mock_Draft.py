import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# Headless Chrome-Setup
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

url = "https://www.tankathon.com/nfl"
driver.get(url)
time.sleep(3)  # Warte auf JS-Rendering

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# Die Tabelle ist unter div class="table-responsive"
table = soup.find("table", class_="table")
rows = table.find_all("tr")[1:]

draft_data = []

for row in rows:
    cols = row.find_all("td")
    if not cols or len(cols) < 4:
        continue
    draft_data.append({
        "pick": int(cols[0].text.strip()),
        "team": cols[1].text.strip(),
        "record": cols[2].text.strip(),
        "sos": cols[3].text.strip(),
        "note": cols[4].text.strip() if len(cols) > 4 else ""
    })

df = pd.DataFrame(draft_data)
st.write(df.head())