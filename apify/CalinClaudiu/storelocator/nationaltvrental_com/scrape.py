from sgscrape import simple_scraper_pipeline as sp
from sgscrape import sgpostal as parser
from sglogging import sglog

from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def para(k):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(k["page_url"], headers=headers).text, "lxml")

    try:
        coords = soup.find("div", {"class": "google-maps-link"}).find(
            "a", {"target": True, "jstcache": True, "href": True}
        )["href"]
        coords = coords.split("ll=", 1)[1].split("&", 1)[0].split(",", 1)
    except Exception:
        coords = ["<MISSING>", "<MISSING>"]

    k["lat"] = coords[0]
    k["lng"] = coords[1]

    raw_addrList = []
    addressCandidates = soup.find_all(
        "p", {"style": "font-size:16px", "class": "text-center"}
    )
    for i in addressCandidates:
        if "ddress" in i.text:
            raw_addrList = list(i.stripped_strings)
    raw_addr = []
    i = 0
    length = len(raw_addrList)
    while i < length:
        if "Address" in raw_addrList[i]:
            raw_addrList.pop(i)
            break
    raw_addr = " ".join(raw_addrList)
    k["raw_addr"] = raw_addr
    parsed = parser.parse_address_usa(raw_addr)

    k["country"] = parsed.country if parsed.country else "<MISSING>"
    k["state"] = parsed.state if parsed.state else "<MISSING>"
    k["postcode"] = parsed.postcode if parsed.postcode else "<MISSING>"
    k["city"] = parsed.city if parsed.city else "<MISSING>"
    k["street_address"] = (
        parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
    )
    k["street_address"] = (
        k["street_address"] + ", " + parsed.street_address_2
        if parsed.street_address_2
        else k["street_address"]
    )

    try:
        phone = soup.find("a", {"href": lambda x: x and x.startswith("tel:")})[
            "href"
        ].replace("tel:", "")

    except Exception:
        phone = "<MISSING>"

    k["phone"] = phone

    hours = "<MISSING>"
    hourCandidates = soup.find_all("div", {"class": "row"})
    for i in hourCandidates:
        div = i.find(
            "div",
            {"class": lambda x: x and all(j in x for j in ["col-sm-4", "text-center"])},
        )
        if div:
            h4 = div.find("h4")
            if h4:
                if "ours" in h4.text:
                    hours = list(div.find("p").stripped_strings)
                    hours = "; ".join(hours)
    k["hours"] = hours
    return k


def fetch_data():
    para(
        {
            "page_url": "https://nationaltvrental.com/aurora_mo",
            "title": "Versailles Missouri National TV Sales and Rental",
        }
    )
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://nationaltvrental.com/pay-now"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    pages = []
    links = soup.find("div", {"class": "locations-inpage"}).find_all(
        "div", {"class": "col-sm-12"}
    )
    for i in links:
        data = {}
        sublink = ""
        try:
            sublink = i.find("h2")
            sublink = sublink.find("a", {"href": True, "title": True})
            if len(sublink.attrs) == 2:
                data["page_url"] = str(
                    "https://nationaltvrental.com/" + sublink["href"]
                ).replace(str("/" + sublink["href"]), str(sublink["href"]))
                data["title"] = sublink["title"]
                pages.append(data)
        except Exception:
            continue

    lize = utils.parallelize(
        search_space=pages,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://nationaltvrental.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["page_url"],
        ),
        location_name=sp.MappingField(
            mapping=["title"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["postcode"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
        ),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
        ),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(
            mapping=["raw_addr"],
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
