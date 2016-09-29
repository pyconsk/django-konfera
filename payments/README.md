# Payments

**Variable symbol** should be the order's `ID`.


## Installation

- Install fiobank module - `pip install fiobank==1.2.0`.
- Add `payments` to installed apps.
- Set `FIO_BANK_TOKEN = 'token'` in settings.
- Set `PAYMENT_ERROR_RATE = Decimal('0.0')` in settings.


## Usage

    from payments.utils import check_payments_status
    check_payments_status()
