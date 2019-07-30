import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def find_element(driver, tag_name, tag_attr_val, tag_attr='data-testid'):
    elements = driver.find_elements_by_tag_name(tag_name)
    for element in elements:
        if element.get_attribute(tag_attr) == tag_attr_val:
            return element
    return None


def find_done_button(driver, container_tag, container_tag_attr_value):
    element = find_element(driver, container_tag, container_tag_attr_value)
    button = element.find_element_by_tag_name('button')
    if button.text == 'Done':
        return button
    return None


def find_form_element(form, element_tag, element_tag_attr, element_tag_attr_value=None, element_text=None):
    elements = form.find_elements_by_tag_name(element_tag)
    for element in elements:
        if element_tag_attr_value and element.get_attribute(element_tag_attr) == element_tag_attr_value:
            return element
        if element_text and element.text == element_text:
            return element
    return None


def clear_text(element, value_len):
    for i in range(0, value_len+1):
        element.send_keys(Keys.BACKSPACE)


def wait(wait_time=10):
    print(f"Going to hangout for {wait_time} seconds")
    time.sleep(wait_time)


def log_msg(msg):
    print(msg)


class _LoginUser(object):

    def __init__(self, driver, robinhood_url, username, password):
        self.driver = driver
        self.username = username
        self.password = password
        self.robinhood_url = robinhood_url

    def _enter_username(self):
        username_xpath = '//*[@id="react_root"]/div/div[1]/div[2]/div/div[2]/div/div/form/div/div[1]/div[1]/label/div[2]/input'
        username_tb = self.driver.find_element_by_xpath(username_xpath)
        username_tb.send_keys(self.username)
        wait()

    def _enter_password(self):
        password_xpath = '//*[@id="react_root"]/div/div[1]/div[2]/div/div[2]/div/div/form/div/div[1]/div[2]/label/div[2]/input'
        password_tb = self.driver.find_element_by_xpath(password_xpath)
        password_tb.send_keys(self.password)
        wait()

    def _submit_login(self):
        signin_xpath = '//*[@id="react_root"]/div/div[1]/div[2]/div/div[2]/div/div/form/footer/div/button'
        signin_btn = self.driver.find_element_by_xpath(signin_xpath)
        signin_btn.click()
        wait(5)

    def is_logged_in(self):
        self.driver.get(f"{self.robinhood_url}/")
        html = self.driver.page_source
        return html.find('Home') > 0 and html.find('Notifications') > 0 and html.find('Account')

    def _initiate_verify_by_sms(self):
        verify_xpath = '//*[@id="react_root"]/div/div[1]/div[2]/div/div[2]/div/div/div/footer/div[1]/button'
        verify_btn = self.driver.find_element_by_xpath(verify_xpath)
        verify_btn.click()
        wait()

    def _get_verify_code(self):
        verify_code = input("Submit verify code here: ")
        return verify_code

    def _enter_verify_code(self, verify_code):
        submit_code_xpath = '//*[@id="react_root"]/div/div[1]/div[2]/div/div[2]/div/div/div/form/input'
        submit_code_tb = self.driver.find_element_by_xpath(submit_code_xpath)
        submit_code_tb.send_keys(verify_code)
        wait()

    def _submit_verify_button(self):
        confirm_xpath = '//*[@id="react_root"]/div/div[1]/div[2]/div/div[2]/div/div/div/form/footer/div[2]/button'
        confirm_btn = self.driver.find_element_by_xpath(confirm_xpath)
        confirm_btn.click()

    def _verify_by_sms(self):
        self._initiate_verify_by_sms()
        verify_code = self._get_verify_code()
        self._enter_verify_code(verify_code)
        self._submit_verify_button()

    def _verify_by_mfa(self):
        mfa_tb = find_element(self.driver, 'input', 'mfa_code', 'name')
        mfa_code = input("Please Open Your MFA App and type in 6 digit code:")
        mfa_tb.send_keys(mfa_code)

        wait(5)
        footer = self.driver.find_element_by_tag_name('footer')
        continue_btn = find_form_element(footer, 'button', 'type', 'submit', 'Continue')
        continue_btn.click()

    def _navigate_to_login(self):
        login_url = f"{self.robinhood_url}/login"
        log_msg(f"Going to open: {login_url}")
        self.driver.get(login_url)

    def login(self):
        if self.is_logged_in():
            log_msg("User is already logged in!")
            return

        self._navigate_to_login()
        self._enter_username()
        self._enter_password()
        self._submit_login()

        html = self.driver.page_source

        should_verify = html.find('Verify Your Identity') > 0
        should_mfa = html.find('Two-Factor Authentication')

        if should_verify:
            log_msg("Looks like you have not configured MFA, using verify by sms")
            self._verify_by_sms()
        elif should_mfa:
            log_msg("Looks like you have Two Factor Authentication Enabled. Initating MFA Flow")
            self._verify_by_mfa()

        html = self.driver.page_source
        output = html.find('Home') > 0 and html.find('Notifications') > 0 and html.find('Account')
        if output:
            log_msg("Congratulations, you have successfully logged in!!!")
        else:
            log_msg("Something Happened, you do not seem to be login. Please check!")
            # todo should send an alert here

        return output



