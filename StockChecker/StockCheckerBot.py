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
    def __init__(self, product_url):
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
                # 'M' beden butonunu bulma ve tıklama
                m_size_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//*[@id='ProductPageDesktop']/div[6]/div[4]/div[2]/div/div[3]/div[1]"))
                )
                m_size_button.click()
                print("M beden seçildi.")

                # Pop-up kontrolü
                if self.is_popup_visible():
                    print("Pop-up göründü. Pop-up kapatılacak ve sayfa yenilenecek.")
                    self.close_popup()  # Pop-up kapama
                    self.refresh_page()  # Sayfayı yenileme
                    time.sleep(2)  # Kapanan pop-up'ın ardından kısa bir bekleme
                    continue  # Pop-up çıkarsa, tekrar bedene tıklamak için döngüye devam et

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

                break  # Ürün sepete eklendiyse döngüden çıkıyoruz

            except Exception as e:
                print(f"Stokta yok veya bir hata oluştu: {str(e)}. Tekrar deneniyor...")
                time.sleep(3)  # Hata sonrası kısa bir bekleme ve yeniden deneme

    def is_popup_visible(self):
        try:
            # Pop-up var mı kontrolü (benzer ürünler pop-up'ı)
            popup_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='ProductPageDesktop']/div[11]/div/div[2]/div"))
            )
            print("Pop-up tespit edildi.")
            return True
        except Exception:
            # Eğer pop-up yoksa hata fırlatılacak, bu durumda False döneriz
            print("Pop-up görünmüyor.")
            return False

    def close_popup(self):
        try:
            # Pop-up kapama butonunu bulma
            close_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='ProductPageDesktop']/div[11]/div/div[1]/button"))
            )
            close_button.click()
            print("Pop-up kapatıldı.")
        except Exception as e:
            print(f"Pop-up kapatılamadı: {str(e)}")

    def refresh_page(self):
        try:
            # Sayfayı yenileme
            self.driver.refresh()
            print("Sayfa yenilendi.")
        except Exception as e:
            print(f"Sayfa yenilenirken hata oluştu: {str(e)}")

    def send_telegram_notification(self):
        bot_token = '7463021219:AAEpR6HZ4-xzGKgNRrhoDFhay5GufSA6cE8'  # BotFather'dan aldığınız bot token
        chat_id = '6514964976'  # Mesajı göndereceğiniz sohbetin ID'si
        message = 'Ürün sepete eklendi. Hemen al!'  # Göndermek istediğiniz mesaj

        # Telegram API'ye HTTP GET isteği gönderiyoruz
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}'

        try:
            response = requests.get(url)
            # Yanıtı kontrol edebilirsiniz
            if response.status_code == 200:
                print("Telegram bildirimi gönderildi.")
            else:
                print(f"Bir hata oluştu: {response.status_code}")
        except Exception as e:
            print(f"Telegram bildirimi gönderilirken hata oluştu: {str(e)}")


if __name__ == "__main__":
    # Kullanıcıdan ürün linkini alma
    product_url = input("Ürün linkini girin: ")

    bot = StockCheckerBot(product_url)
    time.sleep(5)  # Tarayıcının açılması için birkaç saniye bekleyelim
    bot.check_stock_and_add_to_cart()
