from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.barrelandstone.co.uk/discover-local/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="col-lg-3 col-md-4 col-sm-6 pub-list mb3 pub-item")
    locator_domain = "https://www.barrelandstone.co.uk/"

    for item in items:
        link = item.a["href"]

        location_name = item.find(class_="h4").text.strip()
        latitude = item["data-coords"].split(",")[0]
        longitude = item["data-coords"].split(",")[1]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = " ".join(
            base.find(
                class_="col-md-offset-6 col-md-6 text-center mb3"
            ).p.stripped_strings
        )
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        if not zip_code:
            if raw_address.split()[-1].isupper():
                zip_code = " ".join(raw_address.split()[-2:])
        if zip_code and street_address:
            if zip_code.lower() in street_address.lower():
                zip_loc = street_address.lower().find(zip_code.lower())
                street_address = street_address[:zip_loc].strip()
        country_code = "UK"
        location_type = ""
        store_number = ""
        try:
            phone = base.find(class_="barrel-font text-primary tdu").text.strip()
        except:
            phone = ""
        try:
            hours_of_operation = (
                " ".join(
                    list(base.find(string="Opening Hours").find_next().stripped_strings)
                )
                .replace("\n", " ")
                .replace("The Terrace", "")
                .replace("Opening times", "")
                .replace("to visitors and the public", "")
                .replace("The Poacher Pub", "")
                .replace("Oxen Bar & Grill Open for breakfast, lunch and dinner", "")
                .replace("KITCHEN HOURS:", "")
                .replace("Room service also available", "")
                .replace("The Bar is Open:", "")
                .replace("Opening hours:", "")
                .replace("Opening Times:", "")
                .replace("Terrace Bistro", "")
                .replace("Lounge Bar", "")
                .replace("Bloomsbury", "")
                .replace("Restaurant & Bar:", "")
                .replace("Squares", "")
                .replace("\t", " ")
                .replace("  ", " ")
                .split("( last")[0]
                .split("(bank")[0]
                .split("Food Service")[0]
                .split("Food is ")[0]
                .split("If there is")[0]
                .split("Kitchen is open")[0]
                .split("Pizza &")[0]
                .split("Whites Restaurant:")[0]
                .split("PLEASE NOTE")[0]
                .split("For Stadium")[0]
                .strip()
            )
            if (
                "The Hill restaurant" in hours_of_operation
                or "website" in hours_of_operation
            ):
                hours_of_operation = ""
        except:
            hours_of_operation = ""

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
