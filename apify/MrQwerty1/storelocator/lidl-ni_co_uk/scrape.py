import re
from bs4 import BeautifulSoup
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_api_url(session):
    response = session.get("https://www.lidl-ni.co.uk/")
    soup = BeautifulSoup(response.text)
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string:
            newline_removed = re.sub(r"\n", "", script.string)
            result = re.search(
                r'window\.storesearchConfig\s*=\s*.*path:\s*"(.*)"', newline_removed
            )
            config = session.get(f"https://www.lidl-ni.co.uk{result.group(1)}").json()[
                "storesearch"
            ]
            return config["sourceUrl"], config["key"]


def fetch_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], max_search_distance_miles=25
    )
    url, key = fetch_api_url(session)
    for lat, lng in search:
        params = {
            "$select": "*,__Distance",
            "$format": "json",
            "spatialFilter": f"nearby({lat},{lng},1000)",
            "key": key,
        }
        r = session.get(url, params=params, headers=headers)
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

            yield row


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
        for row in fetch_data():
            writer.write_row(row)
