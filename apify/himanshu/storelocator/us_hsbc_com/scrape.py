import csv
from bs4 import BeautifulSoup as bs
import time
from sgselenium import SgSelenium
from selenium.webdriver.common.keys import Keys
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "http://us.hsbc.com/"
    driver = SgSelenium().firefox()
    driver.firefox_profile.set_preference("browser.formfill.enable", False)
    driver.firefox_profile.set_preference("devtools.jsonview.enabled", False)
    driver.firefox_profile.set_preference("useAutomationExtension", False)
    driver.firefox_profile.set_preference("dom.webdriver.enabled", False)
    zipcodes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=2000,
    )
    addressess = []
    phone = ""
    location_type = ""
    hours_of_operation = ""
    for zipcode in zipcodes:
        try:
            driver.get("https://www.us.hsbc.com/branch-locator/")
            try:
                driver.find_element_by_xpath(
                    "/html/body/main/div[1]/div/section/div/div[3]/button"
                ).click()
            except:
                pass
            try:
                driver.find_element_by_xpath(
                    "/html/body/main/div[1]/div/section/div/div[3]/button"
                ).click()
            except:
                pass
            try:
                for n in range(1, 3):
                    time.sleep(5)
                    if n == 1:
                        driver.find_element_by_xpath(
                            "/html/body/main/div[2]/div/div/div/div/div[1]/div/button[2]"
                        ).click()
                        time.sleep(5)
                        try:
                            driver.find_element_by_xpath(
                                "/html/body/main/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/fieldset/span[2]/label"
                            ).click()
                        except:
                            continue
                        hours_of_operation = "Monday 24 hours Tuesday 24 hours Wednesday 24 hours Thursday 24 hours Friday 24 hours Saturday 24 hours Sunday 24 hours"
                        location_type = "ATM"
                    else:
                        location_type = "Branch"
                        hours_of_operation = "Monday 9:00 - 17:00 Tuesday 9:00 - 17:00 Wednesday 9:00 - 17:00 Thursday 9:00 - 17:00 Friday 9:00 - 17:00 Saturday Closed Sunday Closed"

                    driver.find_element_by_xpath(
                        "/html/body/main/div[2]/div/div/div/div/div[1]/div/div[1]/div[2]/form/input"
                    ).send_keys(str(zipcode))
                    time.sleep(2)
                    driver.find_element_by_xpath(
                        "/html/body/main/div[2]/div/div/div/div/div[1]/div/div[1]/div[2]/form/input"
                    ).send_keys(Keys.RETURN)
                    while True:
                        time.sleep(5)
                        try:
                            driver.find_element_by_xpath(
                                "//*[text()='Show more results']"
                            ).click()
                        except:
                            break
                    soup = bs(driver.page_source, "lxml")
                    names = []
                    for dt in soup.find_all("h2", {"class": "_1521gYSzrNIMk9R-rS4Hur"}):
                        names.append(dt)
                    for index, i in enumerate(names):
                        time.sleep(3)
                        driver.find_element_by_xpath(
                            "/html/body/main/div[2]/div/div/div/div/div[1]/div/ul/li["
                            + str(index + 1)
                            + "]/button/h2"
                        ).click()
                        time.sleep(3)
                        soup = bs(driver.page_source, "lxml")
                        location_name = soup.find(
                            "h2", {"class": "_1521gYSzrNIMk9R-rS4Hur"}
                        ).text
                        try:
                            phone = soup.find(
                                "div", {"class": "_1BVddhgeNL2TGp0jUBgsXb"}
                            ).text
                        except:
                            phone = "<MISSING>"
                        list_data = (
                            str(
                                soup.find(
                                    "div", {"class": "_1X8_uDMy4c2FRiCHTbit6u"}
                                ).find("div", recursive=False)
                            )
                            .split("<button")[0]
                            .replace("<div>", "")
                            .replace("<br/>", "")
                            .split(",")
                        )
                        zipp = list_data[-1]
                        state = list_data[-2].strip()
                        city = list_data[-3]
                        address = " ".join(list_data[:-3])
                        storeno = "<MISSING>"
                        country = "US"
                        lat = (
                            soup.find("a", {"class": "_3VOnY-qV7atMV73oAncmTd"})["href"]
                            .split("origin=")[1]
                            .split("/")[0]
                        )
                        lng = (
                            soup.find("a", {"class": "_3VOnY-qV7atMV73oAncmTd"})["href"]
                            .split("origin=")[1]
                            .split("/")[1]
                            .split("&")[0]
                        )
                        store = []
                        store.append(base_url)
                        store.append(
                            location_name.replace("®", "")
                            if location_name
                            else "<MISSING>"
                        )
                        store.append(address if address else "<MISSING>")
                        store.append(city if city else "<MISSING>")
                        store.append(state if state else "<MISSING>")
                        store.append(zipp if zipp else "<MISSING>")
                        store.append(country if country else "<MISSING>")
                        store.append(storeno if storeno else "<MISSING>")
                        store.append(phone if phone else "<MISSING>")
                        store.append(location_type)
                        store.append(lat if lat else "<MISSING>")
                        store.append(lng if lng else "<MISSING>")
                        store.append(
                            hours_of_operation
                            if hours_of_operation.strip()
                            else "<MISSING>"
                        )
                        store.append("<MISSING>")
                        if str(store[2] + location_type) in addressess:
                            continue
                        addressess.append(str(store[2] + location_type))
                        yield store
                        time.sleep(2)
                        driver.execute_script("window.scroll(0, 0);")
                        time.sleep(2)
                        driver.find_element_by_xpath(
                            "//*[text()='Back to results']"
                        ).click()
                driver.refresh()
            except:
                continue
        except:
            zipcode = zipcodes.__next__()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
