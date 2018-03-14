from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import TelegramBot
import re
import Logger
import sys


class ItemObject:
    def __init__(self):
        self.name = ""
        self.offer_price = 0
        self.offer_weight = 0
        self.demand_price = 0
        self.demand_weight = 0
        self.demand_request = False
        self.order_request = False
        self.deal = False
        self.average_price = 0
        self.total_weight = 0
        self.total_price = 0

    def equals(self, object):
        if self.offer_price == object.offer_price:
            if self.offer_weight == object.offer_weight:
                if self.name == object.name:
                    if self.demand_price == object.demand_price:
                        if self.demand_weight == object.demand_weight:
                            if self.average_price == object.average_price:
                                if self.total_weight == object.total_weight:
                                    return self.total_price == object.total_price

    def compare_deal(self, object):
        if self.deal == object.deal:
            return True
        else:
            return False

    def is_differente(self, object):
        if (self.demand_request == True) == (self.demand_request != object.order_request):
            return True
        elif (self.order_request == True) == (self.order_request != object.demand_request):
            return True
        else:
            return False

    def status_is_equal(self, object):
        if self.deal == object.deal:
            if self.order_request == object.order_request:
                return self.deal == object.deal
            else:
                return False
        else:
            return False


class OutputMessageBuilder:
    def __init__(self):
        pass;

    def total_message(self, result):
        constructed_string = []
        if result.get("average_price") == 0:
            constructed_string.append("Сегодня не было заключеноне сделок")
        else:
            constructed_string.append(
                (
                    f"По итогам торгов были заключены сделки по средней цене  {result.get('average_price')} р. объемом {result.get('weight')}т. на общую сумму {result.get('price')} р."))
        return constructed_string

    def build_message_by_status(self, status, item):
        if status == "add":
            if item.demand_request:
                if item.order_request:
                    return f"На бирже появился СПРОС, {item.name}, в объеме {item.demand_weight}, по цене {item.demand_price} р." \
                           f"\nНа бирже появилоcь ПРЕДЛОЖЕНИЕ, {item.name}, в объеме {item.offer_weight}, по цене {item.offer_price} р."
                else:
                    return f"На бирже появился СПРОС, {item.name}, в объеме {item.demand_weight}, по цене {item.demand_price} р."
            elif item.order_request:
                return f"На бирже появилоcь ПРЕДЛОЖЕНИЕ, {item.name}, в объеме {item.offer_weight}, по цене {item.offer_price} р."
            elif item.deal:
                return f"На бирже ПРОИЗОШЛА!!! СДЕЛКА!!!, {item.name}, по цене {item.total_price}"
            else:
                return f"Incorrect status item.order_request {item.order_request}, item.order_request = {item.order_request}, name = {item.name}"
        elif status == "deal":
            return f"На бирже ПРОИЗОШЛА!!! СДЕЛКА!!!, {item.name}, по цене {item.total_price}"
        else:
            return f"Status incorrect. Status: '{status}'"


class ListOfItemObjects:
    def __init__(self):
        self.main_list = []
        self.executed_object = 0

    def compare(self, item):
        for object in self.main_list:
            if object.equals(item):
                return True
        return False

    def add_item(self, object):
        for item in self.main_list:
            if item.equals(object):
                return 0
            if item == self.main_list[len(self.main_list) - 1]:
                self.main_list.append(object)
                return object
        return 0

    def check_changes_in_status(self, target_item, compared_item):
        if target_item.status_is_equal(compared_item):
            return "none", target_item, compared_item
        elif target_item.is_differente(compared_item):
            return "add", target_item, compared_item
        elif target_item.compare_deal(compared_item):
            target_item.deal = True
            compared_item.deal = True
            return "deal", target_item, compared_item
        else:
            return "add", target_item, compared_item

    def check_current_status(self, target_item):
        if target_item.deal == True:
            return "deal"
        else:
            return "add"

    def cleane_str_in_int(self, object_string):
        string_without_nbsp = str(object_string).replace('&nbsp;', ' ')
        list_of_string_elements = string_without_nbsp.split(" ")
        cleared_string = ""
        for string in list_of_string_elements:
            cleared_string += str(string)
        return int(re.search(r'\d+', cleared_string).group())

    def get_all_deal(self):
        count_deal = 0
        average_price = 0
        total_weight = 0
        count_cost = 0
        for item in self.main_list:
            if item.deal:
                total_weight += self.cleane_str_in_int(item.total_weight)
                count_deal += 1
                average_price += self.cleane_str_in_int(item.average_price)
                count_cost += self.cleane_str_in_int(item.total_price)
        if (average_price != 0): average_price = int(round(average_price / count_deal))
        result = {"weight": total_weight, "average_price": average_price, "price": count_cost}
        return result


