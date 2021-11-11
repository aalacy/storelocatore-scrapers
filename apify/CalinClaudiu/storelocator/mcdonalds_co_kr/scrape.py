from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
import sgpostal.sgpostal as parser

# https://mcdonalds.co.kr/kor/store/list.do?page=81&lat=NO&lng=NO&search_options=&searchWord=
# Road in thing means results


def cleanup_this(raw):
    clean = {}
    try:
        coords = raw.find("strong", {"class": "tit"}).find("a")
        clean["lat"], clean["lon"] = (
            coords["href"].split("(", 1)[1].split(")", 1)[0].split(",")
        )
        clean["title"] = coords.text.strip()
    except Exception:
        clean["lat"], clean["lon"] = ["<MISSING>", "<MISSING>"]
        clean["title"] = "<MISSING>"
    try:
        addr1 = raw.find("dd").text.strip()
        addr2 = raw.find("dd", {"class": "road"}).text.strip()
        parsed1 = parser.parse_address_intl(addr1)
        parsed2 = parser.parse_address_intl(addr2)
    except Exception:
        parsed1 = None
        parsed2 = None

    clean["street_addr"] = (
        parsed2.street_address_1
        if parsed2.street_address_1
        else parsed1.street_address_1
        if parsed1.street_address_1
        else "<MISING>"
    )
    clean["city"] = (
        parsed2.city if parsed2.city else parsed1.city if parsed1.city else "<MISSING>"
    )
    clean["state"] = (
        parsed2.state
        if parsed2.state
        else parsed1.state
        if parsed1.state
        else "<MISSING>"
    )
    clean["country"] = (
        parsed2.country
        if parsed2.country
        else parsed1.country
        if parsed1.country
        else "<MISSING>"
    )
    clean["postcode"] = (
        parsed2.postcode
        if parsed2.postcode
        else parsed1.postcode
        if parsed1.postcode
        else "<MISSING>"
    )
    clean["raw_address"] = str("['" + addr1 + "','" + addr2 + "']")

    try:
        loctypes = raw.find("div", {"class": "service"}).find_all("span")
        clean["types"] = []
        for i in loctypes:
            clean["types"].append(i.text.strip())
        clean["types"] = "; ".join(clean["types"])
    except Exception:
        clean["types"] = "<MISSING>"

    try:
        hours = raw.find_all("td", {"class": False})
        clean["hours"] = hours[-1].text.strip()
        clean["hours"] = clean["hours"].replace('"', "").replace("\n", "; ")
        clean["phone"] = hours[0].text.strip()
        clean["phone"] = clean["phone"].replace('"', "").replace("\n", "; ")
        try:
            phonyBackup = clean["phone"].split(" ", 1)[0]
            if len(phonyBackup) >= 10:
                clean["phone"] = phonyBackup
        except Exception:
            pass
    except Exception:
        clean["hours"] = "<MISSING>"
        clean["phone"] = "<MISSING>"

    return clean


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = ""
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    with SgRequests() as session:
        url = "https://mcdonalds.co.kr/kor/store/list.do?page={}&lat=NO&lng=NO&search_options=&searchWord="
        page = 1
        while True:
            dat = session.post(url.format(page), headers=headers).text
            soup = b4(dat, "lxml")
            if '"road"' not in dat:
                break
            data = (
                soup.find("table", {"class": "tableType01"})
                .find("tbody")
                .find_all("tr")
            )
            for raw in data:
                yield cleanup_this(raw)
            page += 1

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "mcdonalds.co.kr"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["title"],
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["lon"],
        ),
        street_address=sp.MappingField(
            mapping=["street_addr"],
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
            is_required=False,
        ),
        country_code=sp.MappingField(
            mapping=["country"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
            is_required=False,
        ),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
            part_of_record_identity=True,
            is_required=False,
        ),
        location_type=sp.MappingField(
            mapping=["types"],
        ),
        raw_address=sp.MappingField(
            mapping=["raw_address"],
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
