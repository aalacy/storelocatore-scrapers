from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.specsavers.co.nz"
base_url = "https://liveapi.yext.com/v2/accounts/me/locations?api_key=be3071a8d4114a2731d389952dd3eeb2&v=20211109&latitude=-33.76864616305005&longitude=151.2644012882174&radius=2000&limit=50&country=nz&offset={}"
days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


def fetch_data():
    with SgRequests() as session:
        offset = 0
        while True:
            locations = session.get(base_url.format(offset), headers=_headers).json()[
                "response"
            ]["locations"]
            if locations:
                offset += 50
            else:
                break
            for _ in locations:
                hours = []
                if _["hours"]:
                    for hh in _["hours"].split(","):
                        day = int(hh.split(":")[0]) - 1
                        hr = f"{hh.split(':')[1]}:{hh.split(':')[2]} am - {hh.split(':')[3]}:{hh.split(':')[4]} pm"
                        hours.append(f"{days[day]}: {hr}")
                if _.get("displayLat"):
                    latitude = _["displayLat"]
                    longitude = _["displayLng"]
                elif _.get("yextDisplayLat"):
                    latitude = _["yextDisplayLat"]
                    longitude = _["yextDisplayLng"]
                street_address = _["address"]
                if _.get("address2"):
                    street_address += " " + _["address2"]
                yield SgRecord(
                    page_url=_["websiteUrl"],
                    location_name=_["locationName"],
                    street_address=street_address,
                    city=_["city"],
                    zip_postal=_["zip"],
                    country_code=_["countryCode"],
                    phone=_["phone"],
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
