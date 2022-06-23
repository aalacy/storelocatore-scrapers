from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgscrape import simple_utils as utils
import sgpostal.sgpostal as parser

from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def has_no(x):
    if any(i.isdigit() for i in x):
        return True
    if any(i in x for i in ["osed", "ay"]):
        return True
    return False


def para(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    page = session.get(url, headers=headers)
    soup = b4(page.text, "lxml")
    k = {}
    k["url"] = url
    try:
        k["phone"] = []
        ph = soup.find("div", {"class": "phoneInfoBlock"})
        for i in ph.text:
            if i.isdigit():
                k["phone"].append(i)
        k["phone"] = "".join(k["phone"])
    except Exception:
        k["phone"] = "<MISSING>"

    data = soup.find_all("div", {"class": "infoBlockInfo"})
    try:
        k["hours"] = []
        for div in data:
            if "ours" in div.text:
                for string in div.stripped_strings:
                    if has_no(string):
                        k["hours"].append(string)
                break

        k["hours"] = "; ".join(k["hours"])
    except Exception:
        k["hours"] = "<MISSING>"

    try:
        coords = page.text.split("maps?ll=", 1)[1]
        k["lat"] = coords[0]
        k["lng"] = coords[1]
    except Exception:
        k["lat"] = "<MISSING>"
        k["lng"] = "<MISSING>"

    try:
        k["type"] = soup.find("div", {"id": "servicesAvailable"})
        k["type"] = list(k["type"].stripped_strings)
        k["type"].pop(0)
        k["type"] = "; ".join(k["type"])
    except Exception:
        k["type"] = "<MISSING>"

    try:
        addr = soup.find("div", {"class": "addrInfoBlock"}).text
        addr = addr.replace("\n", "").replace("\t", "").replace(",", "")
        k["raw_addr"] = addr
        addr = parser.parse_address_usa(addr)
        k["street_address"] = (
            addr.street_address_1 if addr.street_address_1 else "<MISSING>"
        )
        if addr.street_address_2:
            k["street_address"] = k["street_address"] = +", " + addr.street_address_2
        k["city"] = addr.city if addr.city else "<MISSING>"
        k["state"] = addr.state if addr.state else "<MISSING>"
        k["postcode"] = addr.postcode if addr.postcode else "<MISSING>"
        k["country"] = addr.country if addr.country else "<MISSING>"
    except Exception:
        pass

    try:
        k["name"] = soup.find("h1", {"class": "blue"}).text.strip()
    except Exception:
        k["name"] = "<MISSING>"
    if "providence-lending" in k["url"]:
        k["hours"] = "<MISSING>"
    yield k


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.baycoastbank.com/home/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    links = soup.find("div", {"id": "locationsList"}).find_all("a", {"class": "button"})
    pages = []
    for i in links:
        pages.append(i["href"])
    lize = utils.parallelize(
        search_space=pages,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        for j in i:
            yield j

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.baycoastbank.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MissingField(),
        longitude=sp.MissingField(),
        street_address=sp.MappingField(
            mapping=["street_address"],
            is_required=False,
        ),
        city=sp.MappingField(
            mapping=["city"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["state"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["postcode"],
            part_of_record_identity=True,
            is_required=False,
        ),
        country_code=sp.MappingField(
            mapping=["country"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
            is_required=False,
        ),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(
            mapping=["raw_addr"],
            part_of_record_identity=True,
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
