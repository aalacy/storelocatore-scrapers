from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://buchheits.com/"
page_url = "https://buchheits.com/about-us/locations"
base_url = "https://buchheits.com/api/pages?menu=3&path=locations"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "table tr td"
        )
        for _ in locations:
            if not _.text.strip():
                continue
            addr = [
                aa.strip() for aa in _.stripped_strings if aa.strip().replace("\\n", "")
            ]
            try:
                coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = ["", ""]
            hours = [hh for hh in addr[4:-1] if "Hours" not in hh]
            yield SgRecord(
                page_url=page_url,
                location_name=addr[0],
                street_address=addr[1],
                city=addr[2].split(",")[0].strip(),
                state=addr[2].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[2].split(",")[1].strip().split(" ")[-1].strip(),
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=addr[3],
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
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
