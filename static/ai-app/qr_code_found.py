def qr_code_found(inputContent):
    search_list = ['QRCode', 'QRコード', 'qrCode', 'qrコード', 'QR Code', 'QR コード', 'qr Code', 'qr コード']

    found = any(char in inputContent for char in search_list)

    if found:
        return True

    else:
        return False