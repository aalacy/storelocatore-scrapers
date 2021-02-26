from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json


def form_url(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    api_url = "https://sls-api-service.sweetiq-sls-production-west.sweetiq.com/"

    scripts = soup.find_all("script")
    theScript = ""
    for i in scripts:
        if "REDUX_STATE" in i.text:
            theScript = i.text
    theScript = json.loads(
        str(theScript.split("REDUX_STATE__ = ", 1)[1].rsplit(";", 1)[0])
    )
    ids = []
    for i in theScript["dataLocations"]["collection"]["features"]:
        ids.append(str(i["properties"]["id"]))

    api_url = api_url + theScript["dataSettings"]["storeLocatorId"]
    api_url = api_url + "/locations-details?locale=en_US&ids="
    api_url = api_url + "%2C".join(ids) + "&clientId="
    api_url = api_url + theScript["dataSettings"]["clientId"] + "&cname="
    api_url = api_url + theScript["dataSettings"]["cname"]

    return api_url


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = form_url("https://locations.davidstea.com")
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()
    for i in son["features"]:
        if not i["properties"]["isPermanentlyClosed"]:
            yield i
    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    x = x.replace("None", "")
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def human_hours(x):
    week = []
    for i in list(x):
        day = []
        for j in x[i]:
            day.append("-".join(j))
        if len(day) == 0:
            day = "Closed"
        else:
            day = " & ".join(day)
        week.append(i + ": " + day)
    return "; ".join(week)


def scrape():
    url = "https://locations.davidstea.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["properties", "slug"],
            value_transform=lambda x: url + x,
        ),
        location_name=sp.MappingField(mapping=["properties", "name"]),
        latitude=sp.MappingField(
            mapping=["geometry", "coordinates", 1],
        ),
        longitude=sp.MappingField(
            mapping=["geometry", "coordinates", 0],
        ),
        street_address=sp.MultiMappingField(
            mapping=[["properties", "addressLine1"], ["properties", "addressLine2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["properties", "city"],
        ),
        state=sp.MappingField(
            mapping=["properties", "province"],
        ),
        zipcode=sp.MappingField(
            mapping=["properties", "postalCode"],
        ),
        country_code=sp.MappingField(
            mapping=["properties", "country"],
        ),
        phone=sp.MappingField(
            mapping=["properties", "phoneNumber"],
        ),
        store_number=sp.MappingField(
            mapping=["properties", "id"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["properties", "hoursOfOperation"], raw_value_transform=human_hours
        ),
        location_type=sp.MappingField(
            mapping=["properties", "categories"],
            raw_value_transform=lambda x: ", ".join(x),
        ),
        raw_address=sp.MissingField(),
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
