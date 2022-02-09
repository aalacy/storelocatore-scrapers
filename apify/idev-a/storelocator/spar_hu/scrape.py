from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("spar")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.spar.hu"
base_url = "https://www.spar.hu/uzletek/_jcr_content.marker.v2.html?hour=&filter="
json_url = "https://www.spar.hu/uzletek/_jcr_content.stores.v2.html?latitude={}&longitude={}&radius=40&hour=&filter="


def _f(val):
    if len(str(val)) == 1:
        return "0" + str(val)
    return val


def fetch_data():
    with SgRequests() as session:
        latLngs = session.get(base_url, headers=_headers).json()
        for latlng in latLngs:
            url = json_url.format(latlng["latitude"], latlng["longitude"])
            locations = session.get(url, headers=_headers).json()
            logger.info(
                f"[{latlng['latitude'], latlng['longitude']}] {len(locations)} found"
            )
            for _ in locations:
                page_url = locator_domain + _["pageUrl"]
                hours = []
                for hh in _.get("shopHours", []):
                    hr = hh["openingHours"]
                    if hr["from1"]:
                        times = f"{_f(hr['from1']['hourOfDay'])}:{_f(hr['from1']['minute'])} - {_f(hr['to1']['hourOfDay'])}:{_f(hr['to1']['minute'])}"
                    else:
                        times = "closed"
                    hours.append(f"{hr['dayType']}: {times}")
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["locationId"],
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    zip_postal=_["zipCode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="Hungury",
                    phone=_["telephone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
