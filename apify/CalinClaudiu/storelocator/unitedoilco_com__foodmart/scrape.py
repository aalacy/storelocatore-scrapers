from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog

from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def para(k):

    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    son = session.get(k[-1], headers=headers)

    soup = b4(son.text, "lxml")

    try:
        phone = soup.find("div", {"style": "float:left;width:100%;"}).find("h1").text
        h = []
        for i in phone:
            if i.isdigit():
                h.append(i)
        phone = "".join(h)
    except Exception:
        phone = "<MISSING>"

    try:
        typ = soup.find("div", {"style": "float:left;width:100%;"}).find("img")["src"]
        typ = typ.split(".")[-2].split("/")[-1]
    except Exception:
        typ = "<MISSING>"

    k.append(phone)
    k.append(typ)
    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "http://www.unitedoilco.com/locations?brand=foodmart"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).text

    soup = b4(son, "lxml")

    son = {}
    son["stores"] = []
    soup = soup.find("table", {"class": "list-of-station"})
    soup = soup.find_all("tr")
    for i in soup:
        data = list(i.stripped_strings)
        data.pop(-1)
        data.append(i.find("a")["href"])
        son["stores"].append(data)

    lize = utils.parallelize(
        search_space=son["stores"],
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://unitedoilco.com/foodmart"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=[5]),
        location_name=MappingField(mapping=[0]),
        latitude=MissingField(),
        longitude=MissingField(),
        street_address=MappingField(
            mapping=[1],
        ),
        city=MappingField(mapping=[2]),
        state=MappingField(mapping=[3]),
        zipcode=MappingField(
            mapping=[4],
        ),
        country_code=MissingField(),
        phone=MappingField(mapping=[6], is_required=False),
        store_number=MappingField(
            mapping=[5], value_transform=lambda x: x.split("?")[-1]
        ),
        hours_of_operation=MissingField(),
        location_type=MappingField(mapping=[7], is_required=False),
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
