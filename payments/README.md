# Payments

**Variable symbol** should be the order's `ID`.


## Installation

- Install fiobank module - `pip install fiobank==1.2.0`.
- Add `payments` to installed apps.
- Set `FIO_BANK_TOKEN` variable in settings.


## Usage

        from payments.utils import check_payments_status
        check_payments_status()
