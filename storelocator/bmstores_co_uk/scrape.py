from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("bmstores")

locator_domain = "https://www.bmstores.co.uk"
base_url = "https://www.bmstores.co.uk"
headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "cookie": "cftoken=0; CURRENTFARCRYPROJECT=bmstorescouk; FARCRYDEVICETYPE=desktop; _ALGOLIA=anonymous-2beb611b-d307-4db0-910b-81e1448ec1b6; _ga=GA1.3.624511035.1611222053; _gid=GA1.3.197517442.1611222053; _gat_UA-23199122-1=1; INGRESSCOOKIE=46a06f577086c2c7f08d6e67b0feb709; OptanonConsent=isIABGlobal=false&datestamp=Thu+Jan+21+2021+13%3A42%3A03+GMT-0500+(Eastern+Standard+Time)&version=5.8.0&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_17%3A1%2C0_27%3A1%2C0_26%3A1%2C0_25%3A1%2C0_24%3A1%2C0_23%3A1%2C0_22%3A1%2C0_21%3A1%2C0_20%3A1%2C0_19%3A1%2C0_18%3A1&AwaitingReconsent=false; SESSIONSCOPETESTED=true; HASSESSIONSCOPE=true; cfid=d37d7d0f-023c-44ce-a3af-c253a9b3caae",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def parse_result(page_url, soup, store):
    street_address = soup.select_one("span[itemprop='streetAddress']").text
    city = soup.select_one("span[itemprop='addressLocality']").string
    state = soup.select_one("span[itemprop='addressRegion']").string
    zipcode = soup.select_one("span[itemprop='postalCode']").string
    phone = soup.select_one("span[itemprop='telephone']")
    phone = "" if phone is None else phone.string

    hr = []
    if soup.find_all("h4", string=re.compile(r"Opening Times$")):
        hr = (
            soup.find_all("h4", string=re.compile(r"Opening Times$"))[-1]
            .find_next_sibling()
            .select("li")
        )
    hours = []
    for hh in hr:
        div = hh.select("div")
        hours.append(f"{div[0].text.strip()}: {div[1].text.strip()}")

    if not hours:
        note = soup.find("h4", string=re.compile(r"Store Notes"))
        if note:
            note = note.find_next_sibling().text.strip()
            if "Unfortunately" in note and "CLOSED" in note:
                hours = ["closed"]

    street_address = street_address.replace("\n", " ").strip()
    location_name = ""
    if "markerHomestoreGardenCentre" in store["properties"]["svg"]:
        location_name = "B&M Home Store with Garden Centre"
    elif "markerBargainstore" in store["properties"]["svg"]:
        location_name = "B&M Store"
    elif (
        "markerBargainstore" in store["properties"]["svg"]
        or "markerHomestore" in store["properties"]["svg"]
    ):
        location_name = "B&M Home Store"

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zipcode,
        country_code="GB",
        phone=phone,
        locator_domain=locator_domain,
        latitude=store["geometry"]["coordinates"][1],
        longitude=store["geometry"]["coordinates"][0],
        hours_of_operation="; ".join(hours).replace("Store Hours:", ""),
    )


def fetch_data():
    with SgRequests() as session:
        store_list = session.get(
            "https://www.bmstores.co.uk/hpcstores/StoresGeoJson&start=1&maxrows=10000",
            headers=headers,
        ).json()["features"]
        for store in store_list:
            page_url = base_url + store["properties"]["link"]
            logger.info(page_url)
            soup = bs(session.get(page_url, headers=headers).text, "lxml")
            yield parse_result(page_url, soup, store)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
