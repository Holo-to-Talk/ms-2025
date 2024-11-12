from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def phoneAutomation():
    # 定数
    # URL
    # 本番
    URL = 'https://holog.net/'
    # 開発
    # URL = 'https://num-0145.holog.net/'
    # 電話番号（代表回線）
    PHONE_NUMBER = '+1 8302242800'
    # WebDriverWaitの時間指定
    WEB_DRIVER_WAIT_TIME = 10
    # time.sleepの時間指定
    TIME_SLEEP_TIME = 5

    # Options指定
    options = Options()
    # マイク（カメラ）ポップアップ無効化
    options.add_argument('--use-fake-ui-for-media-stream')
    # 証明書エラー無視
    options.add_argument('--ignore-certificate-errors')
    # SSLエラー無視
    options.add_argument('--ignore-ssl-errors')
    # GPUの無効化
    options.add_argument('--disable-gpu')
    # ソフトウェアによるレンダリングの無効化
    options.add_argument('--disable-software-rasterizer')

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
        startUpButton = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="startup-button"]'))
        )
        # Click
        startUpButton.click()

        # 「オーディオ情報を再読み込みする」
        # ButtonがClick可能になるまで待機
        getDevicesButton = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="get-devices"]'))
        )
        # Click
        getDevicesButton.click()

        # 「発信先の電話番号を入力してください。」
        # Inputが入力可能になるまで待機
        phoneNumberInput = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="phone-number"]'))
        )
        # 入力
        phoneNumberInput.send_keys(PHONE_NUMBER)

        # 「発信」
        # ButtonがClick可能になるまで待機
        callButton = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="button-call"]'))
        )
        # Click
        callButton.click()

    except Exception as e:
        print(f"Error: {e}")

    # 「電話を終了」
    # ButtonがClick可能になるまで待機
    hangUpOutGoingButton = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
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
                break
            else:
                # hideがない（「電話を終了」ボタンがある = 電話が途切れていない）
                # 5秒ごとに確認
                time.sleep(TIME_SLEEP_TIME)

    except Exception as e:
        print(f"Error: {e}")