import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def save_cookies_to_file(cookies, filename):
    with open(filename, 'w') as f:
        f.write("# Netscape HTTP Cookie File\n")
        for cookie in cookies:
            domain = cookie.get('domain', '')
            flag = 'TRUE' if domain.startswith('.') else 'FALSE'
            path = cookie.get('path', '/')
            secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
            expiry = str(cookie.get('expiry', 0))
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
    print(f"[INFO] Cookies saved to {filename}")

def main():
    print("Starte Chrome-Browser, um YouTube-Cookies zu erfassen.")
    print("Bitte melde dich in dem geöffneten Browser-Fenster bei YouTube an.")
    print("Sobald du angemeldet bist, kehre in dieses Terminal zurück und drücke Enter.")
    
    # Chrome-Optionen (Nicht headless, damit du den Login durchführen kannst)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Initialisiere den ChromeDriver (webdriver_manager lädt den passenden Treiber)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    # Öffne YouTube
    driver.get("https://www.youtube.com")
    
    input("Drücke Enter, sobald du dich angemeldet hast...")
    
    # Cookies auslesen
    cookies = driver.get_cookies()
    driver.quit()
    
    # Speichere die Cookies in Netscape-Format
    cookie_file = os.path.join(os.getcwd(), "youtube_cookies.txt")
    save_cookies_to_file(cookies, cookie_file)
    
if __name__ == "__main__":
    main()