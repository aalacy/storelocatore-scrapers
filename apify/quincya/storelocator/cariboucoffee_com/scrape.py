from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("cariboucoffee_com")


def fetch_data(sgw: SgWriter):
    base_link = "https://locations.cariboucoffee.com/us"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []
    locator_domain = "cariboucoffee.com"

    url = "https://locations.cariboucoffee.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'hreflang="en" href="https://locations.cariboucoffee.com/us/' in line:
            lurl = line.split('href="')[1].split('"')[0].replace("&#39;", "'")
            if lurl.count("/") == 6:
                final_links.append(lurl)

    logger.info("Processing " + str(len(final_links)) + " links ..")
    for final_link in final_links:
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.find(id="location-name").text.strip()
        street_address = base.find(itemprop="streetAddress")["content"]
        city = base.find(class_="c-address-city").text.strip()
        state = base.find(itemprop="addressRegion").text.strip()
        zip_code = base.find(itemprop="postalCode").text.strip()
        country_code = "US"

        try:
            phone = base.find(id="telephone").text.strip()
        except:
            phone = ""
        store_number = ""
        location_type = ""

        try:
            hours_of_operation = (
                " ".join(
                    list(base.find(class_="c-location-hours-details").stripped_strings)
                )
                .replace("Day of the Week Hours", "")
                .strip()
            )
        except:
            hours_of_operation = ""

        latitude = base.find(itemprop="latitude")["content"]
        longitude = base.find(itemprop="longitude")["content"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
