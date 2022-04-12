from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://daltile.com/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://hosted.where2getit.com",
        "Connection": "keep-alive",
        "Referer": "https://hosted.where2getit.com/daltile/index.html?premierstatementsdealer=1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    params = {
        "like": "0.9582873315282501",
        "lang": "en_US",
    }

    json_data = {
        "request": {
            "appkey": "085E99FA-1901-11E4-966B-82C955A65BB0",
            "formdata": {
                "dynamicSearch": True,
                "geoip": False,
                "dataview": "store_default",
                "limit": 250,
                "order": "PREMIERSTATEMENTSDEALER asc, SHOWROOM asc, LOCATION_RATING::numeric desc nulls last, _distance",
                "geolocs": {
                    "geoloc": [
                        {
                            "country": "US",
                            "latitude": lat,
                            "longitude": long,
                        },
                    ],
                },
                "searchradius": "250",
                "stateonly": "1",
                "where": {
                    "clientkey": {
                        "distinctfrom": "12345",
                    },
                    "locator": {
                        "eq": "1",
                    },
                    "badge": {
                        "distinctfrom": "Not On Locator",
                    },
                    "daltile": {
                        "eq": "1",
                    },
                    "authorizedfabricator": {
                        "distinctfrom": "1",
                    },
                    "homedepot": {
                        "distinctfrom": "1",
                    },
                    "or": {
                        "showroom": {
                            "eq": "1",
                        },
                        "premierstatementsdealer": {
                            "eq": "1",
                        },
                        "authorizeddealer": {
                            "eq": "1",
                        },
                        "daltileservicecenter": {
                            "eq": "1",
                        },
                        "tile_mosaics": {
                            "eq": "",
                        },
                        "stone_slab_countertops": {
                            "eq": "1",
                        },
                    },
                },
                "true": "1",
                "false": "0",
            },
        },
    }

    r = session.post(
        "https://hosted.where2getit.com/daltile/rest/locatorsearch",
        headers=headers,
        params=params,
        json=json_data,
    )
    try:
        js = r.json()["response"]["collection"]
    except:
        return

    for j in js:

        page_url = "https://www.daltile.com/store-locator"
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalcode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = j.get("storetype")
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        for d in days:
            day = d
            opens = j.get(f"{d}_open")
            closes = j.get(f"{d}_closed")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)
        if hours_of_operation.count("None - None") == 7:
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=10,
        expected_search_radius_miles=10,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
