from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.strip().replace("–", "-").replace("’", "'")


def fetch_data():
    locator_domain = "https://koyajapan.com/"
    base_url = "https://koyajapan.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.elementor-column.elementor-col-50")
        for _ in locations:
            if not _.text.strip():
                continue
            addr = list(_.p.stripped_strings)
            hours = []
            if re.search(r"TEMPORARILY CLOSED", _.text, re.IGNORECASE):
                hours = ["TEMPORARILY CLOSED"]
                addr = list(_.select("p")[1].stripped_strings)
            else:
                hours = (
                    _.select("div.elementor-element")[2]
                    .select("p")[-1]
                    .stripped_strings
                )

            try:
                coord = (
                    _.select("a")[-1]["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=_valid(addr[0]),
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip(),
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=addr[2],
                country_code="CA",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
