from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
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
    son = session.get(
        "https://www.bestwestern.co.uk/hotels/" + k["Url"], headers=headers
    )

    soup = b4(son.text, "lxml")

    candidates = soup.find_all("a", {"href": lambda x: x and "tel:" in x})
    h = []
    h.append("<MISSING>")
    h.append("<MISSING>")
    for i in candidates:
        h.append(i["href"].split("tel:")[1].strip())

    k["Phone"] = h[-2]
    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.bestwestern.co.uk/restapi/destinations/county-hotels/hotels?take=5000&skip=0&page=1&pageSize=5000&format=json"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()

    lize = utils.parallelize(
        search_space=son["Items"],
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    x = x.replace("None", "")

    try:
        x = x.split(",")
        for i in x:
            if len(i) > 3:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def scrape():
    url = "https://www.bestwestern.co.uk/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["Url"],
            value_transform=lambda x: "https://www.bestwestern.co.uk/hotels/" + x,
        ),
        location_name=MappingField(mapping=["Name"]),
        latitude=MappingField(
            mapping=["Address", "Longitude"],
        ),
        longitude=MappingField(
            mapping=["Address", "Latitude"],
        ),
        street_address=MultiMappingField(
            mapping=[["Address", "Street"], ["Address", "AddressLine2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=MappingField(mapping=["Address", "City"]),
        state=MissingField(),
        zipcode=MappingField(mapping=["Address", "Zip"]),
        country_code=MappingField(mapping=["Address", "Country"]),
        phone=MappingField(mapping=["Phone"], is_required=False),
        store_number=MappingField(mapping=["PropertyId"]),
        hours_of_operation=MissingField(),
        location_type=MissingField(),
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
