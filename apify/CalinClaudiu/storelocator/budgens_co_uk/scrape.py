from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def para(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    k = {}
    k["link"] = url
    session = SgRequests()
    try:
        son = session.get(url, headers=headers)
    except Exception:
        k["hours"] = "<INACCESSIBLE>"
        k["title"] = "<INACCESSIBLE>"
        k["latitude"] = "<INACCESSIBLE>"
        k["longitude"] = "<INACCESSIBLE>"
        k["address"] = "<INACCESSIBLE>"
        k["city"] = "<INACCESSIBLE>"
        k["state"] = "<INACCESSIBLE>"
        k["zip"] = "<INACCESSIBLE>"
        k["country"] = "<INACCESSIBLE>"
        k["telephone"] = "<INACCESSIBLE>"
        k["id"] = "<INACCESSIBLE>"
        k["type"] = "<INACCESSIBLE>"
        return k

    soup = b4(son.text, "lxml")
    try:
        k["hours"] = list(
            soup.find("div", {"id": "storeOpeningTimes"}).find("tbody").stripped_strings
        )
        h = []
        while len(k["hours"]) > 0:
            h.append(k["hours"][0] + " " + k["hours"][1])
            k["hours"].pop(0)
            k["hours"].pop(0)
        k["hours"] = "; ".join(h)

    except Exception:
        k["hours"] = "<MISSING>"

    try:
        k["title"] = soup.find("meta", {"name": "geo.placename"})["content"]
    except Exception:
        k["title"] = "<MISSING>"

    try:
        k["latitude"] = soup.find("meta", {"property": "og:latitude"})["content"]
    except Exception:
        k["latitude"] = "<MISSING>"

    try:
        k["longitude"] = soup.find("meta", {"property": "og:longitude"})["content"]
    except Exception:
        k["longitude"] = "<MISSING>"

    try:
        k["address"] = soup.find("meta", {"property": "og:street_address"})["content"]
    except Exception:
        k["address"] = "<MISSING>"

    try:
        k["city"] = soup.find("meta", {"property": "og:locality"})["content"]
    except Exception:
        k["city"] = "<MISSING>"

    try:
        k["state"] = soup.find("meta", {"property": "og:region"})["content"]
    except Exception:
        k["state"] = "<MISSING>"

    try:
        k["zip"] = soup.find("meta", {"property": "og:postal_code"})["content"]
    except Exception:
        k["zip"] = "<MISSING>"

    try:
        k["country"] = soup.find("meta", {"name": "geo.region"})["content"]
    except Exception:
        k["country"] = "<MISSING>"

    try:
        k["telephone"] = soup.find("meta", {"property": "og:phone_number"})["content"]
    except Exception:
        k["telephone"] = "<MISSING>"

    k["id"] = "<MISSING>"

    try:
        k["type"] = soup.find("meta", {"property": "og:type"})["content"]
    except Exception:
        k["type"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")
    url = "https://www.budgens.co.uk/sitemap.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    results = list(i.text for i in soup.find_all("loc") if "our-stores" in i.text)
    lize = utils.parallelize(
        search_space=results,
        fetch_results_for_rec=para,
        max_threads=20,
        print_stats_interval=20,
    )
    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        x = x.split(",")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def scrape():
    url = "https://www.budgens.co.uk/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["link"]),
        location_name=sp.MappingField(
            mapping=["title"], is_required=False, part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(
            mapping=["address"],
            is_required=False,
            value_transform=fix_comma,
            part_of_record_identity=True,
        ),
        city=sp.MappingField(
            mapping=["city"],
            is_required=False,
            value_transform=lambda x: x.replace("NULL", "<MISSING>"),
            part_of_record_identity=True,
        ),
        state=sp.MappingField(
            mapping=["state"], is_required=False, part_of_record_identity=True
        ),
        zipcode=sp.MappingField(
            mapping=["zip"], is_required=False, part_of_record_identity=True
        ),
        country_code=sp.MappingField(mapping=["country"], is_required=False),
        phone=sp.MappingField(mapping=["telephone"]),
        store_number=sp.MappingField(mapping=["id"]),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(mapping=["type"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
