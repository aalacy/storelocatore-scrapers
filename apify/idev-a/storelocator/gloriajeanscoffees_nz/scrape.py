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

locator_domain = "https://gloriajeanscoffees.nz"
base_url = "https://gloriajeanscoffees.nz/pages/store-locator"


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
        locations = soup.select("main div.rte p")
        for _ in locations:
            if not _.text.strip() or _.strong:
                continue
            block = list(_.stripped_strings)
            phone = ""
            if _p(block[-1]):
                phone = block[-1]
                del block[-1]
            addr = block[1:]
            raw_address = " ".join(addr)
            addr = parse_address_intl(raw_address + ", Netherlands")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            try:
                coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address.replace("Khartoum Place", "")
                .replace("Westfield Manukau", "")
                .replace("The Base Shopping Centre Te Rapa", "")
                .replace("Westfield Chartwell", ""),
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="NZ",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
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
