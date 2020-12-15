from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def parse_store(k):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    }

    session = SgRequests()

    page = session.get(
        k["page_url"],
        headers=headers,
    )

    soup = b4(page.text, "lxml")

    try:
        addr = list(soup.find("address").stripped_strings)
        unwanted = [
            "Tel:",
            "Parking",
            "Tube",
            "minute",
            "Car Park",
            "nearest",
            "closest",
            "accessible",
            "easily",
        ]
        poplist = []
        for i, val in enumerate(addr):
            if any(j in val for j in unwanted):
                poplist.append(i)
        topop = len(addr)
        while topop >= 0:
            if topop in poplist:
                addr.pop(topop)
            topop -= 1

    except Exception:
        addr = "<MISSING>"

    try:
        k["address"] = addr[0]
        addr.pop(0)

        while any(i.isdigit() for i in addr[0]) and len(addr[0]) > 8:
            k["address"] = k["address"] + ", " + addr[0]
            addr.pop(0)

        if k["address"] == "Unit 54":
            k["address"] = k["address"] + ", " + addr[0]
            addr.pop(0)
            k["address"] = k["address"] + ", " + addr[0]
            addr.pop(0)
            k["address"] = k["address"] + ", " + addr[0]
            addr.pop(0)
        if k["address"] == "8-9 The Great Hall":
            k["address"] = k["address"] + ", " + addr[0]
            addr.pop(0)
        if k["address"] == "2nd Floor Bentall Centre":
            k["address"] = k["address"] + ", " + addr[0]
            addr.pop(0)

    except Exception:
        k["address"] = "<MISSING>"

    try:
        k["city"] = addr[0]
        addr.pop(0)
    except Exception:
        k["city"] = "<MISSING>"

    try:
        k["region"] = addr[0]
        addr.pop(0)
    except Exception:
        k["region"] = "<MISSING>"

    try:
        k["zip"] = addr[0]
        addr.pop(0)
    except Exception:
        k["zip"] = "<MISSING>"

    if k["zip"] == "<MISSING>" and k["region"] != "<MISSING>":
        k["zip"] = k["region"]
        k["region"] = "<MISSING>"

    if (
        k["zip"] == "<MISSING>"
        and k["region"] == "<MISSING>"
        and k["city"] != "<MISSING>"
    ):
        k["zip"] = k["city"]
        k["city"] = "<MISSING>"

    try:
        k["phone"] = "<MISSING>"
        j = soup.find_all("p")
        for i in j:
            if "hone" in i.text:
                k["phone"] = i.text.strip()
                break
    except Exception:
        k["phone"] = "<MISSING>"

    try:
        k["phone"] = k["phone"].split(":")[-1].strip()
    except Exception:
        k["phone"] = (
            k["phone"]
            .replace("Telephone", "")
            .replace("Phone", "")
            .replace(":", "")
            .strip()
        )
    k["id"] = "<MISSING>"
    k["type"] = "<MISSING>"
    try:
        h = soup.find(
            "div",
            {"class": lambda x: x and all(i in x for i in ["grid__item", "mb-3"])},
        ).find("ul")
        h = h.find_all("li")
        k["hours"] = []
        for i in h:
            k["hours"].append(i.text.strip())

        k["hours"] = "; ".join(k["hours"])
        if "opening soon" in k["hours"]:
            k["hours"] = "<MISSING>"
            k["type"] = "Coming Soon!"
    except Exception:
        k["hours"] = "<MISSING>"

    try:
        k["lat"] = soup.find("div", {"id": "store-map"})["data-latitude"]
        k["lon"] = soup.find("div", {"id": "store-map"})["data-longitude"]
    except Exception:
        k["lat"] = "<MISSING>"
        k["lon"] = "<MISSING>"

    try:

        k["name"] = soup.find("h2").text.strip()
    except Exception:
        k["name"] = "<MISSING>"

    return k


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    }

    session = SgRequests()
    url = "https://www.sofaworkshop.com/pages/stores"
    page = session.get(url, headers=headers)
    soup = b4(page.text, "lxml")

    results = []
    locs = soup.find_all("div", {"class": "store-list__details"})
    for i in locs:
        k = {}
        k["page_url"] = "https://www.sofaworkshop.com/" + i.find(
            "a",
            {
                "class": lambda x: x
                and all(i in x for i in ["btn", "btn--secondary", "btn--small"])
            },
        )["href"]
        results.append(k)

    for i in results:
        yield parse_store(i)

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    x = x.replace("None", "")
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


def fix_colon(x):
    x = x.replace("None", "")
    h = []
    try:
        x = x.split(":")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def scrape():
    url = "https://www.sofaworkshop.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["page_url"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["lon"],
            is_required=False,
        ),
        street_address=sp.MappingField(
            mapping=["address"],
            is_required=False,
        ),
        city=sp.MappingField(
            mapping=["city"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["region"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["zip"],
            is_required=False,
        ),
        country_code=sp.MissingField(),
        phone=sp.MappingField(
            mapping=["phone"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["id"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
            value_transform=lambda x: x.replace("/", ":"),
            is_required=False,
        ),
        location_type=sp.MappingField(
            mapping=["type"],
            is_required=False,
        ),
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