class Browser:
    def __init__(self, logger):
        self.logger = logger
        self.driver = webdriver.Chrome()
        self.delay = 3  # seconds

    def get_page(self, page):
        self.driver.get(str(page))

    def active_checkbox(self, xpath):
        self.driver.find_element_by_xpath(xpath).click()

    def input_text_in_form(self, form_xpath, inputed_text):
        self.driver.find_element_by_xpath(form_xpath).send_keys(inputed_text)

    def wait_for_loading_id(self, id):
        try:
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.ID, id)))
        except TimeoutException:
            self.logger.write_error(sys.exc_info()[0])

    def get_str_list_by_class_name(self, class_name):
        elements_list = []
        for elm in self.driver.find_elements_by_class_name(class_name):
            self.logger.write_info(f"Finded item id: {elm.text}")
            elements_list.append(elm.text)
        return elements_list

    def separator(self, object):
        if str(object.text) != "—":
            if str(object.text) != "":
                list_of_strings = []
                try:
                    list_of_strings = object.text.split("\n")
                except:
                    self.logger.write_error(
                        f"Error: {sys.exc_info()[0]} \n Object text: {object.text} \n {sys.exc_info()[1]}{sys.exc_info()[2]}\n{sys.exc_info()[3]}")
                if (len(list_of_strings) == 2):
                    if list_of_strings[1] != "—":
                        return list_of_strings[0], list_of_strings[1]
                    else:
                        return list_of_strings[0], 0
                else:
                    return 0, 0
        else:
            return 0, 0

    def scrap_list_of_items(self, class_name, list_for_search):
        result_list = []
        for item_id in list_for_search:
            parent_element = self.driver.find_element_by_class_name(class_name)
            item = ItemObject()

            if parent_element.find_elements_by_id(item_id):
                for a in parent_element.find_elements_by_id(item_id):
                    i = 0
                    print(a.text)
                    if a.find_elements_by_tag_name("td"):
                        for b in a.find_elements_by_tag_name("td"):
                            # Td container
                            ##Name
                            if i == 0:
                                item.name = b.text
                            ##Offer
                            if i == 1:
                                item.offer_price, item.offer_weight = self.separator(b)
                            ##Demand
                            if i == 3:
                                item.demand_price, item.demand_weight = self.separator(b)
                            ##Average price, exist only if item was sold
                            if i == 4:
                                item.average_price, item.percent_of_changes = self.separator(b)
                            ##Result of deal in total price and weight
                            if i == 5:
                                item.total_price, item.total_weight = self.separator(b)
                            i += 1

                    if (item.offer_price != 0) & (item.demand_price == 0):
                        item.order_request = True
                        item.demand_request = False
                        item.deal = False
                        print("1")
                    elif (item.offer_price == 0) & (item.demand_price != 0):
                        item.demand_request = True
                        item.order_request = False
                        item.deal = False
                        print("2")
                    elif (item.average_price != 0):
                        item.order_request = False
                        item.demand_request = False
                        item.deal = True

                    else:
                        item.demand_request = True
                        item.order_request = True
                        item.deal = False

                    result_list.append(item)
        return result_list

    def result_analyzer(self, result_list, list_of_items, message_builder):
        list_of_changes = []
        ## If main list have any item, compare it with new items
        if len(list_of_items.main_list) != 0:
            for new_item in result_list:
                for item in list_of_items.main_list:
                    if item.equals(new_item):
                        changes_in_status, item, new_item = list_of_items.check_changes_in_status(item, new_item)
                        ## If status of item have been changed, swap item in main list to the new
                        if changes_in_status != "none":
                            constructed_message = message_builder.build_message_by_status(changes_in_status, new_item)
                            list_of_changes.append(constructed_message)
                            list_of_items.main_list.remove(item)
                            list_of_items.main_list.append(new_item)
                            self.logger.write_info(f"Added message: {new_item.name}")

        ## If main list do not have any item, construct list of changes and main list
        else:
            for new_item in result_list:
                constructed_message = message_builder.build_message_by_status("add", new_item)
                list_of_changes.append(constructed_message)
                list_of_items.main_list.append(new_item)
                self.logger.write_info(f"Added message: {new_item.name}")
        return list_of_changes, list_of_items

    def quit(self):
        self.driver.quit()


class ScrapperController():
    def __init__(self):
        self.list_of_titles_by_xpath = '//*[@id="status_id"]'
        self.checkbox_xpath = '//*[@id="fname"]'
        self.title_name = 'конденсат газовый'
        self.url_titles_location = "http://spimex.com/markets/oil_products/instrument_list/"
        self.url_of_parsing = "http://spimex.com/markets/oil_products/trades/"
        self.js_class_name_tabel = "trade-time"
        self.titles_class_name = "black"
        self.class_name_for_active_form = "trade-time"
        self.browser = 0
        self.list_of_item_objects = ListOfItemObjects()
        self.list_for_search = []
        self.logger = Logger.Logger('./var/tmp/myapp.log')

    def execute_prepare_sequence(self):
        self.browser = Browser(self.logger)
        self.browser.get_page(self.url_titles_location)
        self.browser.input_text_in_form(self.checkbox_xpath, self.title_name)
        self.browser.active_checkbox(self.list_of_titles_by_xpath)
        self.browser.wait_for_loading_id(self.titles_class_name)
        self.list_for_search = self.browser.get_str_list_by_class_name(self.titles_class_name)
        self.browser.get_page(self.url_of_parsing)

    def start_telegram_bot(self):
        TelegramBot.start_bot()

    def send_message(self, message_list):
        TelegramBot.add_message(message_list)

    def check_list(self):
        text_list_results, self.list_of_item_objects = self.browser.result_analyzer(self.browser.scrap_list_of_items(
            self.js_class_name_tabel, self.list_for_search), self.list_of_item_objects, OutputMessageBuilder())
        if text_list_results != "none":
            self.send_message(text_list_results)

    def get_total(self):
        result = self.list_of_item_objects.get_all_deal()
        message = OutputMessageBuilder().total_message(result)
        self.send_message(message)

    def close_browser(self):
        self.browser.quit()
        self.list_of_item_objects.main_list.clear()
