from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json5


def get_locations(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")
    theScript = ""
    allScripts = soup.find_all("script", {"type": "text/javascript"})
    for script in allScripts:
        if "var locations" in script.text:
            theScript = script.text

    theScript = json5.loads(
        "{ data: ["
        + str(theScript.split("var locations = [ ", 1)[1].rsplit(",  ];", 1)[0])
        + ",  ]}"
    )
    # length 44
    theScript = theScript["data"]

    stores = soup.find("div", {"class": "locations"}).find_all(
        "div", {"class": "alocation"}
    )
    # length 44
    for i in range(len(stores)):
        k = {}
        js_data = theScript[i]
        bs_data = list(stores[i].stripped_strings)
        if len(bs_data) == 6:
            k["lat"] = js_data["lat"] if js_data["lat"] else ""
            k["lon"] = js_data["lng"] if js_data["lng"] else ""
            k["storeno"] = bs_data[0]
            k["type"] = bs_data[1]
            k["raw"] = bs_data[2]
            k["phone"] = bs_data[-2]

            nice = k["raw"].split(",")
            addressData = []
            for i in nice:
                addressData.append(i.strip())

            k["address"] = addressData[0]

            k["city"] = addressData[1]
            k["state"] = addressData[2].split(" ")[0]
            k["zip"] = addressData[2].split(" ")[1]
            k["country"] = ""
        else:
            k["lat"] = js_data["lat"] if js_data["lat"] else ""
            k["lon"] = js_data["lng"] if js_data["lng"] else ""
            k["storeno"] = bs_data[0]
            k["raw"] = bs_data[1]

            nice = k["raw"].split(",")
            addressData = []
            for i in nice:
                addressData.append(i.strip())

            k["address"] = addressData[0]

            k["city"] = addressData[1]
            k["state"] = addressData[2].split(" ")[0]
            k["zip"] = addressData[2].split(" ")[1]
            k["country"] = ""
        yield k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://minutemanfoodmart.pairsite.com/?page_id=155"
    son = get_locations(url)
    for i in son:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def scrape():
    url = "https://www.minutemanfoodmart.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MissingField(),
        location_name=sp.MissingField(),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lon"],
        ),
        street_address=sp.MappingField(
            mapping=["address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["zip"],
        ),
        country_code=sp.MappingField(mapping=["country"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["storeno"],
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(mapping=["type"], is_required=False),
        raw_address=sp.MappingField(
            mapping=["raw"],
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
