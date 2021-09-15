import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgscrape.pause_resume import CrawlStateSingleton
from sglogging import sglog


def fetch_data(la, ln, sgw: SgWriter):
    data = {
        "request": {
            "appkey": "CFCAC866-ADF8-11E3-AC4F-1340B945EC6E",
            "formdata": {
                "dataview": "store_default",
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "",
                            "country": "",
                            "latitude": la,
                            "longitude": ln,
                        }
                    ]
                },
                "searchradius": "500",
                "where": {
                    "country": {"eq": ""},
                    "off": {"eq": "TRUE"},
                    "out": {"eq": ""},
                },
            },
        }
    }

    r = session.post(
        "https://hosted.where2getit.com/vans/rest/locatorsearch",
        data=json.dumps(data),
    )
    log.info(f"Response Code: {r.status_code}")
    try:
        js = r.json()["response"]["collection"]

        for j in js:
            location_name = j.get("name")
            log.info(f"{location_name}")
            street_address = j.get("address1") or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            postal = j.get("postalcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            if country_code == "US":
                state = j.get("state") or "<MISSING>"
            else:
                state = j.get("province") or "<MISSING>"

            store_number = j.get("clientkey")
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"

            _tmp = []
            days = {
                "m": "monday",
                "t": "tuesday",
                "w": "wednesday",
                "thu": "thursday",
                "f": "friday",
                "sa": "saturday",
                "su": "sunday",
            }
            for k, v in days.items():
                time = j.get(k)
                if time:
                    _tmp.append(f"{v}: {time}")

            hours_of_operation = ";".join(_tmp) or "<MISSING>"
            row = SgRecord(
                page_url=SgRecord.MISSING,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)
    except Exception as e:
        log.error(f"Can't load data from : {la, ln}, Error:{e}")


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)
    session = SgRequests()
    locator_domain = "https://www.vans.com/"
    log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        search = DynamicGeoSearch(
            country_codes=SearchableCountries.ALL, max_search_distance_miles=100
        )
        for lat, lng in search:
            log.info(
                f"Coordinates remaining: {search.items_remaining()} For country: {search.current_country()}"
            )
            log.info(f"Now Checking : {lat},{lng}")
            fetch_data(lat, lng, writer)
