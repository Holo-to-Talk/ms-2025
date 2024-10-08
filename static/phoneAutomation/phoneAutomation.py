from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# 定数
# URL（※定期的に変わる可能性）
URL = 'https://k1zuna.shop/'
# 電話番号（代表回線）
PHONE_NUMBER = '+1 8302242800'

# Options指定
options = Options()
# マイク（カメラ）ポップアップ無効化
options.add_argument('--use-fake-ui-for-media-stream')

# ChromeDriver起動
driver = webdriver.Chrome(options = options)

# 指定URLアクセス
driver.get(URL)

# ブラウザ起動 → 電話をかけるまで
try:
    # 「Visit Site」
    # ButtonがClick可能になるまで待機
    #visitSiteButton = WebDriverWait(driver, 10).until(
    #    EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/main/div/div/section[1]/div/footer/button'))
    #)
    # Click
    #visitSiteButton.click()

    # 「デバイスを起動する」
    # ButtonがClick可能になるまで待機
    startUpButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="startup-button"]'))
    )
    # Click
    startUpButton.click()

    # 「オーディオ情報を再読み込みする」
    # ButtonがClick可能になるまで待機
    getDevicesButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="get-devices"]'))
    )
    # Click
    getDevicesButton.click()

    # 「発信先の電話番号を入力してください。」
    # Inputが入力可能になるまで待機
    phoneNumberInput = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="phone-number"]'))
    )
    # 入力
    phoneNumberInput.send_keys(PHONE_NUMBER)

    # 「発信」
    # ButtonがClick可能になるまで待機
    callButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="button-call"]'))
    )
    # Click
    callButton.click()

except Exception as e:
    print(f"Error: {e}")

# 「電話を終了」
# ButtonがClick可能になるまで待機
hangUpOutGoingButton = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="button-hangup-outgoing"]'))
)

# 電話がつながる → 電話が途切れる → ブラウザを閉じるまで
try:
    # 電話が途切れるまでタブを維持（「電話を終了」ボタンが消えた瞬間 = 電話が切れた（途切れた）瞬間）
    while True:
        # ButtonのClass取得
        hangUpOutGoingButton_className = hangUpOutGoingButton.get_attribute('class')
        # 「電話を終了」ボタンを消すClass（hide）があるかないか
        if 'hide' in hangUpOutGoingButton_className.split():
            # hideがある（「電話を終了」ボタンが消えた = 電話が途切れた）
            # Browserを閉じる
            driver.quit()
            # ループ終了
            exit
        else:
            # hideがない（「電話を終了」ボタンがある = 電話が途切れていない）
            # 5秒ごとに確認
            time.sleep(5)

except Exception as e:
    print(f"Error: {e}")