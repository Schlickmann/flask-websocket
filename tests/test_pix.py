import sys
sys.path.append('../')

import pytest
import os

from payments.pix import Pix

def test_create_payment():
    pix = Pix()
    
    # create a payment
    payment = pix.create_payment(base_dir="../")

    # check if the payment was created
    assert payment['bank_payment_id'] is not None
    assert payment['qr_code_path'] is not None

    # check if the qr code was created
    assert os.path.exists(f"../static/img/{payment['qr_code_path']}.png")

    # delete the payment
    os.remove(f"../static/img/{payment['qr_code_path']}.png")
    