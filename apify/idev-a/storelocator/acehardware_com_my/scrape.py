from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://acehardware.com.my"
base_url = "https://acehardware.com.my/location/"


def _coord(locs, v):
    coord = {"latitude": "", "longitude": ""}
    for loc in locs:
        if (
            loc["marker_description"]
            and bs(loc["marker_description"], "lxml").text.replace("Branch", "").strip()
            in v
        ):
            coord = loc
            break

    return coord


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locs = json.loads(res.split("labVcMaps.push(")[1].split(");")[0])["locations"]
        soup = bs(res, "lxml")
        locations = soup.select("div.vc_col-sm-3")
        for _ in locations:
            if not _.text:
                continue
            raw_address = " ".join(_.p.stripped_strings)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = ""
            if "Hour" in _.select("p")[-1].text:
                hours = _.select("p")[-1].text
            coord = _coord(locs, raw_address)
            hours.replace("Operation Hours:", "").strip()
            if "temporarily closed" in hours.lower():
                hours = "temporarily closed"
            yield SgRecord(
                page_url=base_url,
                location_name=_.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="MY",
                latitude=coord["latitude"],
                longitude=coord["longitude"],
                locator_domain=locator_domain,
                hours_of_operation=hours.replace("Operation Hours:", "").strip(),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
