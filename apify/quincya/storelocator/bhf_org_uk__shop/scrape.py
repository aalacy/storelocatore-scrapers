from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


from sgrequests import SgRequests

logger = SgLogSetup().get_logger("www.bhf.org.uk")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://www.bhf.org.uk/what-we-do/find-bhf-near-you?keyword=&tab=locations&servicetype=book-bank%2cbooks-music-shop%2cclothing-bank%2cclothing-shop%2cfurniture-electrical-store&run=1&page="
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    found = []
    locator_domain = "https://www.bhf.org.uk"

    last_page = int(base.find(class_="pagination-last").a["href"].split("=")[-1]) + 1

    for num in range(1, last_page):

        base_link = (
            "https://www.bhf.org.uk/what-we-do/find-bhf-near-you?keyword=&tab=locations&servicetype=book-bank%2cbooks-music-shop%2cclothing-bank%2cclothing-shop%2cfurniture-electrical-store&run=1&page="
            + str(num)
        )
        logger.info(base_link)
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find_all(class_="c-search-results-MVC__list--item")

        for item in items:
            link = locator_domain + item.a["href"]
            if link in found:
                continue
            found.append(link)

            location_name = item.a.text.strip()

            raw_address = item.p.text.strip()
            if "May 2018." in raw_address:
                raw_address = raw_address.split("2018.")[1].strip()
            addr = parse_address_intl(raw_address)
            try:
                street_address = addr.street_address_1 + " " + addr.street_address_2
            except:
                street_address = addr.street_address_1
            if not street_address or len(street_address) < 8:
                street_address = " ".join(raw_address.split(",")[:-2]).strip()

            city = addr.city
            state = addr.state
            zip_code = raw_address.split(",")[-1].strip()

            if not city:
                city = raw_address.split(",")[-2].strip()
                street_address = " ".join(raw_address.split(",")[:-2]).strip()
            if zip_code.upper() in street_address.upper():
                street_address = " ".join(raw_address.split(",")[:-2]).strip()

            street_address = (
                street_address.replace(
                    " Outside Entrance Kingsland Shopping Centre", ""
                )
                .replace(" Car Park in Wolfe House Car Park  ", "")
                .replace(" Main Road Mini Roundabout Old", "")
                .replace("  ", " ")
                .strip()
            )

            country_code = "GB"
            store_number = "<MISSING>"
            try:
                location_type = item.find(class_="number")["data-phone-hotline-name"]
                phone = item.find(class_="number").text.replace("�", "").strip()
            except:
                location_type = ""
                phone = ""

            req = session.get(link, headers=headers)
            try:
                base = BeautifulSoup(req.text, "lxml")

                hours_of_operation = ""
                try:
                    raw_hours = base.find("h2", string="Opening Hours").find_all_next(
                        "p"
                    )
                    for hour in raw_hours:
                        if "day" in hour.text:
                            hours_of_operation = (
                                hours_of_operation + " " + hour.text.strip()
                            ).strip()
                    if not hours_of_operation:
                        hours_of_operation = ""
                except:
                    pass

                try:
                    latitude = base.find(class_="bhflocation map-container-small")[
                        "data-lat"
                    ]
                    longitude = base.find(class_="bhflocation map-container-small")[
                        "data-lon"
                    ]
                except:
                    latitude = ""
                    longitude = ""
            except:
                hours_of_operation = ""
                latitude = ""
                longitude = ""

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
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
                    raw_address=raw_address,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
