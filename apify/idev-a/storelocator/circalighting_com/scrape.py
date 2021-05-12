from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.circalighting.com"
    base_url = "https://www.circalighting.com/showrooms/"
    streets = []
    phones = []
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.category-cms .pagebuilder-column")
        for _ in locations:
            if not _.select_one("div.more"):
                continue
            if "Coming Soon" in _.select_one("div.more").text:
                continue
            block = list(_.select_one("div.more").stripped_strings)
            page_url = locator_domain + _.select("div.more a")[-1]["href"]
            if block[1].strip() in streets:
                continue
            streets.append(block[1].strip())
            block = [
                bb
                for bb in block
                if bb != "MAKE APPOINTMENT"
                and "Opening" not in bb
                and "More Information" not in bb
                and "appointment" not in bb
            ]
            phone = ""
            if "Phone" in block[3]:
                phone = block[3].replace("Phone", "").strip()
            if phone in phones:
                continue
            phones.append(phone)
            hours = []
            if len(block) >= 5:
                hours = block[4:]
            addr = parse_address_intl(" ".join(block[1:3]))
            country = "US"
            if len(addr.postcode) > 5:
                country = "UK"
            yield SgRecord(
                page_url=page_url,
                location_name=block[0],
                street_address=block[1],
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
