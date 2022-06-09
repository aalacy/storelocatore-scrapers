from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgrecord_id import SgRecordID


def fetch_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=None,
        max_search_results=None,
    )

    for llat, llng in search:
        locator_domain = "https://www.chevrolet.com/"

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://www.chevrolet.com/dealer-locator",
            "clientapplicationid": "quantum",
            "content-type": "application/json; charset=utf-8",
            "locale": "en-US",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "max-age=0",
        }

        params = {
            "desiredCount": "25",
            "distance": "500",
            "makeCodes": "001",
            "serviceCodes": "",
            "latitude": str(llat),
            "longitude": str(llng),
            "searchType": "latLongSearch",
        }

        r = session.get(
            "https://www.chevrolet.com/bypass/pcf/quantum-dealer-locator/v1/getDealers",
            headers=headers,
            params=params,
        )

        js = r.json()["payload"]["dealers"]

        for j in js:
            a = j.get("address")
            page_url = "https://www.chevrolet.com/dealer-locator"
            name = j.get("dealerName")
            add = f"{a.get('addressLine1')} {a.get('addressLine2')} {a.get('addressLine3')}".strip()
            city = a.get("cityName") or "<MISSING>"
            state = a.get("region") or "<MISSING>"
            zc = a.get("postalCodeFormatted") or "<MISSING>"
            country = "US"
            phone = j.get("generalContact").get("phone1") or "<MISSING>"
            phone = str(phone).replace(",", "").strip()
            lat = j.get("geolocation").get("latitude") or "<MISSING>"
            lng = j.get("geolocation").get("longitude") or "<MISSING>"
            store = j.get("dealerCode") or "<MISSING>"
            typ = "<MISSING>"
            days = {
                1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Saturday",
                7: "Sunday",
            }

            hours = (
                j.get("generalOpeningHour")
                or j.get("serviceOpeningHour")
                or j.get("partsOpeningHour")
            )

            hours_of_operation_tmp = []

            for hour in hours:
                for day in hour.get("dayOfWeek"):
                    hours_of_operation_tmp.append(
                        f"{days[day]} {hour.get('openFrom')}-{hour.get('openTo')}"
                    )
            hours = "; ".join(hours_of_operation_tmp)

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                },
                fail_on_empty_id=True,
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
