from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json


def para(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"  # noqa
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    data = soup.find_all("script", {"type": "text/javascript"})
    son = ""
    for i in data:
        if "map_list_data" in i.text:
            son = i.text

    son = son.split("map_list_data = ", 1)[1].rsplit("]", 1)[0] + "]"
    son = json.loads(son)
    for i in son:
        i["hours_sets:primary"] = json.loads(i["hours_sets:primary"])
        yield i


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://stores.burkesoutlet.com/index.m.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"  # noqa
    }

    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    states = []
    cities = []

    logzilla.info(f"Grabbing state links")  # noqa
    for i in soup.find("div", {"class": "no-results"}).find_all(
        "a",
        {"href": True, "class": "ga-link", "data-ga": True, "data-search-term": True},
    ):
        states.append(i["href"].replace("index.m.html", ""))
    logzilla.info(f"Found {len(states)} states \n")  # noqa

    logzilla.info(f"Grabbing city links")  # noqa
    for i in states:
        do = 0
        son = session.get(i, headers=headers)
        soup = b4(son.text, "lxml")
        for j in soup.find("div", {"class": "map-list"}).find_all(
            "a",
            {
                "href": True,
                "class": "ga-link",
                "data-ga": True,
                "data-search-term": True,
            },
        ):
            cities.append(j["href"])
            do += 1
        logzilla.info(f'Found {do} for state: {i.rsplit("/",3)[-2]}')  # noqa

    logzilla.info(f"Found {len(cities)} cities \n")  # noqa

    logzilla.info(f"Grabbing store data")  # noqa

    lize = utils.parallelize(
        search_space=cities,
        fetch_results_for_rec=para,
        max_threads=20,
        print_stats_interval=20,
    )

    for i in lize:
        for j in i:
            yield j

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except Exception:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def pretty_hours(k):
    h = []
    try:
        days = list(k["days"])
        for i in days:
            h.append(
                str(
                    str(i)
                    + ": "
                    + str(k["days"][i][0]["open"])
                    + "-"
                    + str(k["days"][i][0]["close"])
                )
            )
    except Exception:
        h = ["<MISSING>"]

    return "; ".join(h)


def scrape():
    url = "https://www.burkesoutlet.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["url"]),
        location_name=MappingField(
            mapping=["location_name"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lng"]),
        street_address=MultiMappingField(
            mapping=[["address_1"], ["address_2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=MappingField(
            mapping=["city"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        state=MappingField(
            mapping=["region"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        zipcode=MappingField(
            mapping=["post_code"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MissingField(),
        phone=MappingField(
            mapping=["local_phone_pn_dashes"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["fid"]),
        hours_of_operation=MappingField(
            mapping=["hours_sets:primary"],
            raw_value_transform=pretty_hours,
            is_required=False,
        ),
        location_type=MappingField(
            mapping=["location_custom_message"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="burkesoutlet.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
