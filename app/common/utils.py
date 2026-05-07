from datetime import date
from app.common.enums import Semester

AUTUMN_MONTHS = (8,9,10,11,12,1)


def get_curr_year_and_semester() -> tuple[int, Semester]:
    today = date.today()
    year = today.year
    month = today.month
    semester = Semester.AUTUMN if month in AUTUMN_MONTHS else Semester.SPRING
    return year, semester