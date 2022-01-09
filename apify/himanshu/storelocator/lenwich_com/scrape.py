import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "https://www.lenwich.com/locations/"
    r = session.get(base_url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "lxml")

    script = soup.find("script", attrs={"type": "application/ld+json"}).contents[0]
    info = json.loads(script)["subOrganization"]

    locator_domain = "lenwich.com"
    for i in info:
        link = i["url"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        r_loc = session.get(link)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        hours = (
            " ".join(list(soup_loc.find(id="intro").find_all("p")[-1].stripped_strings))
            .replace("Hours", "")
            .replace("Hou rs", "")
            .strip()
        )
        latitude = soup_loc.find(class_="gmaps")["data-gmaps-lat"]
        longitude = soup_loc.find(class_="gmaps")["data-gmaps-lng"]

        location_name = i["name"]
        street_address = i["location"]["streetAddress"]
        city = i["location"]["addressLocality"]
        state = i["location"]["addressRegion"]
        zipp = i["location"]["postalCode"]
        phone = i["telephone"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
