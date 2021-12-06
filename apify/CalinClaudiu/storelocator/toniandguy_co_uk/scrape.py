from sgscrape import simple_scraper_pipeline as sp
from sgscrape import sgpostal as parser
from sglogging import sglog

from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def para(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    try:
        soup = b4(
            SgRequests.raise_on_err(session.get(url, headers=headers)).text, "lxml"
        )
    except Exception:
        return False

    k = {}
    k["url"] = url
    raw_a = soup.find("address").text.strip()
    k["rawa"] = raw_a
    parsed = parser.parse_address_intl(raw_a)
    k["country"] = parsed.country if parsed.country else "<MISSING>"
    k["address"] = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
    k["address"] = (
        (k["address"] + ", " + parsed.street_address_2)
        if parsed.street_address_2
        else k["address"]
    )
    k["city"] = parsed.city if parsed.city else "<MISSING>"
    k["state"] = parsed.state if parsed.state else "<MISSING>"
    k["zip"] = parsed.postcode if parsed.postcode else "<MISSING>"
    try:
        k["name"] = soup.find("title").text.strip()
    except Exception:
        k["name"] = "<MISSING>"

    try:
        coords = (
            soup.find("a", {"href": lambda x: x and "google.com/maps?q=" in x})["href"]
            .split("google.com/maps?q=", 1)[1]
            .split(",")
        )
    except Exception:
        coords = ["<MISSING>", "<MISSING>"]

    k["lat"] = coords[0]
    k["lng"] = coords[1]

    try:
        k["phone"] = soup.find(
            "a", {"href": lambda x: x and x.startswith("tel:")}
        ).text.strip()
    except Exception:
        k["phone"] = "<MISSING>"

    try:
        k["hours"] = "; ".join(
            list(
                soup.find(
                    "ol", {"class": lambda x: x and "opening-times" in x}
                ).stripped_strings
            )
        )
    except Exception:
        k["hours"] = "<MISSING>"

    return k


def fetch_data():
    para("https://toniandguy.com/salon/phnom-penh")
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://toniandguy.com/sitemap.xml"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    links = soup.find_all("loc")
    pages = []
    for i in links:
        pages.append(i.text.strip())

    lize = utils.parallelize(
        search_space=pages,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for i in lize:
        if i:
            yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://toniandguy.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["url"], part_of_record_identity=True),
        location_name=sp.MappingField(mapping=["name"]),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MappingField(mapping=["address"]),
        city=sp.MappingField(mapping=["city"]),
        state=sp.MappingField(mapping=["state"]),
        zipcode=sp.MappingField(mapping=["zip"]),
        country_code=sp.MappingField(mapping=["country"]),
        phone=sp.MappingField(mapping=["phone"], part_of_record_identity=True),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
            value_transform=lambda x: x.replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " "),
        ),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(
            mapping=["rawa"],
            value_transform=lambda x: x.replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " "),
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
