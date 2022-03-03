from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.gloriajeans.ro/language"
base_url = "https://www.gloriajeans.ro/language/en/store-locator/"


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
        locations = soup.select("article.iconbox")
        for _ in locations:
            block = list(_.p.stripped_strings)
            phone = ""
            if _p(block[-1]):
                phone = block[-1]
                del block[-1]
            if "Phone" in block[-1]:
                del block[-1]
            if "@" in block[-1]:
                del block[-1]
            if "Email" in block[-1]:
                del block[-1]
            hours = ""
            if "hours" in block[-1] or "–" in block[-1]:
                hours = block[-1].split("hours:")[-1].replace("–", "-")
                del block[-1]
            if "hours" in block[-1]:
                del block[-1]

            zip_postal = ""
            if "Code" in block[-1]:
                zip_postal = block[-1].split(":")[-1]
                del block[-1]
            raw_address = " ".join(block)
            addr = parse_address_intl(raw_address)
            if addr.postcode:
                zip_postal = addr.postcode
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=" ".join(block[:-1]).replace(",", " "),
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code="Romania",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=" ".join(block),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
