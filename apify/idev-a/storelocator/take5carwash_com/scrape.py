from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Host": "dbrgenipc.interplay.iterate.ai",
    "Origin": "https://www.take5carwash.com",
    "Referer": "https://www.take5carwash.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.take5carwash.com"
base_url = "https://www.take5carwash.com/_next/static/chunks/pages/contact-forms/Form1-a5f0ab6bedb62f90fca3.js"
json_url = "https://dbrgenipc.interplay.iterate.ai/api/v1/carwash/allstores"


def fetch_data():
    with SgRequests() as session:
        _headers["apikey"] = (
            session.get(base_url).text.split("apiKey:")[1].split("}")[0].strip()[1:-1]
        )
        pageload = {"lat": "35.562", "lng": "-77.4045"}
        locations = session.post(json_url, headers=_headers, json=pageload).json()[
            "store"
        ]
        for _ in locations:
            page_url = f"https://www.take5carwash.com/locations/{_['store_state'].lower().replace(' ','-')}/{_['store_city'].lower().replace(' ','-')}/{_['store_id']}/"
            hours = []
            for day, hh in _.get("hours", {}).items():
                times = "closes"
                if hh.get("is_open"):
                    times = f"{hh['open']} - {hh['close']}"
                hours.append(f"{day}: {times}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_id"],
                location_name=_["store_name"],
                street_address=_["store_address"],
                city=_["store_city"],
                state=_["store_state"],
                zip_postal=_["store_postcode"],
                latitude=_["store_lat"],
                longitude=_["store_long"],
                country_code="US",
                phone=_["store_phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["geo_address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
