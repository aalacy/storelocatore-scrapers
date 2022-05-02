from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=10
    )
    for lat, lng in search:
        api = f"https://spatial.virtualearth.net/REST/v1/data/91bdba818b3c4f5e8b109f223ac4a9f0/Filialdaten-NIE/Filialdaten-NIE?$select=*,__Distance&$filter=Adresstyp%20eq%201&key=AkeGPHUAkt63PHcPYgWMYeSXRmUHkFqe4ql0f8XDSEdG-PnxQ22O6gL9rTAdQ-WV&$format=json&spatialFilter=nearby({lat},{lng},15)"
        r = session.get(api, headers=headers)
        try:
            js = r.json()["d"]["results"]
        except:
            continue

        for j in js:
            street_address = j.get("AddressLine") or ""
            city = j.get("Locality") or ""
            postal = j.get("PostalCode")

            if f", {city}" in street_address:
                street_address = street_address.split(f", {city}")[0].strip()
            country_code = "GB"
            store_number = j.get("EntityID")
            location_name = j.get("ShownStoreName") or city
            latitude = j.get("Latitude")
            longitude = j.get("Longitude")

            _tmp = []
            source = j.get("OpeningTimes") or "<html>"
            tree = html.fromstring(source)
            hours = tree.xpath("//text()")

            for h in hours:
                if not h.strip():
                    continue
                if "Day" in h:
                    break
                _tmp.append(h.strip())

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = page_url = "https://www.lidl-ni.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
