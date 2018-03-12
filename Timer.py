from datetime import date, datetime, timedelta, time
import time


class Timer:
    def __init__(self):
        self.utc_time_interval = datetime.now() - datetime.utcnow()
        self.utc_start_time = timedelta(hours=8)

    def get_time_for_next_event(self):
        current_hour = timedelta(hours=datetime.utcnow().
                                 hour, minutes=datetime.utcnow().
                                 minute, seconds=datetime.utcnow().
                                 second, milliseconds=datetime.utcnow().microsecond)
        if datetime.today().weekday() < 4:
            if current_hour < self.utc_start_time:
                return self.utc_start_time - current_hour
            else:
                return timedelta(hours=24) - current_hour + self.utc_start_time
        elif datetime.today().weekday() == 4:
            if current_hour < self.utc_start_time:
                return self.utc_start_time - current_hour
            else:
                return timedelta(hours=24) - current_hour + self.utc_start_time + timedelta(hours=48)
        elif datetime.today().weekday() == 5:
            if current_hour < self.utc_start_time:
                return self.utc_start_time - current_hour + timedelta(hours=48)
            else:
                return timedelta(hours=24) - current_hour + self.utc_start_time + timedelta(hours=24)
        else:
            if current_hour < self.utc_start_time:
                return self.utc_start_time - current_hour
            else:
                return timedelta(hours=24) - current_hour + self.utc_start_time

    def wait_next_event(self):
        alarm_clock = round((self.get_time_for_next_event()).total_seconds())
        time.sleep(alarm_clock)
        time.sleep(self.get_time_for_next_event)

    def start_timer(self):
        import Scrapper
        sc = Scrapper.ScrapperController()
        sc.start_telegram_bot()
        while True:
            self.wait_next_event()
            sc.execute_prepare_sequence()
            i = 0
            ## Repeat for two hours with intervals of one minute
            while i < 120:
                sc.check_list()
                time.sleep(60)
                i += 1
            sc.get_total()
            sc.close_browser()
