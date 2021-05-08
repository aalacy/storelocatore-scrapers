import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import json
from sglogging import sglog

driver = SgSelenium().chrome()
log = sglog.SgLogSetup().get_logger(logger_name="www.fastsigns.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
all = []


def fetch_data():
    driver.get("https://www.fastsigns.com/worldwide")
    driver.find_element_by_xpath(
        "//select[@name='DataTables_Table_0_length']/option[5]"
    ).click()

    soup = BeautifulSoup(driver.page_source, "html.parser")
    trs = soup.find_all("tr")
    del trs[0]

    for tr in trs:
        tds = tr.find_all("td")
        country = tds[-1].text.strip()
        if (country == "US" or country == "CA") and "coming soon" not in tds[
            0
        ].text.lower():
            url = tds[0].find("a").get("href")
            if "https://www.fastsigns.com/" not in url:
                url = "https://www.fastsigns.com" + url

            log.info(url)

            try:
                res = session.get(url)
            except:
                res = session.get(url)
            soup = BeautifulSoup(res.text, "html.parser")

            jso = soup.find("input", {"id": "CookieValue"}).get("value")
            js = json.loads(jso.replace("%20", " "))

            loc = js["SiteDesignator"]
            phone = js["Phone"]
            if phone.strip() == "":
                try:
                    phone = re.findall(r'"telePhone": "([^"]+)"', str(soup))[0]
                except:
                    phone = "<MISSING>"

            tim = js["WeekHours"] + ", " + js["SatHours"] + ", " + js["SunHours"]

            if tim.replace(",", "").strip() == "":
                try:
                    tim = re.findall(r'"openingHours": "([^"]+)"', str(soup))[0]
                except:
                    tim = "<MISSING>"
            addr = js["Address"].replace("|", "").strip().split(",")
            sz = addr[-1].strip().split(" ")
            try:
                zip = re.findall(r'"postalCode": "([^"]+)"', str(soup))[0]
            except:
                if country == "CA":
                    zip = re.findall(r"[A-Z][0-9][A-Z] *[0-9][A-Z][0-9]", addr[-1])[0]
                else:
                    zip = sz[-1]

            state = sz[0]
            del addr[-1]
            city = addr[-1]
            del addr[-1]
            try:
                street = re.findall(
                    r'"streetAddress": "Street: (.*), City:', str(soup)
                )[0]
            except:
                street = ",".join(addr)

            try:
                lat = re.findall(r'"latitude": "([^"]+)"', str(soup))[0]
            except:
                lat = "<MISSING>"

            try:
                long = re.findall(r'"longitude": "([^"]+)"', str(soup))[0]
            except:
                long = "<MISSING>"

            all.append(
                [
                    "https://www.fastsigns.com",
                    loc.replace("%c2%ae", ""),
                    street,
                    city.strip(),
                    state,
                    zip,
                    country,
                    url.strip().strip("/").split("/")[-1].split("-")[0],  # store #
                    phone,  # phone
                    "<MISSING>",  # type
                    lat,  # lat
                    long,  # long
                    tim.replace("%e2%80%93", "-"),  # timing
                    url,
                ]
            )
    return all


def scrape():
    data = fetch_data()
    write_output(data)
    driver.quit()


scrape()
