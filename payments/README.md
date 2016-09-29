# Payments

**Variable symbol** should be the order's `ID`.


## Installation

- Install fiobank module - `pip install -r payments/requirements.txt`.
- Add `payments` to installed apps.
- Set `FIO_BANK_TOKEN = 'token'` in settings.
- Set `PAYMENT_ERROR_RATE = 0` (percentage) in settings.


## Usage

    from payments.utils import check_payments_status
    check_payments_status()
