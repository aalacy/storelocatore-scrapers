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

locator_domain = "https://geprekbensuindonesia.com"
base_url = "https://geprekbensuindonesia.com/lokasi/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("table#tablepress-1 tbody tr")
        for _ in locations:
            location_name = _.strong.text.strip()
            if location_name == "GB CIRACAS":
                continue
            raw_address = _.select("p")[1].text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if city and city.isdigit():
                city = ""
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
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation=_.select("p")[-1].text.strip(),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
