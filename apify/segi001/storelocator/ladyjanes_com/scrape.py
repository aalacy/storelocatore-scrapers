import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ladyjanes.com/"
    api = "https://www.ladyjanes.com/location/getLocationsBySearch"

    s = SgRequests()

    search = DynamicZipSearch(country_codes=[SearchableCountries.USA])

    for postcode in search:
        p = {"search": postcode}
        try:
            locs = json.loads(s.post(api, data=p).text)["data"]["visibleLocations"]
        except:
            continue
        for loc in locs:
            st = locs[loc]
            if st["wait_time"] == "Coming Soon":
                pass
            else:
                store_name = st["api"]["name"]
                address = st["street_address"]
                state = st["state"]
                city = st["city"]
                store_zip = st["api"]["address"].strip().split(" ")[-1]
                lat = st["api"]["lat"]
                lng = st["api"]["lng"]
                search.found_location_at(lat, lng)
                store_number = st["id"]
                phone = st["phone"]
                hours = "Monday-Thursday : {}, Friday : {}, Saturday : {}, Sunday : {}".format(
                    st["monday_thursday"], st["friday"], st["saturday"], st["sunday"]
                )

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url="https://www.ladyjanes.com/locations",
                    location_name=store_name,
                    street_address=address,
                    city=city,
                    state=state,
                    zip_postal=store_zip,
                    country_code="US",
                    store_number=store_number,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
