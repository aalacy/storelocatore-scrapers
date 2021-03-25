from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def para(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    goodStuff = session.get(url, headers=headers).text

    soup = b4(goodStuff, "lxml")

    k = {}
    k["page_url"] = url

    try:
        k["name"] = soup.find("span", {"itemprop": "name"}).text.strip()
    except Exception:
        k["name"] = "<MISSING>"

    scripts = soup.find_all("script", {"type": "text/javascript"})
    coords = ""
    for i in scripts:
        if "var lat =" in i.text:
            coords = i.text
    try:
        k["lat"] = coords.split("lat", 1)[1].split('("', 1)[1].split('")', 1)[0]
    except Exception:
        k["lat"] = "<MISSING>"

    try:
        k["lng"] = coords.split("lng", 1)[1].split('("', 1)[1].split('")', 1)[0]
    except Exception:
        k["lng"] = "<MISSING>"
    check = 1
    for i in k["lng"]:
        if i.isdigit():
            if i != 0:
                check = 0
    if check == 1:
        k["lng"] = "<MISSING>"

    check = 1
    for i in k["lat"]:
        if i.isdigit():
            if i != 0:
                check = 0
    if check == 1:
        k["lat"] = "<MISSING>"

    try:
        addressData = []
        for i in soup.find_all("span", {"class": "spnLDTCIAddress"}):
            if "!!" not in i.text:
                addressData.append(i.text)

        k["address"] = ", ".join(addressData)
    except Exception:
        pass
    if not k["address"]:
        try:
            k["address"] = soup.find("span", {"itemprop": "streetAddress"})["content"]
        except Exception:
            k["address"] = "<MISSING>"
    if "Call/Email" in k["address"]:
        k["address"] = "<MISSING>"
    try:
        k["city"] = soup.find("span", {"itemprop": "addressLocality"}).text.strip()
    except Exception:
        k["city"] = "<MISSING>"

    try:
        k["state"] = soup.find("span", {"itemprop": "addressRegion"}).text.strip()
    except Exception:
        k["state"] = "<MISSING>"

    try:
        k["zip"] = soup.find("span", {"itemprop": "postalCode"}).text.strip()
        # currently no location has zipcode, so no idea what to put here.
        # the code above is just a random guess based on how the rest of the data looks.
    except Exception:
        k["zip"] = "<MISSING>"

    try:
        k["phone"] = soup.find(
            "a", {"href": lambda x: x and x.startswith("tel:")}
        ).text.strip()
    except Exception:
        k["phone"] = "<MISSING>"

    try:
        h = soup.find("div", {"class": "divLDTHours"}).find_all(
            "meta", {"itemprop": "openingHours", "content": True}
        )
        k["hours"] = []
        for i in h:
            k["hours"].append(i["content"])

        k["hours"] = "; ".join(k["hours"])
    except Exception:
        k["hours"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.mauiwowi.com/Locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")
    pages = []
    links = soup.find_all(
        "a", {"href": lambda x: x and ("Locations/US/" in x or "Locations/CA/" in x)}
    )
    for i in links:
        pages.append(str("https://www.mauiwowi.com/" + i["href"]))

    for j in pages:
        counter = 0
        i = para(j)
        while (
            all(
                i[k] == "<MISSING>"
                for k in ["name", "address", "city", "state", "zip", "phone", "hours"]
            )
            and counter < 10
        ):
            counter += 1
            i = para(j)
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.mauiwowi.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["name"]),
        latitude=sp.MappingField(mapping=["lat"], is_required=False),
        longitude=sp.MappingField(mapping=["lng"], is_required=False),
        street_address=sp.MappingField(mapping=["address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(
            mapping=["page_url"],
            value_transform=lambda x: x.split("Locations/", 1)[1].split("/", 1)[0],
        ),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["page_url"], value_transform=lambda x: x.split("/")[-1]
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MissingField(),
        raw_address=sp.MissingField(),
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
