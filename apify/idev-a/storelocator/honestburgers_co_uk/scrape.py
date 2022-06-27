from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("honestburgers")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.honestburgers.co.uk"
base_url = "https://www.honestburgers.co.uk/locations/"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers)
        store_list = bs(res.text, "lxml").select("div.filterable-location")
        for store in store_list:
            page_url = store.select_one("a")["href"]
            if page_url == base_url:
                continue
            logger.info(page_url)
            location_name = store.h3.text.replace("–", "-")
            soup = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            try:
                if (
                    "currently closed"
                    in soup.select_one("div.hero-location div.sm-0 p").text.lower()
                ):
                    hours = ["Temporarily closed"]
            except:
                pass

            zip_postal = city = latitude = street_address = phone = longitude = ""
            try:
                detail = json.loads(
                    soup.find_all("script", type="application/ld+json")[-1].string
                )
                zip_postal = detail["address"]["postalCode"]
                city = detail["address"]["addressRegion"]
                street_address = detail["address"]["streetAddress"]
                phone = detail["telephone"]
                latitude = detail["geo"]["latitude"]
                longitude = detail["geo"]["longitude"]
            except:
                addr = []
                try:
                    addr = list(
                        soup.select_one("div.hero-location > p").stripped_strings
                    )
                    zip_city = addr[1].split()
                    zip_postal = " ".join(zip_city[-2:])
                    city = " ".join(zip_city[:-2])
                    street_address = addr[0]
                except:
                    pass
                try:
                    phone = soup.find("a", href=re.compile(r"tel:")).text.strip()
                except:
                    pass
            try:
                days = [
                    day.text
                    for day in soup.select("div.hero-location dl dt")
                    if day.text.strip()
                ]
                if "Lunch & Dinner" in days[0]:
                    del days[0]
                times = [
                    tt.text
                    for tt in soup.select("div.hero-location dl dd")
                    if tt.text.strip()
                ]
                for x in range(len(days)):
                    hours.append(f"{days[x]}: {times[x]}")
            except:
                pass

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                phone=phone,
                locator_domain=locator_domain,
                country_code="UK",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
