from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch


def get_countries():
    countries = []
    api = "https://www.lefties.com/itxrest/2/catalog/store?brandId=9&appId=1"
    r = session.get(api, headers=headers)
    js = r.json()["stores"]
    for j in js:
        _id = j.get("id")
        key = j.get("countryCode") or ""
        countries.append((_id, key.lower()))

    return countries


def fetch_data(sgw: SgWriter):
    params = get_countries()
    for p in params:
        _id, cc = p
        if cc == "ic":
            continue
        search = DynamicGeoSearch(country_codes=[cc], expected_search_radius_miles=100)
        for lat, lng in search:
            country = search.current_country().upper()
            api = f"https://www.lefties.com/itxrest/2/bam/store/{_id}/physical-store?favouriteStores=false&lastStores=false&closerStores=false&latitude={lat}&longitude={lng}&receiveEcommerce=false&countryCode={country}&languageId=-1&appId=1"
            r = session.get(api, headers=headers)
            js = r.json()["closerStores"]

            for j in js:
                location_name = j.get("name")
                page_url = j.get("url")
                lines = j.get("addressLines") or []
                street_address = " ".join(lines)
                street_address = street_address.strip()
                if "(" in street_address:
                    street_address = street_address.split("(")[0].strip()
                if street_address.endswith(","):
                    street_address = street_address[:-1]
                city = j.get("city") or ""
                postal = j.get("zipCode") or ""
                if str(postal) == "0":
                    postal = SgRecord.MISSING
                country = j.get("countryCode")

                phones = j.get("phones") or []
                phone = SgRecord.MISSING
                if phones:
                    phone = phones.pop(0)
                phone = phone.replace("-", "").strip()
                latitude = j.get("latitude")
                longitude = j.get("longitude")
                location_type = j.get("nameStoreType")
                store_number = j.get("id")

                _tmp = []
                try:
                    hours = j["openingHours"]["schedule"]
                except:
                    hours = []
                days = [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]

                for h in hours:
                    try:
                        t = h["timeStripList"][0]
                    except:
                        t = dict()
                    start = t.get("initHour")
                    end = t.get("endHour")
                    week = h.get("weekdays") or []
                    for w in week:
                        day = days[w - 1]
                        _tmp.append(f"{day}: {start}-{end}")

                hours_of_operation = ";".join(_tmp)
                raw_address = " ".join(f"{street_address} {city} {postal}".split())

                row = SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    zip_postal=postal,
                    country_code=country,
                    location_type=location_type,
                    store_number=store_number,
                    phone=phone,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.lefties.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
