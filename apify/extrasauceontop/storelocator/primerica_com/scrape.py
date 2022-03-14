from bs4 import BeautifulSoup
from sgrequests import SgRequests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape import simple_scraper_pipeline as sp
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_data():
    got_driver = 0
    linklist = []
    data = []
    p = 0
    url = "http://www.primerica.com/public/locations.html"
    page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    maidiv = soup.find("main")
    mainsection = maidiv.findAll("section", {"class": "content locList"})
    sec = 0
    while sec < 2:
        if sec == 0:
            ccode = "US"
        if sec == 1:
            ccode = "CA"
        rep_list = mainsection[sec].findAll("a")
        for rep in rep_list:

            link = "http://www.primerica.com/public/" + rep["href"]

            if True:
                page1 = session.get(link, headers=headers)
                soup1 = BeautifulSoup(page1.text, "html.parser")
                maindiv = soup1.find("main")
                xip_list = maindiv.findAll("a")

                got_link = 0
                for xip in xip_list:

                    if True:
                        pcode = xip.text

                        statelink = "http://www.primerica.com" + xip["href"]
                        page2 = session.get(statelink, headers=headers, verify=False)
                        soup2 = BeautifulSoup(page2.text, "html.parser")
                        mainul = soup2.find("ul", {"class": "agent-list"})
                        li_list = mainul.findAll("li")
                        if len(li_list) == 0:

                            if got_driver == 0:
                                driver = get_driver(link, "zip-list")
                                got_driver = 1
                                driver.get(statelink)
                                soup2 = BeautifulSoup(driver.page_source, "html.parser")
                                mainul = soup2.find("ul", {"class": "agent-list"})
                                li_list = mainul.findAll("li")

                            else:
                                x = 0
                                while True:
                                    x = x + 1
                                    if x == 10:

                                        break
                                    try:
                                        if got_link == 0:
                                            driver.get(link)

                                        driver.get(statelink)
                                        soup2 = BeautifulSoup(
                                            driver.page_source, "html.parser"
                                        )
                                        mainul = soup2.find(
                                            "ul", {"class": "agent-list"}
                                        )
                                        li_list = mainul.findAll("li")
                                        if len(li_list) == 0:

                                            driver = get_driver(
                                                link, "zip-list", driver=driver
                                            )
                                            driver.get(statelink)
                                            soup2 = BeautifulSoup(
                                                driver.page_source, "html.parser"
                                            )
                                            mainul = soup2.find(
                                                "ul", {"class": "agent-list"}
                                            )
                                            li_list = mainul.findAll("li")

                                        break

                                    except Exception:
                                        continue

                        for m in range(0, len(li_list)):
                            if True:
                                address = ""
                                alink = li_list[m].find("a")

                                title = alink.text
                                alink = alink["href"] + "&origin=customStandard"
                                if alink in linklist:
                                    continue
                                linklist.append(alink)

                                try:
                                    page3 = session.get(
                                        alink, headers=headers, verify=False
                                    )
                                except Exception:
                                    continue

                                soup3 = BeautifulSoup(page3.text, "html.parser")
                                try:
                                    address = soup3.find(
                                        "div", {"class": "officeInfoDataWidth"}
                                    ).text.strip()
                                except Exception:
                                    continue

                                address = address.split("\n")

                                if len(address) > 2:
                                    street = ""
                                    for num in range(len(address) - 1):
                                        part = address[num].strip()
                                        street = street + part + " "

                                    street = street.strip().replace("  ", " ")

                                else:
                                    street = address[0].strip()

                                city = address[-1].split(",")[0]
                                state = address[-1].split(", ")[-1].split(" ")[0]

                                if ccode == "US":
                                    postal = address[-1].split(", ")[-1].split(" ")[-1]
                                    pcode = ""
                                    for character in postal:
                                        if bool(re.search(r"\d", character)) is True:
                                            pcode = pcode + character

                                    if len(pcode) == 9:
                                        pcode = pcode[:-4] + "-" + pcode[-4:]

                                else:
                                    postal = (
                                        address[-1].split(", ")[-1].split(" ")[-2]
                                        + address[-1].split(", ")[-1].split(" ")[-1]
                                    )

                                phone = soup3.find(
                                    "div", {"class": "telephoneLabel"}
                                ).text
                                phone = phone.replace("Office: ", "")
                                phone = phone.replace("Mobile", "")
                                phone = phone.replace(":", "")
                                phone = phone.strip()
                                if len(phone) < 2:
                                    phone = "<MISSING>"
                                if len(street) < 2:
                                    street = "<MISSING>"
                                if len(city) < 2:
                                    city = "<MISSING>"
                                if len(state) < 2:
                                    state = "<MISSING>"
                                if len(pcode) < 2:
                                    pcode = "<MISSING>"
                                if len(phone) < 11:
                                    phone = "<MISSING>"
                                street = street.lstrip().replace(",", "")
                                city = city.lstrip().replace(",", "")
                                state = state.lstrip().replace(",", "")

                                if state == "NF":
                                    state = "NL"
                                if state == "PQ":

                                    state = "QC"
                                if True:
                                    yield {
                                        "locator_domain": "http://www.primerica.com/",
                                        "page_url": alink,
                                        "location_name": title,
                                        "latitude": "<MISSING>",
                                        "longitude": "<MISSING>",
                                        "city": city,
                                        "store_number": "<MISSING>",
                                        "street_address": street,
                                        "state": state,
                                        "zip": pcode,
                                        "phone": phone,
                                        "location_type": "<MISSING>",
                                        "hours": "<MISSING>",
                                        "country_code": ccode,
                                    }

                                    p += 1
        sec += 1
    return data


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
