from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json


def determine_type(k):
    if k["coming_soon"]:
        return "Coming Soon"
    if k["alt_title"] and k["title"]:
        try:
            z = (
                k["alt_title"].split("C", 1)[0]
                + "C"
                + k["alt_title"].split("C", 1)[1].split(" ", 1)[0]
            )
            return z
        except Exception:
            return "<MISSING>"
    else:
        return "<MISSING>"


def para(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    allscripts = soup.find_all("script", {"type": "text/javascript"})
    thescript = ""
    for script in allscripts:
        if "jQuery.extend(Drupal.settings" in script.text:
            thescript = script.text

    thescript = (
        thescript.split("jQuery.extend(Drupal.settings,", 1)[1].split("});", 1)[0] + "}"
    )
    son = json.loads(thescript)

    for rec in son["gohealth_regional_landing_pages"]["clinics"]:
        yield rec


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.gohealthuc.com/#center-locator-anchor"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")
    links = soup.find("select", {"id": "regionSelect"})
    links = links.find_all("option", {"value": lambda x: x and "/" in x})

    pages = []
    for i in links:
        pages.append("https://www.gohealthuc.com" + i["value"])

    lize = utils.parallelize(
        search_space=pages,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for county in lize:
        for entry in county:
            if (
                entry["title"] != "Virtual Visit"
                and "virtual-visit" not in entry["link"]
                and "covid-19" not in entry["link"]
            ):
                entry["type"] = determine_type(entry)
                yield entry

    logzilla.info(f"Finished grabbing data!!")  # noqa


def human_hours(x):
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    i = 0
    hours = []
    for i in x:
        hours.append(
            str(
                days[int(i["day"])]
                + ": "
                + str(int(i["starthours"]) / 100)
                + ":"
                + str(int(i["starthours"]) % 100)
                + " - "
                + str(int(i["endhours"]) / 100)
                + ":"
                + str(int(i["endhours"]) % 100)
            )
        )

    return "; ".join(hours)


def scrape():
    url = "https://www.gohealthuc.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["link"], value_transform=lambda x: "https://www.gohealthuc.com" + x
        ),
        location_name=sp.MappingField(
            mapping=["title"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        latitude=sp.MappingField(
            mapping=["geolocation", "lat"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        longitude=sp.MappingField(
            mapping=["geolocation", "lon"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        street_address=sp.MappingField(
            mapping=["address", "thoroughfare"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        city=sp.MappingField(
            mapping=["address", "locality"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        state=sp.MappingField(
            mapping=["address", "administrative_area"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=sp.MappingField(
            mapping=["address", "postal_code"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        country_code=sp.MappingField(
            mapping=["address", "country"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        phone=sp.MappingField(
            mapping=["phone"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        store_number=sp.MappingField(
            mapping=["clockwise_id"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours"], raw_value_transform=human_hours
        ),
        location_type=sp.MappingField(
            mapping=["type"], value_transform=lambda x: x.replace("None", "<MISSING>")
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
