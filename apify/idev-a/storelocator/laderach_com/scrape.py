from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://laderach.com/"
base_url = "https://us.laderach.com/our-locations/"


ca_provinces = [
    "alberta",
    "british columbia",
    "manitoba",
    "new brunswick",
    "newfoundland and labrador",
    "nova scotia",
    "ontario",
    "prince edward island",
    "quebec",
    "saskatchewan",
]
ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def get_country_by_code(state, raw_address):
    if state:
        if us.states.lookup(state):
            return "United States"
        elif state in ca_provinces_codes:
            return "Canada"
    elif "Singapore" in raw_address:
        return "Singapore"
    elif "Seoul" in raw_address:
        return "South Korea"
    else:
        return ""


def fetch_data(session):
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    stores = soup.select("div.amlocator-store-desc")
    for _ in stores:
        block = list(_.select_one("div.main-info").stripped_strings)
        raw_address = phone = page_url = ""
        for x, bb in enumerate(block):
            if bb == "Address":
                raw_address = block[x + 1]
            if bb == "Website":
                page_url = block[x + 1]
                if page_url == "Phone":
                    page_url = ""
            if bb == "Phone" and x + 1 < len(block):
                phone = block[x + 1]

        location_name = _.select_one("a.title").text.strip()
        addr = parse_address_intl(raw_address)
        city = addr.city
        state = addr.state
        zip_postal = addr.postcode
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if street_address.isdigit() and len(raw_address.split(",")) > 1:
            street_address = raw_address.split(",")[0]
        country_code = addr.country
        if not country_code:
            country_code = get_country_by_code(addr.state, raw_address)
        if not country_code:
            nn = location_name.split("|")
            country_code = nn[1]
        hours = []
        for hh in _.select(
            "table.sk-ww-google-business-profile-content-container tr table tr"
        ):
            hours.append(" ".join(hh.stripped_strings))
        yield SgRecord(
            page_url=page_url or base_url,
            location_name=location_name,
            store_number=_["data-amid"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=raw_address,
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        with SgRequests() as session:
            results = fetch_data(session)
            for rec in results:
                writer.write_row(rec)
