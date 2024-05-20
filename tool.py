import qrcode
import pyotp


def generate_qr_code():
    secret = pyotp.random_base32()
    print(f'Admin secret: {secret}')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(pyotp.totp.TOTP(secret).provisioning_uri(name='Admin', issuer_name='prompt doc'))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("admin_auth.png")


if __name__ == '__main__':
    generate_qr_code()
