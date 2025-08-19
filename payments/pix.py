import uuid
import qrcode

class Pix:
  def __init__(self):
    pass

  def create_payment(self, base_dir=""):
    #  Create the payment in the banking system
    #  Return the bank_payment_id and the qr_code_path
    
    # Generating locally since this is a fake API
    # should come from the banking system
    bank_payment_id = str(uuid.uuid4())

    #  Hash payment should come from the banking system
    hash_payment  = f"hash_payment_{bank_payment_id}"
    
    # qr code
    qr_code = qrcode.make(hash_payment)
    qr_code.save(f"{base_dir}static/img/qr_code_payment_{bank_payment_id}.png")

    return {
      "bank_payment_id": bank_payment_id,
      "qr_code_path": f'qr_code_payment_{bank_payment_id}',
    }