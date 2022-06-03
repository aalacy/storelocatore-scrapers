from bs4 import BeautifulSoup

from sglogging import sglog

from sgselenium.sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger(logger_name="brookshires.com")

base_link = "https://www.brookshires.com/stores/?coordinates=33.081696254439834,-95.94856100000001&zoom=4"

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


with SgChrome(user_agent=user_agent) as driver:
    driver.get(base_link)
    base = BeautifulSoup(driver.page_source, "lxml")
    log.info(base)
