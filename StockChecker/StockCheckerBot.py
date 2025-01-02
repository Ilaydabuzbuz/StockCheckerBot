import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests

class StockCheckerBot:
    def __init__(self, product_url, size):
        self.size = size.upper()  # Convert size to uppercase for consistency
        self.size_xpath_map = {
            'XS': "//*[@id='ProductPageDesktop']/div[6]/div[4]/div[2]/div/div[1]/div",
            'S': "//*[@id='ProductPageDesktop']/div[6]/div[4]/div[2]/div/div[2]/div",
            'M': "//*[@id='ProductPageDesktop']/div[6]/div[4]/div[2]/div/div[3]/div[1]",
            'L': "//*[@id='ProductPageDesktop']/div[6]/div[4]/div[2]/div/div[4]/div",
            'XL': "//*[@id='ProductPageDesktop']/div[6]/div[4]/div[2]/div/div[5]/div"
        }

        # Validate size input
        if self.size not in self.size_xpath_map:
            raise ValueError(f"Invalid size: {self.size}. Available sizes are: {', '.join(self.size_xpath_map.keys())}")

        # ChromeOptions nesnesi oluşturuluyor
        options = Options()
        options.add_argument("--disable-gpu")
        # options.add_argument("--headless")  # Tarayıcıyı başlatmadan işlemi yapma (isteğe bağlı)

        # ChromeDriver'ı başlatmak için Service kullanıyoruz
        service = Service(ChromeDriverManager().install())

        try:
            # WebDriver'ı başlatma
            self.driver = webdriver.Chrome(service=service, options=options)
            print("Tarayıcı başlatıldı.")
        except Exception as e:
            print(f"Tarayıcı başlatılırken hata oluştu: {str(e)}")
            return

        # Sayfayı açma
        try:
            self.driver.get(product_url)
            print(f"Sayfa açıldı: {product_url}")
        except Exception as e:
            print(f"Sayfa açılırken hata oluştu: {str(e)}")
            return

        # Sayfayı tam ekran yapıyoruz
        self.driver.maximize_window()
        print("Tarayıcı tam ekran yapıldı.")

    def check_stock_and_add_to_cart(self):
        while True:
            try:
                # Seçilen bedeni bulma ve tıklama
                size_xpath = self.size_xpath_map[self.size]
                size_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, size_xpath))
                )
                size_button.click()
                print(f"{self.size} beden seçildi.")

                # Pop-up kontrolü
                if self.is_popup_visible():
                    print("Pop-up göründü. Pop-up kapatılacak ve sayfa yenilenecek.")
                    self.close_popup()
                    self.refresh_page()
                    time.sleep(2)
                    continue

                # Sepete Ekle butonuna tıklama
                add_to_cart_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='ProductPageDesktop']/div[6]/div[5]/div/button"))
                )
                add_to_cart_button.click()
                print("Ürün sepete eklendi.")

                # Sepete eklendi yazısını bekleme
                time.sleep(5)
                print("Ürün sepete başarıyla eklendi!")

                # Telegram bildirimi gönderme
                self.send_telegram_notification()

                break

            except Exception as e:
                print(f"Stokta yok veya bir hata oluştu: {str(e)}. Tekrar deneniyor...")
                time.sleep(3)

    def is_popup_visible(self):
        try:
            popup_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='ProductPageDesktop']/div[11]/div/div[2]/div"))
            )
            print("Pop-up tespit edildi.")
            return True
        except Exception:
            print("Pop-up görünmüyor.")
            return False

    def close_popup(self):
        try:
            close_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='ProductPageDesktop']/div[11]/div/div[1]/button"))
            )
            close_button.click()
            print("Pop-up kapatıldı.")
        except Exception as e:
            print(f"Pop-up kapatılamadı: {str(e)}")

    def refresh_page(self):
        try:
            self.driver.refresh()
            print("Sayfa yenilendi.")
        except Exception as e:
            print(f"Sayfa yenilenirken hata oluştu: {str(e)}")

    def send_telegram_notification(self):
        bot_token = '7463021219:AAEpR6HZ4-xzGKgNRrhoDFhay5GufSA6cE8'
        chat_id = '6514964976'
        message = f'{self.size} beden ürün sepete eklendi. Hemen al!'

        url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}'

        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Telegram bildirimi gönderildi.")
            else:
                print(f"Bir hata oluştu: {response.status_code}")
        except Exception as e:
            print(f"Telegram bildirimi gönderilirken hata oluştu: {str(e)}")


if __name__ == "__main__":
    # Kullanıcıdan ürün linkini ve beden bilgisini alma
    product_url = input("Ürün linkini girin: ")
    size = input("Beden seçin (XS/S/M/L/XL): ")

    try:
        bot = StockCheckerBot(product_url, size)
        time.sleep(5)
        bot.check_stock_and_add_to_cart()
    except ValueError as e:
        print(e)