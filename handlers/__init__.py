from .com_start import router as start_router
from .city import router as city_router
from .feedback import router as feedback_router
from .statistic import router as stat_router
from .weather_day_week import router as weather_day_week_router
from .fishing_calender import router as fishing_calender_router
from .back import router as back_to_main_menu
from .links import router as links
from .connection import router as connection
from .SOS import router as sos
from .ride_ads import router as ride_ads
routers = [
    start_router,
    city_router,
    feedback_router,
    stat_router,
    weather_day_week_router,
    fishing_calender_router,
    back_to_main_menu,
    links,
    connection,
    sos,
    ride_ads,



]
