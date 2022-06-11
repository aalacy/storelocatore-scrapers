from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.auntieannes.ru"
base_url = "http://www.auntieannes.ru/locations/"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locs = json.loads(
            res.split("var balloonArray =")[1].split("map_clusters")[0].strip()[:-1]
        )
        locations = bs(res, "lxml").select("div.r-loc")
        for x, _ in enumerate(locations):
            raw_address = _.select_one("p.loc-res-address").text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = locs[x]["center"]
            phone = hours_of_operation = ""
            if _.select_one("p.loc-res-phone"):
                phone = _.select_one("p.loc-res-phone").text.strip()
            if _.select_one("span.open-until"):
                hours_of_operation = _.select_one("span.open-until").text.strip()
            if hours_of_operation == "Открыто":
                hours_of_operation = ""
            yield SgRecord(
                page_url=base_url,
                store_number=_.h2.a["data-store"],
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=coord[0],
                longitude=coord[1],
                country_code="RU",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
