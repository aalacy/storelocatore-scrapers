from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.bizou.com/"
page_url = "https://bizou.com/pages/store-locator"
base_url = "https://cdn.shopify.com/s/files/1/0482/6015/3510/t/5/assets/sca.storelocatordata.json?v=1646331102&origLat=37.09024&origLng=-95.712891&origAddress=5000%20Estate%20Enighed%2C%20Independence%2C%20KS%2067301%2C%20USA&formattedAddress=&boundsNorthEast=&boundsSouthWest=&_=1646643410412"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            hours = list(bs(_["schedule"], "lxml").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["id"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
