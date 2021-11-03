from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://aldoshoes.it"
base_url = "https://aldoshoes.it/it/store-locator"


def _p(val):
    if (
        val.replace("(", "")
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
        res = session.get(base_url, headers=_headers).text
        locations = res.split("gmap.addMarker(")[1:]
        for loc in locations:
            _ = json.loads(loc.split(");")[0])
            block = list(bs(_["infoWindow"]["content"], "lxml").stripped_strings)[1:]
            phone = ""
            if _p(block[-1]):
                phone = block[-1]
                del block[-1]
            if phone == "0":
                phone = ""
            raw_address = " ".join(block)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                location_name=_["title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Italy",
                phone=phone,
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

        locations = bs(res, "lxml").select(
            "div.weasy_page_content  div.row div.omw-sentence"
        )[-6:-3]
        for _ in locations:
            if not _.p:
                continue
            block = []
            for bb in _.select("p")[:-1]:
                block += list(bb.stripped_strings)
            if "@" in block[-1]:
                del block[-1]
            phone = ""
            if "T:" in block[-1]:
                phone = block[-1].replace("T:", "")
                del block[-1]
            raw_address = " ".join(block[1:])
            addr = parse_address_intl(raw_address + ", Italy")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if "Roma" in raw_address:
                city = "Roma"
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address,
                city=city,
                zip_postal=addr.postcode,
                country_code="Italy",
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
