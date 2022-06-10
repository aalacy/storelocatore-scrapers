from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sgpostal import sgpostal as parser


def para(url):

    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    soup = b4(
        session.get("https://www.eskimohut.com" + url, headers=headers).text, "lxml"
    )

    k = {}
    k["status"] = True

    try:
        data = soup.find("div", {"data-lat": True})
    except Exception:
        data = "<MISSING>"

    try:
        addressData = list(soup.find("div", {"id": "1603828934"}).stripped_strings)
    except Exception:
        k["status"] = False
        addressData = "<MISSING>"

    k["page_url"] = "https://www.eskimohut.com" + url

    k["name"] = "<MISSING>"

    try:
        k["latitude"] = data["data-lat"]
        k["longitude"] = data["data-lng"]
    except Exception:
        k["latitude"] = "<MISSING>"
        k["longitude"] = "<MISSING>"

    try:
        k["hours"] = (
            "; ".join(list(soup.find("div", {"id": "1566722847"}).stripped_strings))
            .strip()
            .split("; DELIVERY HOURS")[0]
            .strip()
        )
        if "PLEASE CALL TO CONFIRM HOURS" in k["hours"]:
            k["hours"] = "<MISSING>"
    except Exception:
        k["hours"] = "<MISSING>"

    try:
        h = []
        for i in addressData[-1]:
            if i.isdigit():
                h.append(i)
        k["phone"] = "".join(h)
        addressData.pop(-1)
    except Exception:
        k["phone"] = "<MISSING>"

    noice = " ".join(addressData)
    nice = parser.parse_address_usa(noice)

    k["address"] = nice.street_address_1
    if nice.street_address_2:
        k["address"] = k["address"] + ", " + nice.street_address_2

    k["city"] = nice.city
    k["state"] = nice.state
    k["zip"] = nice.postcode
    k["country"] = nice.country
    k["raw"] = noice

    k["type"] = "<MISSING>"

    if k["type"] == "<MISSING>":
        try:
            k["name"] = soup.find("h2", {"id": "1266783305"}).text.strip()
            if "oming" in k["name"]:
                k["type"] = "Coming Soon"
                try:
                    k["name"] = k["name"].split("(", 1)[0] + k["name"].split(")", 1)[1]
                except Exception:
                    k["name"] = k["name"]
            else:
                k["type"] = "<MISSING>"
        except Exception:
            k["name"] = "<MISSING>"
            k["type"] = "<MISSING>"
        try:
            k["name"] = soup.find("div", {"id": "1092523778"}).text.strip()
        except Exception:
            k["name"] = "<MISSING>"

    return k


def fetch_data():
    para("/houston-westheimer")
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.eskimohut.com/contacts"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")
    pages = soup.find_all("a", {"data-element-type": "dButtonLinkId"})
    h = []
    for i in pages:
        if (
            "google" not in i["href"]
            and i["href"].count("/") == 1
            and "newsletter" not in i["href"]
            and i["href"] != "/"
        ):
            h.append(i["href"])

    pages = h

    lize = utils.parallelize(
        search_space=pages,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for i in lize:
        if i["status"]:
            yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.eskimohut.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(mapping=["name"]),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MappingField(mapping=["address"]),
        city=sp.MappingField(mapping=["city"]),
        state=sp.MappingField(mapping=["state"]),
        zipcode=sp.MappingField(mapping=["zip"]),
        country_code=sp.MappingField(mapping=["country"]),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(mapping=["type"]),
        raw_address=sp.MappingField(mapping=["raw"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Scraper",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
