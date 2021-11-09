import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}
    session = SgRequests()

    base_link = "https://russellcellular.com/wp-admin/admin-ajax.php"
    locator_domain = "russellcellular.com"

    found_poi = []

    max_distance = 400

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=max_distance,
        max_search_distance_miles=max_distance,
        granularity=Grain_4(),
    )

    for lat, lng in search:
        # Request post
        payload = {"action": "localpages", "lat": lat, "lon": lng}

        response = session.post(base_link, headers=headers, data=payload)
        base = BeautifulSoup(response.text, "lxml")

        items = base.find_all("div", attrs={"style": "display:none"})
        for item in items:
            location_name = item.strong.text.strip()
            if "soon" in location_name.lower():
                continue

            try:
                geo = json.loads(item["data-gmapping"])
                latitude = geo["latlng"]["lat"]
                longitude = geo["latlng"]["lng"]
                search.found_location_at(latitude, longitude)
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            raw_address = str(item.find(class_="infobox")).split("<br/>")[1:-2]
            street_address = " ".join(raw_address[:-1]).strip()
            if "{" in street_address:
                street_address = street_address[: street_address.find("{")].strip()
            city_line = raw_address[-1].strip().split(",")
            city = city_line[0].strip()
            if street_address + city in found_poi:
                continue
            found_poi.append(street_address + city)
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = item.a.text.strip()
            hours_of_operation = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url="https://russellcellular.com/locations/",
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(
    SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.CITY})
    )
) as writer:
    fetch_data(writer)
