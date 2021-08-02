from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://uni-mart.com"
base_url = "https://uni-mart.com/locations?radius=-1&filter_catid=0&limit=0&filter_order=distance&searchzip=Pennsylvania?searchzip=You&task=search&radius=-1&option=com_mymaplocations&limit=0&component=com_mymaplocations&Itemid=223&zoom=9&format=json&geo=1&limitstart=0&latitude=37.09024&longitude=-95.712891"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["features"]
        for _ in locations:
            page_url = locator_domain + _["properties"]["url"]
            addr = list(
                bs(_["properties"]["fulladdress"], "lxml")
                .select_one("span.locationaddress")
                .stripped_strings
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["properties"]["name"].split("#")[1],
                location_name=_["properties"]["name"],
                street_address=addr[0],
                city=addr[1].split(",")[0],
                state=addr[1].split(",")[1],
                zip_postal=addr[2].split("\xa0")[1],
                latitude=_["geometry"]["coordinates"][1],
                longitude=_["geometry"]["coordinates"][0],
                country_code=addr[2].split("\xa0")[0],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
