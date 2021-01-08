from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from bs4 import BeautifulSoup as b4


def parse_dealer(k):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "Accept": "application/json",
    }

    session = SgRequests()
    if k["page_url"] == "<MISSING>":
        k["hours"] = "<MISSING>"
        k["lat"] = "<MISSING>"
        k["lon"] = "<MISSING>"
        return k

    k["page_url"] = "http:" + k["page_url"]
    page = session.get(
        k["page_url"],
        headers=headers,
    )

    soup = b4(page.text, "lxml")

    try:
        h = soup.find("div", {"class": lambda x: x and "intro-opening-times" in x})
        h = h.find_all("p")
        k["hours"] = []
        for i in h:
            k["hours"].append(i.text)

        k["hours"] = "; ".join(k["hours"])
    except Exception:
        k["hours"] = "<MISSING>"
    if len(k["hours"]) < 2:
        k["hours"] = "<MISSING>"
    if k["hours"] == "<MISSING>":
        try:
            h = soup.find("div", {"class": lambda x: x and "intro-opening-times" in x})
            h = list(h.find("tbody").stripped_strings)
            j = 0
            while j < len(h):
                h[j] = h[j] + ": " + h[j + 1]
                h.pop(j + 1)
                j += 1
            k["hours"] = "; ".join(h)
        except:
            k["hours"] = "<MISSING>"

    try:
        k["lat"] = soup.find("div", {"id": "gm-contact-us"})["data-lat"]
    except Exception:
        k["lat"] = "<MISSING>"

    try:
        k["lon"] = soup.find("div", {"id": "gm-contact-us"})["data-lng"]
    except Exception:
        k["lon"] = "<MISSING>"

    try:
        k["name"] = soup.find("a", {"id": "dealer_name"}).text.strip()
    except Exception:
        k["name"] = "<MISSING>"

    return k


def get_url(soup):
    k = {}
    moresoup = soup

    soup = soup.find("div", {"class": lambda x: x and "dealer_details" in x})
    links = soup.find_all("a")
    k["page_url"] = "<MISSING>"
    for i in links:
        if "ebsite" in i.text:
            k["page_url"] = i["href"]

    try:
        addr = list(soup.find("address").stripped_strings)
    except Exception:
        addr = "<MISSING>"

    try:
        k["address"] = addr[0]
        addr.pop(0)
        while any(i.isdigit() for i in addr[0]):
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

    if len(addr) > 0:
        if k["region"] != "<MISSING>":
            while (len(addr)) > 0:
                k["region"] = k["region"] + " - " + k["zip"]
                k["zip"] = addr[0]
                addr.pop(0)
        else:
            raise Exception("something quite impossible happened")

    try:
        k["phone"] = soup.find(
            "a", {"href": lambda x: x and x.startswith("tel:")}
        ).text.strip()
    except Exception:
        k["phone"] = "<MISSING>"

    try:
        k["id"] = moresoup.find("form", {"id": True}).find(
            "input", {"name": "dealer_contact[dealer_id]"}
        )["value"]
    except Exception:
        k["id"] = "<MISSING>"

    try:
        k["name"] = soup.find("h3").text.strip()
    except Exception:
        k["name"] = "<MISSING>"

    return k


def parse_page(soup):
    k = {}
    soup = b4(soup, "lxml")
    results = soup.find("div", {"id": "search_block"})
    results = results.find(
        "div", {"class": lambda x: x and "dealer_search_results" in x}
    )
    results = results.find("div")
    raw_dealers = results.find_all("div", recursive=False)
    k["count"] = len(raw_dealers)
    if k["count"] > 0:
        k["entities"] = []
        for i in raw_dealers:
            k["entities"].append(get_url(i))

    return k


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "Accept": "application/json",
    }

    session = SgRequests()
    search = DynamicZipSearch(country_codes=[SearchableCountries.BRITAIN])
    identities = set()
    final_results = []
    tot = 0
    for coord in search:
        now = 0
        page = session.get(
            str(
                "https://mg.co.uk/dealers/?search%5Btext%5D="
                + str(coord).replace(" ", "+")
            ),
            headers=headers,
        )

        results = parse_page(page.text)
        if results["count"] > 0:
            for i in results["entities"]:
                if i["page_url"] == "<MISSING>":
                    now += 1
                    tot += 1
                    final_results.append(i)
                elif i["page_url"] not in identities:
                    now += 1
                    tot += 1
                    identities.add(i["page_url"])
                    final_results.append(i)

        logzilla.info(
            f"{coord} | remaining: {search.items_remaining()} | found: {now} | Total: {tot} "
        )

    lize = utils.parallelize(
        search_space=final_results,
        fetch_results_for_rec=parse_dealer,
        max_threads=20,
        print_stats_interval=20,
    )

    for i in lize:
        yield i
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
    url = "https://www.mg.co.uk/"
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
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
            value_transform=lambda x: x.replace("/", ":")
            .replace("&nbsp;", " ")
            .replace("Â", " "),
            is_required=False,
        ),
        location_type=sp.MissingField(),
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
