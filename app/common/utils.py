from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from app.common.enums import Semester


AUTUMN_MONTHS = (8, 9, 10, 11, 12, 1)


def get_curr_year_and_semester() -> tuple[int, Semester]:
    today = date.today()
    year = today.year
    month = today.month
    semester = Semester.AUTUMN if month in AUTUMN_MONTHS else Semester.SPRING
    return year, semester


def split_fullname(fullname: str) -> tuple[str, str | None, str | None]:
    splitted = fullname.split(" ")
    if len(splitted) < 2:
        return fullname, None, None
    last_name = splitted[0]
    first_name = splitted[1]
    patronymic = splitted[2] if len(splitted) > 2 else None
    return last_name, first_name, patronymic


def get_next_week_range() -> tuple[datetime, datetime]:
    today = (
        datetime.today()
        .astimezone(ZoneInfo("Asia/Yekaterinburg"))
        .replace(hour=0, minute=0, second=0, microsecond=0)
    )
    start_date = today + timedelta(days=1)
    end_date = today + timedelta(days=6)
    return start_date, end_date.replace(hour=23, minute=59, second=59, microsecond=59)
