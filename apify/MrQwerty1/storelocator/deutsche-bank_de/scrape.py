import math
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def get_bounds(latitude, longitude, distance):
    radius = 6371

    lat = math.radians(latitude)
    lng = math.radians(longitude)
    parallel_radius = radius * math.cos(lat)

    lat_min = lat - distance / radius
    lat_max = lat + distance / radius
    lon_min = lng - distance / parallel_radius
    lon_max = lng + distance / parallel_radius
    rad2deg = math.degrees

    lat_min = rad2deg(lat_min)
    lng_min = rad2deg(lon_min)
    lat_max = rad2deg(lat_max)
    lng_max = rad2deg(lon_max)

    bounds = f"{lat_max}%2C{lng_max}%2C{lat_min}%2C{lng_min}"
    return bounds


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.GERMANY], expected_search_radius_miles=10
    )

    for lat, lng in search:
        bounds = get_bounds(lat, lng, 15)
        api = f"https://www.deutsche-bank.de/cip/rest/api/url/pfb/content/gdata/Presentation/DbFinder/Home/IndexJson?label=BRANCH&searchTerm=15320&bounds={bounds}"
        r = session.get(api, headers=headers)
        js = r.json()["Items"]

        for j in js:
            a = j.get("Address") or {}
            street_address = a.get("StreetNo")
            state = a.get("District")
            zc = a.get("ZipWithCity") or ""
            try:
                postal = zc.split()[0]
                city = zc.replace(postal, "").strip()
            except:
                city, postal = SgRecord.MISSING, SgRecord.MISSING
            country_code = "DE"
            store_number = j.get("ID")
            location_name = j.get("Title") or ""
            if "SB" in location_name:
                location_type = "ATM"
            else:
                location_type = "Branch"
            page_url = f"https://www.deutsche-bank.de/cip/rest/api/url/filialfinder/Home/Details?id={store_number}"
            phone = a.get("Tel")

            g = j.get("LatLng") or {}
            latitude = g.get("Lat") or ""
            longitude = g.get("Lng") or ""

            _tmp = []
            hours = j.get("OpeningHours") or []
            for h in hours:
                inters = []

                br = h.get("Item1") or {}
                if not br:
                    br = h.get("Item2") or {}
                    day = br.get("Day")
                    if day:
                        _tmp.append(f"{day}: Closed")
                    continue

                day = br.get("Day")
                m = br.get("Morning")
                if m:
                    m_start = m.get("From")
                    m_end = m.get("Until")
                    inters.append(f"{m_start}-{m_end}")

                a = br.get("Afternoon")
                if a:
                    a_start = a.get("From")
                    a_end = a.get("Until")
                    inters.append(f"{a_start}-{a_end}")

                _tmp.append(f'{day}: {"|".join(inters)}')

            hours_of_operation = ";".join(_tmp)
            if location_type == "ATM":
                hours_of_operation = SgRecord.MISSING

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                location_type=location_type,
                phone=phone,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.deutsche-bank.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
