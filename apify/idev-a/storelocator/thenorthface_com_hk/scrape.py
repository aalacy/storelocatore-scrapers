from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thenorthface.com.hk"
base_url = "https://www.thenorthface.com.hk/find-a-store/#"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        countries = soup.select("div.store-list-item")
        for country in countries:
            country_code = country.h6.text.strip()
            locations = country.select("li")
            for _ in locations:
                strongs = _.select("strong")
                raw_address = strongs[1].text.strip()
                if _p(raw_address):
                    continue
                if country_code not in raw_address:
                    raw_address += ", " + country_code
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                if city and city in [
                    "Mens",
                    "The",
                    "Hong",
                    "A-05C",
                    "A-16",
                    "#035-036",
                ]:
                    city = ""
                if "MUNTINLUPA" in raw_address:
                    city = "MUNTINLUPA"
                state = addr.state
                if state and state in ["Department"]:
                    state = ""
                zip_postal = addr.postcode
                if zip_postal and zip_postal in ["POKHARABAIDAM-6", "RAMA9"]:
                    zip_postal = ""
                phone = ""
                if len(strongs) > 2:
                    phone = strongs[-1].text.strip()
                yield SgRecord(
                    page_url=base_url,
                    location_name=strongs[0]
                    .text.replace("\n", "")
                    .replace("\r", "")
                    .strip(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
