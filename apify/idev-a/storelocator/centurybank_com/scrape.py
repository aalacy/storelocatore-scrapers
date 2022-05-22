from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "www.easternbank.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.easternbank.com/"
base_url = "https://www.easternbank.com/locations?geolocation_geocoder_google_geocoding_api=81523&geolocation_geocoder_google_geocoding_api_state=1&field_location_hours_day=&field_location_hours_starthours=&field_location_hours_endhours=&proximity=50"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.location-map-list div.views-form div.views-row"
        )
        for _ in locations:
            raw_address = " ".join(_.select_one("p.address").stripped_strings)
            street_address = _.select_one(".address-line1").text.strip()
            if _.select_one("span.address-line2"):
                street_address += " " + _.select_one("span.address-line2").text.strip()

            phone = ""
            if _.select_one("div.views-field-field-location-phone-number"):
                phone = _.select_one(
                    "div.views-field-field-location-phone-number"
                ).text.strip()

            hours = []
            for hh in _.select(
                "div.views-field-field-location-hours div.office-hours div.office-hours__item"
            ):
                hours.append(" ".join(hh.stripped_strings))

            if not hours:
                hours = (
                    _.select_one(
                        "div.views-field-field-location-services div.field-content"
                    )
                    .text.split(",")[0]
                    .strip()
                )

            name = list(_.select_one("div.map-location-title").stripped_strings)
            yield SgRecord(
                page_url=base_url,
                location_name=name[1],
                street_address=street_address,
                city=_.select_one(".locality").text.strip(),
                state=_.select_one(".administrative-area").text.strip(),
                zip_postal=_.select_one(".postal-code").text.strip(),
                latitude=_.select_one("div.location-coordinates")["data-loc-lat"],
                longitude=_.select_one("div.location-coordinates")["data-loc-lng"],
                phone=phone,
                country_code="US",
                location_type=name[-1].replace("(", "").replace(")", "").strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
