from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures

session = SgRequests()


def get_data(zipps, sgw: SgWriter):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    }

    base_url = "https://www.daltile.com"

    r = session.post(
        "https://hosted.where2getit.com/daltile/rest/locatorsearch?like=0.3630849894369319&lang=en_US",
        headers=headers,
        data='{"request":{"appkey":"085E99FA-1901-11E4-966B-82C955A65BB0","formdata":{'
        '"dynamicSearch":true,"false":"0","geoip":false,"dataview":"store_default","limit":1000,'
        '"geolocs":{"geoloc":[{"addressline":"'
        + str(zipps)
        + '","country":"","latitude":"",'
        '"longitude":"","postalcode":'
        + str(zipps)
        + ',"province":"","state":""}]},"order":"PREMIERSTATEMENTSDEALER asc, SHOWROOM asc, LOCATION_RATING::numeric desc nulls last, _distance","searchradius":"1000"}}}',
    )
    json_data = r.json()
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    phone = "<MISSING>"
    location_type = "daltile"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""
    if "collection" in json_data["response"]:

        for address_list in json_data["response"]["collection"]:

            latitude = address_list["latitude"]
            longitude = address_list["longitude"]
            zipp = address_list["postalcode"]
            location_name = address_list["name"]
            city = address_list["city"]
            country_code = address_list["country"]
            location_type = address_list["storetype"]
            if not location_type:
                continue
            if (
                "Dealer" in location_type
                or "Distributor" in location_type
                or "Corporate" in location_type
                or "Tile & Stone" in location_name
            ):
                continue
            state = address_list["state"]
            street_address = address_list["address1"]
            phone = address_list["phone"]
            if street_address is not None:
                if address_list["address2"] is not None:
                    street_address += ", " + address_list["address2"]
                soup_street_address = BeautifulSoup(street_address, "lxml")
                street_address = ", ".join(list(soup_street_address.stripped_strings))
                street_address = str(street_address).replace(",", "").strip()
            else:
                street_address = "<MISSING>"

            if location_name is None or len(location_name) == 0:
                location_name = "<MISSING>"

            if street_address is None or len(street_address) == 0:
                street_address = "<MISSING>"

            if city is None or len(city) == 0:
                city = "<MISSING>"

            if state is None or len(state) == 0:
                state = "<MISSING>"

            if zipp is None or len(zipp) == 0:
                zipp = "<MISSING>"
            else:
                if not any(char.isdigit() for char in zipp):
                    zipp = "<MISSING>"

            if latitude is None or len(latitude) == 0:
                latitude = "<MISSING>"

            if longitude is None or len(longitude) == 0:
                longitude = "<MISSING>"

            if phone is None or len(phone) == 0:
                phone = "<MISSING>"

            is_missing_hours = True
            if (
                address_list["sunday_open"] is not None
                and address_list["sunday_closed"] is not None
            ):
                is_missing_hours = False
                hours_of_operation = (
                    "Sunday "
                    + address_list["sunday_open"]
                    + " - "
                    + address_list["sunday_closed"]
                    + ", "
                )
            else:
                hours_of_operation += "Sunday CLOSED" + ", "

            if (
                address_list["monday_open"] is not None
                and address_list["monday_closed"] is not None
            ):
                is_missing_hours = False
                hours_of_operation += (
                    "Monday "
                    + address_list["monday_open"]
                    + " - "
                    + address_list["monday_closed"]
                    + ", "
                )
            else:
                hours_of_operation += "Monday CLOSED" + ", "

            if (
                address_list["tuesday_open"] is not None
                and address_list["tuesday_closed"] is not None
            ):
                is_missing_hours = False
                hours_of_operation += (
                    "Tuesday "
                    + address_list["tuesday_open"]
                    + " - "
                    + address_list["tuesday_closed"]
                    + ", "
                )
            else:
                hours_of_operation += "Tuesday CLOSED" + ", "

            if (
                address_list["wednesday_open"] is not None
                and address_list["wednesday_closed"] is not None
            ):
                is_missing_hours = False
                hours_of_operation += (
                    "Wednesday "
                    + address_list["wednesday_open"]
                    + " - "
                    + address_list["wednesday_closed"]
                    + ", "
                )
            else:
                hours_of_operation += "Wednesday CLOSED" + ", "

            if (
                address_list["thursday_open"] is not None
                and address_list["thursday_closed"] is not None
            ):
                is_missing_hours = False
                hours_of_operation += (
                    "Thursday "
                    + address_list["thursday_open"]
                    + " - "
                    + address_list["thursday_closed"]
                    + ", "
                )
            else:
                hours_of_operation += "Thursday CLOSED" + ", "

            if (address_list["friday_open"] is not None) and (
                address_list["friday_closed"] is not None
            ):
                is_missing_hours = False
                hours_of_operation += (
                    "Friday "
                    + address_list["friday_open"]
                    + " - "
                    + address_list["friday_closed"]
                    + ", "
                )
            else:
                hours_of_operation += "Friday CLOSED" + ", "

            if (address_list["saturday_open"] is not None) and (
                address_list["saturday_closed"] is not None
            ):
                is_missing_hours = False
                hours_of_operation += (
                    "Saturday "
                    + address_list["saturday_open"]
                    + " - "
                    + address_list["saturday_closed"]
                )
            else:
                hours_of_operation += "Saturday CLOSED"

            hours_of_operation = hours_of_operation.replace("CLOSED - CLOSED", "CLOSED")
            store_number = str(address_list["uid"]).replace("-", "")
            if not store_number:
                store_number = "<MISSING>"
            if is_missing_hours:
                hours_of_operation = "<MISSING>"

            row = SgRecord(
                locator_domain=base_url,
                page_url="https://www.daltile.com/store-locator",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
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
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
