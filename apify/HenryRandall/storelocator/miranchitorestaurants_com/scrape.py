import re
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    url = "http://www.miranchitorestaurants.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(url, headers=headers)
    soup = BeautifulSoup(req.text, "lxml")
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    for script in scripts:
        loc_data = json.loads(re.findall(r"{.*}", str(script))[0])
        hoo = ", ".join(loc_data["openingHours"]).strip()
        loc = loc_data["address"]["addressLocality"]
        loc_url = url + loc.lower().replace(" ", "-")
        street_address = loc_data["address"]["streetAddress"]
        regex = f'(?<={street_address}).*?(?="menuLandingPageUrl")'
        coords = re.findall(regex, str(soup))
        lat, long = re.findall(r'"lat":(-?[\d\.]+),"lng":(-?[\d\.]+)', str(coords))[0]

        sgw.write_row(
            SgRecord(
                locator_domain=url,
                page_url=loc_url,
                location_name=loc,
                street_address=street_address,
                city=loc,
                state=loc_data["address"]["addressRegion"],
                zip_postal=loc_data["address"]["postalCode"],
                country_code=SgRecord.MISSING,
                store_number=SgRecord.MISSING,
                phone=loc_data["address"]["telephone"],
                location_type=loc_data["@type"],
                latitude=lat,
                longitude=long,
                hours_of_operation=hoo,
            )
        )


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)


scrape()