class _TradeStock(object):

    def __init__(self, driver, use_limit_order):
        self.driver = driver
        self.use_limit_order = use_limit_order
        self._form = None

        self._buy_three_dots_xpath = '//*[@id="react_root"]/div/main/div[2]/div/div/div/main/div[2]/div[2]/div/form/header/div/div[2]/div/div/div'
        self._buy_three_dots_xpath = '//*[@id="react_root"]/div/main/div[2]/div/div/div/main/div[2]/div[2]/div/form/header/div/div[2]/div/div'
        self._buy_three_dots_dropdown_limit_order_menu_xpath = '//*[@id="react_root"]/div/main/div[2]/div/div/div/main/div[2]/div[2]/div/form/div[2]/div[1]/div/div/div/a[2]'

        self._sell_three_dots_xpath = '//*[@id="react_root"]/div/main/div[2]/div/div/div/main/div[2]/div[2]/div/form/header/div/div[2]/div/div/div'
        self._sell_three_dots_dropdown_limit_order_menu_xpath = '//*[@id="react_root"]/div/main/div[2]/div/div/div/main/div[2]/div[2]/div/form/div[2]/div[1]/div/div/div/a[2]'

        self._select_sell_menu_xpath = '//*[@id="react_root"]/div/main/div[2]/div/div/div/main/div[2]/div[2]/div/form/header/div/div[1]/div/div[2]/div/h3'

    def _navigate(self, symbol):

        symbol_url = f"https://robinhood.com/stocks/{symbol}"
        log_msg(f"Navigating to {symbol_url}")
        self.driver.get(symbol_url)

    def _load_form_element(self):
        self._form = find_element(self.driver, 'form', 'OrderForm')
        return self._form

    def _select_limit_order(self, buy=False, sell=False):

        if not buy and not sell:
            raise ValueError("Incorrect order type")

        three_dots_xpath = self._buy_three_dots_xpath
        three_dots_limit_order_menu_xpath = self._buy_three_dots_dropdown_limit_order_menu_xpath

        if sell:
            self._select_sell_menu()
            three_dots_xpath = self._sell_three_dots_xpath
            three_dots_limit_order_menu_xpath = self._sell_three_dots_dropdown_limit_order_menu_xpath

        log_msg(f"SELL: {sell} BUY: {buy} ...={three_dots_xpath}")
        three_dots_el = self.driver.find_element_by_xpath(three_dots_xpath)
        three_dots_el.click()

        wait(1)
        three_dots_dropdown_limit_order_menu_href = self.driver.find_element_by_xpath(three_dots_limit_order_menu_xpath)
        three_dots_dropdown_limit_order_menu_href.click()

    def _enter_limit_price(self, limit_price):
        limit_price_tb = find_form_element(self._form, 'input', 'name', 'price')
        limit_price = limit_price or limit_price_tb.get_attribute("value").replace('$', '')
        clear_text(limit_price_tb, len(limit_price))
        limit_price_tb.send_keys(limit_price)
        wait(5)

    def _enter_quantity(self, quantity: int):
        number_of_shares_tb = find_form_element(self._form, 'input', 'name', 'quantity')
        number_of_shares_to_buy = quantity
        number_of_shares_tb.send_keys(number_of_shares_to_buy)
        wait(1)

    def _review_order(self):
        review_btn = find_form_element(self._form, 'button', 'type', element_text='Review Order')
        review_btn.click()
        log_msg("Order has been reviewed")
        wait(5)

    def _submit_order(self, confirm=False):
        if confirm:
            answer = input("You are going to submit an order, enter YES to proceed")
            if answer.lower() != 'yes':
                log_msg("You did not say YES, skipping order!!!!")
                return

        submit_btn_data_testid = 'OrderFormControls-Submit'
        submit_btn = find_element(self.driver, 'button', submit_btn_data_testid)
        submit_btn.click()
        wait(5)
        self._done()

    def _select_sell_menu(self):
        sell_menu_link = self.driver.find_element_by_xpath(self._select_sell_menu_xpath)
        sell_menu_link.click()

    def _order(self, symbol: str, quantity: int, buy=False, sell=False,
               limit_price: float = None, confirm: bool = False):

        if not buy and not sell:
            raise ValueError("You must provide buy=True OR sell=True")

        self._navigate(symbol)
        self._load_form_element()

        if self.use_limit_order:
            self._select_limit_order(buy=buy, sell=sell)
            self._enter_limit_price(limit_price)

        self._enter_quantity(quantity)
        self._submit_order(confirm=confirm)

    def _done(self):
        done_btn = find_done_button(self.driver, 'div', 'OrderFormReceipt')
        done_btn.click()

    def buy(self, symbol, quantity, limit_price: float = None, confirm: bool = False):
        self._order(symbol, quantity, buy=True, sell=False,
                    limit_price=limit_price,
                    confirm=confirm)

    def sell(self, symbol, quantity, limit_price: float = None, confirm: bool = False):
        self._order(symbol, quantity, buy=False, sell=True,
                    limit_price=limit_price,
                    confirm=confirm)


class Robinhood(object):

    def __init__(self, session_id=None, port=9515):
        self.driver = webdriver.Remote(f"http://127.0.0.1:{port}")
        if session_id and len(session_id) > 0:
            self.driver.close()
            self.driver.session_id = session_id
        self.robinhood_url = 'https://robinhood.com'

    def login(self, username, password):
        log_msg("Going to login the user")
        _LoginUser(self.driver, self.robinhood_url, username, password).login()

    def sell(self, symbol, quantity, use_limit: bool = True,
             limit_price: float = None, confirm: bool = False):

        _TradeStock(self.driver, use_limit_order=use_limit,).sell(
            symbol, quantity, limit_price=limit_price, confirm=confirm
        )

    def buy(self, symbol, quantity, use_limit: bool = True,
            limit_price: float = None, confirm: bool = False):

        _TradeStock(self.driver, use_limit_order=use_limit).buy(
            symbol, quantity, limit_price=limit_price, confirm=confirm
        )


def main():
    import getpass

    username = input("Enter Robinhood username: ")
    password = getpass.getpass("Enter password:")
    session_id = input("Please enter existing browser session_id (press enter for null): ")

    r = Robinhood(session_id)

    r.login(username, password)


if __name__ == '__main__':
    sys.exit(main())