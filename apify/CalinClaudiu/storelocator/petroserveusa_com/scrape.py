from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog

from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def para(k):

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(k["url"], headers=headers).text, "lxml")

    hours = soup.find(
        "div",
        {"class": "box_cnt"},
    )

    try:
        hours = list(hours.stripped_strings)
        flag = 0
        i = 0
        h = []
        while i < len(hours):
            if any(
                mark in hours[i]
                for mark in ["hours", "day", "ppointment", "emporarily", "Hours"]
            ):
                flag = 1
            if flag == 1:
                h.append(hours[i])
            i = i + 1

        k["hours"] = []
        for i in h:
            if (
                any(
                    mark in i
                    for mark in [
                        "day",
                        "p.m",
                        "a.m",
                        "A.M",
                        "P.M",
                        "Mon",
                        "Fri",
                        "Sat",
                        "Sun",
                        "Tue",
                        "Thur",
                        "Tue",
                        "Wed",
                    ]
                )
                or any(j.isdigit for j in i)
            ):
                k["hours"].append(i)
        k["hours"] = "; ".join(k["hours"])
    except Exception:
        k["hours"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://petroserveusa.com/locations.php"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    stores = soup.find_all(
        "div",
        {"class": "grid_4"},
    )

    son = []

    for i in stores:
        k = {}
        k["phone"] = (
            list(i.find("h5").stripped_strings)[-1].replace("Call: ", "").strip()
        )
        k["url"] = "https://petroserveusa.com/" + i.find("a")["href"]
        k["name"] = i.find("h5").find("span").text.strip()
        try:
            address = list(i.find("p").stripped_strings)
        except Exception:
            address = "<MISSING>"
        typ = " ".join(list(i.stripped_strings))
        k["type"] = "<MISSING>"
        if any(mark in typ for mark in ["OON", "oon", "pening", "PENING"]):
            k["type"] = "Coming Soon"
        if any(mark in typ for mark in ["orporate"]):
            k["type"] = "Corporate Office"

        k["address"] = address[0]
        zipc = []
        address[-1] = list(address[-1])
        while address[-1][-1].isdigit():
            zipc.append(address[-1][-1])
            address[-1].pop(-1)
        k["zip"] = []
        for i in reversed(zipc):
            k["zip"].append(i)
        k["zip"] = "".join(k["zip"])

        address[-1] = "".join(address[-1]).replace(k["zip"], "").strip()

        k["state"] = address[-1].split(" ")[-1].strip()
        address[-1] = address[-1].replace(k["state"], "")

        k["city"] = address[-1].replace(",", "").strip()

        if k["city"] in k["address"] and any(i.isdigit() for i in k["city"]):

            if len(k["city"].split(" ")[-1]) < 3:
                k["city"] = k["city"].split(" ")[-2:-1]
            else:
                k["city"] = k["city"].split(" ")[-1]

            k["address"] = (
                k["address"]
                .replace(k["city"], "")
                .replace(k["state"], "")
                .replace(k["zip"], "")
                .replace(",", "")
            )

        son.append(k)

    lize = utils.parallelize(
        search_space=son,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://petroserveusa.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["url"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MissingField(),
        longitude=MissingField(),
        street_address=MappingField(mapping=["address"]),
        city=MappingField(mapping=["city"]),
        state=MappingField(mapping=["state"]),
        zipcode=MappingField(mapping=["zip"]),
        country_code=MissingField(),
        phone=MappingField(mapping=["phone"]),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=["hours"]),
        location_type=MappingField(mapping=["type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
