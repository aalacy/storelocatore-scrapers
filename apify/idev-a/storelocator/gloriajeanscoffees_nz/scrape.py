from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

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
            street_address = (
                " ".join(addr[:-1])
                + " "
                + " ".join(addr[-1].split()[:-2]).replace(",", "")
            )
            try:
                coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address,
                city=addr[-1].split()[-2].strip(),
                zip_postal=addr[-1].split()[-1].strip(),
                country_code="NZ",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
