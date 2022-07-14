from datetime import datetime

from khayyam import JalaliDatetime
from pytz import timezone


def PersianDateTime(date: datetime) -> str:
    ir_date = JalaliDatetime(
        date.astimezone(tz=timezone('Asia/Tehran'))
    )
    return str(ir_date)
