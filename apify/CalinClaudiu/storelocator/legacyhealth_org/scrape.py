from sgscrape import simple_scraper_pipeline as sp
from sgscrape import sgpostal as parser
from sglogging import sglog


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def determine(loc):
    k = {}
    k["page_url"] = (
        loc.find("a", {"class": "ls-view-link", "href": True})["href"]
        if loc.find("a", {"class": "ls-view-link", "href": True})
        else "<MISSING>"
    )
    try:
        k["name"] = loc.find("span", {"data-marker-text": True})["data-marker-text"]
    except Exception:
        k["name"] = "<MISSING>"

    try:
        coords = loc.find("div", {"data-lat": True})
        k["lat"] = coords["data-lat"]
        k["lng"] = coords["data-lng"]
    except Exception:
        k["lat"] = "<MISSING>"
        k["lng"] = "<MISSING>"

    raw_addr = " ".join(list(loc.find("address").stripped_strings))
    raw_addr = raw_addr.replace("\r", "").replace("\n", "")
    ImSorry = [
        "Legacy Salmon Creek Medical Center, Medical Office Building B",
        "located at Legacy Medical Group-Cornell",
        "3rd Floor Randall Children's Hospital at Legacy Emanuel",
        "Randall Children's Hospital at Legacy Emanuel",
        "Medical Office Building A,",
        "Medical Office Building A",
        "Building 1 Legacy Good Samaritan Medical Center campus Portland",
        "Good Samaritan Building 2,",
    ]
    for i in ImSorry:
        raw_addr = raw_addr.replace(i, "")
    k["rawa"] = raw_addr
    breakables = ["CLINIC", "Clinic"]
    try:
        parsed = parser.parse_address_usa(raw_addr)
    except Exception:
        for eww in breakables:
            try:
                separated = raw_addr.split(eww)
                raw_addr = (
                    separated[1]
                    if len(separated[1]) > len(separated[0])
                    else separated[0]
                )
                break
            except Exception:
                continue

        parsed = parser.parse_address_usa(raw_addr)
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
        k["phone"] = loc.find("a", {"href": lambda x: x and x.startswith("tel:")})[
            "href"
        ].split("tel:")[1]
    except Exception:
        k["phone"] = "<MISSING>"

    try:
        k["hours"] = loc.find("div", {"class": "ls-info-inner"}).find("p").text.strip()
    except Exception:
        k["hours"] = "<MISSING>"

    try:
        k["type"] = (
            loc.find("div", {"class": "ls-image-card", "style": True})["style"]
            .split("Locations/", 1)[1]
            .split("/", 1)[0]
        )
    except Exception:
        k["type"] = "<MISSING>"
    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.legacyhealth.org/doctors-and-locations?Latitude=&Longitude=&keyword=&services=&ActiveLocationTypeFilter=&ZipCode=&Radius=5&SearchType=LOCATIONS&OpenWeekends=false&Open24Hours=false&PageNumber="
    page = 0
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    while True:
        page += 1
        soup = b4(session.get(url + str(page), headers=headers).text, "lxml")
        locs = soup.find("div", {"class": "ls-list-result"}).find_all(
            "div", {"class": "LegacyHealth-Feature-LocationSearch-LocationItem"}
        )
        if len(locs) > 0:
            for loc in locs:
                zap = determine(loc)
                yield zap
        else:
            break

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.legacyhealth.org"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["name"]),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MappingField(
            mapping=["address"],
        ),
        city=sp.MappingField(mapping=["city"]),
        state=sp.MappingField(mapping=["state"]),
        zipcode=sp.MappingField(mapping=["zip"]),
        country_code=sp.MappingField(mapping=["country"]),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(mapping=["type"]),
        raw_address=sp.MappingField(mapping=["rawa"]),
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
