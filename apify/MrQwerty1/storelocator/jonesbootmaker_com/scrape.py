from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(0, 10000, 50):
        params = (
            ("experienceKey", "answers-jonesbootmaker"),
            ("api_key", "9d200ab7c8620cc20297f7dbfd870b45"),
            ("v", "20190101"),
            ("version", "PRODUCTION"),
            ("locale", "en_GB"),
            ("input", ""),
            ("verticalKey", "location"),
            ("limit", "50"),
            ("offset", i),
            ("facetFilters", "{}"),
            ("queryTrigger", "initialize"),
            ("sessionTrackingEnabled", "true"),
            ("sortBys", "[]"),
            ("referrerPageUrl", "https://www.jonesbootmaker.com/"),
            ("source", "STANDARD"),
            ("jsLibVersion", "v1.8.6"),
        )
        api = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query"
        r = session.get(api, headers=headers, params=params)
        js = r.json()["response"]["results"]

        for j in js:
            j = j["data"]
            location_name = j.get("c_answersName")
            page_url = j.get("website")
            phone = j.get("mainPhone")

            a = j.get("address") or {}
            street_address = f'{a.get("line1")} {a.get("line2") or ""}'.strip()
            city = a.get("city")
            postal = a.get("postalCode")
            country = a.get("countryCode")

            g = j.get("yextDisplayCoordinate") or {}
            latitude = g.get("latitude")
            longitude = g.get("longitude")
            store_number = j.get("id")

            _tmp = []
            intervals = j.get("hours") or {}
            for day, interval in intervals.items():
                if interval.get("isClosed"):
                    _tmp.append(f"{day.capitalize()}: Closed")
                    continue

                start = interval["openIntervals"][0]["start"]
                end = interval["openIntervals"][0]["end"]
                _tmp.append(f"{day.capitalize()}: {start} - {end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country,
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 50:
            break


if __name__ == "__main__":
    locator_domain = "https://jonesbootmaker.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
