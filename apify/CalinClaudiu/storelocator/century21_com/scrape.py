from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def para(chunk):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(chunk["url"], headers=headers)
    if str(son) != "<Response [200]>":
        raise Exception(
            "Sorry, this url\n", chunk["url"], "\nBroke the crawler with response:", son
        )

    soup = b4(son.text, "lxml")

    data = soup.find("div", {"id": "PageFrame"})

    k = {}

    k["CustomUrl"] = chunk["url"]

    try:
        k["Latitude"] = data.find("meta", {"itemprop": "latitude"})["content"]
    except:
        k["Latitude"] = "<MISSING>"

    try:
        k["Longitude"] = data.find("meta", {"itemprop": "longitude"})["content"]
    except:
        k["Longitude"] = "<MISSING>"

    try:
        k["Name"] = data.find("div", {"class": "officeName"}).text.strip()
    except:
        k["Name"] = "<MISSING>"

    try:
        k["Address"] = chunk["data"].find_all("div", {"class": "office-address"})
        h = []
        for i in k["Address"]:
            h.append(i.text.strip())
        k["Address"] = ", ".join(h)

    except:
        k["Address"] = "<MISSING>"

    try:
        k["City"] = data.find("span", {"itemprop": "addressLocality"}).text.strip()
    except:
        k["City"] = "<MISSING>"

    try:
        k["State"] = data.find("span", {"itemprop": "addressRegion"}).text.strip()
    except:
        k["State"] = "<MISSING>"

    try:
        k["Zip"] = data.find("span", {"itemprop": "postalCode"}).text.strip()
    except:
        k["Zip"] = "<MISSING>"

    try:
        k["Phone"] = data.find("meta", {"itemprop": "telephone"})["content"].strip()
        k["Phone"] = k["Phone"].replace("+1.", "").replace(".", "")
    except:
        k["Phone"] = "<MISSING>"

    k["OpenHours"] = "<MISSING>"

    try:
        k["IsActive"] = data.find("meta", {"itemprop": "legalName"})["content"].strip()
    except:
        k["IsActive"] = "<MISSING>"

    try:
        k["Number"] = data.find("input", {"id": "TRACKING_OFFICE_ID"})["value"]

    except:
        k["Number"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.century21.com/officesearch-async?lid=S"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }

    # https://www.century21.com/officesearch-async?lid=SCA&s=0&r=10000
    # SCA = State- California

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    # thanks jeff https://gist.github.com/JeffPaine/3083347

    session = SgRequests()
    chunks = []
    k = []
    identities = set()
    for i in states:
        logzilla.info(f"Total stores found: {len(k)}\n")
        logzilla.info(f"Grabbing state: {i}")
        son = session.get(url + i + "&s=0&r=10000", headers=headers)
        soup = b4(son.text, "lxml")
        count = int(soup.find("input", {"type": True, "id": "numResults"})["value"])
        logzilla.info(f"Found {count} offices for state: {i}.")
        if count > 0:
            chunks = soup.find_all(
                "div",
                {
                    "class": True,
                    "data-link": True,
                    "data-usagetrack": True,
                    "data-id": True,
                    "data-latitude": True,
                    "data-longitude": True,
                },
            )
            son = {}
            for j in chunks:
                son = {}
                son["data"] = j
                son["url"] = j["data-link"]
                if son["url"] not in identities:
                    identities.add(son["url"])
                    son["url"] = "https://www.century21.com" + son["url"]
                    k.append(son)

    lize = utils.parallelize(
        search_space=k,
        fetch_results_for_rec=para,
        max_threads=15,
        print_stats_interval=15,
    )

    for i in lize:
        yield i
    lize = "Finished grabbing data!!"
    logzilla.info(f"{lize}")


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def scrape():
    url = "https://www.century21.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["CustomUrl"]),
        location_name=MappingField(
            mapping=["Name"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        latitude=MappingField(mapping=["Latitude"]),
        longitude=MappingField(mapping=["Longitude"]),
        street_address=MappingField(mapping=["Address"], value_transform=fix_comma),
        city=MappingField(
            mapping=["City"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        state=MappingField(
            mapping=["State"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        zipcode=MappingField(
            mapping=["Zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MissingField(),
        phone=MappingField(
            mapping=["Phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["Number"]),
        hours_of_operation=MappingField(mapping=["OpenHours"], is_required=False),
        location_type=MappingField(mapping=["IsActive"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="century21.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
