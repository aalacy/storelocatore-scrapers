from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipAndGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ditchwitch")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "http://ditchwitch.com/"
base_url = "https://www.ditchwitch.com/find-a-dealer"


def fetch_records(search):
    total = 0
    for zip, coord in search:
        lat = coord[0]
        lng = coord[1]
        with SgRequests(verify_ssl=False) as http:
            current_country = search.current_country().upper()
            logger.info(f"[{current_country}] {lat, lng}")
            if current_country == "US":
                url = f"https://www.ditchwitch.com/wtgi.php?ajaxPage&ajaxAddress={zip}&lat={lat}&lng={lng}"
            else:
                url = f"https://www.ditchwitch.com/wtgi.php?ajaxPage&ajaxCountryCode={current_country}&ajaxCountryQuery={zip}&ajaxCountryLocal=false&lat={lat}"
            res = http.get(url, headers=headers)
            if res.status_code != 200:
                continue
            locations = res.json()
            if "dealers" in locations:
                if locations["dealers"]:
                    search.found_location_at(lat, lng)

                total += len(locations["dealers"])
                for loc in locations["dealers"]:
                    try:
                        mon = "Mon " + loc["mon_open"] + "-" + loc["mon_close"]
                        tue = "; Tue " + loc["tue_open"] + "-" + loc["tue_close"]
                        wed = "; Wed " + loc["wed_open"] + "-" + loc["wed_close"]
                        thu = "; Thu " + loc["thur_open"] + "-" + loc["thur_close"]
                        fri = "; Fri " + loc["fri_open"] + "-" + loc["fri_close"]
                        sat = "; Sat " + loc["sat_open"] + "-" + loc["sat_close"]
                        sun = "; Sun " + loc["sun_open"] + "-" + loc["sun_close"]
                        hours_of_operation = mon + tue + wed + thu + fri + sat + sun
                    except:
                        hours_of_operation = "<MISSING>"

                    street_address = loc["address1"]
                    if loc["address2"]:
                        street_address += " " + loc.get("address2", "")
                    yield SgRecord(
                        page_url=base_url,
                        store_number=loc["clientkey"],
                        location_name=loc["name"],
                        street_address=street_address,
                        city=loc["city"],
                        state=loc["state"],
                        zip_postal=loc["postalcode"],
                        country_code=loc["country"],
                        phone=loc["phone"],
                        hours_of_operation=hours_of_operation,
                    )

                logger.info(f"found: {len(locations['dealers'])} | total: {total}")


if __name__ == "__main__":
    search = DynamicZipAndGeoSearch(
        country_codes=SearchableCountries.ALL, granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
