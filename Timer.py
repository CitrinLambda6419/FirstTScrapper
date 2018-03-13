from datetime import date, datetime, timedelta, time
import time


class Timer:
    def __init__(self):
        self.utc_start_time = timedelta(hours=8)
        self.utc_start_time_in_hours = 8
        self.utc_end_time_in_hours = 10
        self.working_time_in_minutes = 120
        self.day_off = 5
        self.last_working_day = 4
        self.one_day = timedelta(hours=24)


    def get_time_for_next_event(self):
        current_hour = timedelta(hours=datetime.utcnow().
                                 hour, minutes=datetime.utcnow().
                                 minute, seconds=datetime.utcnow().
                                 second)
        # If status for first 4 days of week
        if datetime.today().weekday() < self.last_working_day:
            # If date time between start and end of work time, return 0
            if (datetime.utcnow().hour >= self.utc_start_time_in_hours) & (
                        datetime.utcnow().hour < self.utc_end_time_in_hours):
                return timedelta(minutes=0)
            # If the working time has not come, return interval before working time
            elif datetime.utcnow().hour < self.utc_start_time_in_hours:
                return self.utc_start_time - current_hour
            # Get time until the end of the day, then add the time before the start of the event
            else:
                return self.one_day - current_hour + self.utc_start_time
        # Friday
        elif datetime.today().weekday() == self.last_working_day:
            if (datetime.utcnow().hour >= self.utc_start_time_in_hours) & (
                        datetime.utcnow().hour < self.utc_end_time_in_hours):
                return timedelta(minutes=0)
            elif datetime.utcnow().hour < self.utc_end_time_in_hours:
                return self.utc_start_time - current_hour
            else:
                return self.one_day - current_hour + self.utc_start_time + timedelta(hours=48)
        # Saturday
        elif datetime.today().weekday() == self.day_off:
            if datetime.utcnow().hour < self.utc_start_time_in_hours:
                return self.utc_start_time - current_hour + timedelta(hours=48)
            else:
                return self.one_day - current_hour + self.utc_start_time + timedelta(hours=24)
        # Sunday
        else:
            if datetime.utcnow().hour < self.utc_start_time_in_hours:
                return self.utc_start_time - current_hour + timedelta(hours=24)
            else:
                return self.one_day - current_hour + self.utc_start_time


    def wait_next_event(self):
        alarm_clock = round((self.get_time_for_next_event()).total_seconds())
        time.sleep(alarm_clock)
        time_for_next_event = self.get_time_for_next_event
        time.sleep(time_for_next_event)


    def start_timer(self):
        import Scrapper
        sc = Scrapper.ScrapperController()
        sc.start_telegram_bot()
        while True:
            self.wait_next_event()
            sc.execute_prepare_sequence()
            i = 0
            ## Repeat for two hours with intervals of one minute
            while i < self.working_time_in_minutes:
                sc.check_list()
                time.sleep(60)
                i += 1
            sc.get_total()
            sc.close_browser()
