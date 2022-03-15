from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


def fetch_data(sgw: SgWriter):

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        max_search_distance_miles=5000,
        expected_search_radius_miles=1000,
    )

    for zip_code in search:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        }
        base_url = "https://www.benandjerrys.ca"

        try:
            r = session.get(
                "https://benjerry.where2getit.com/ajax?lang=en_US&xml_request=%3Crequest%3E%20%3Cappkey%3E3D71930E-EC80"
                "-11E6-A0AE-8347407E493E%3C/appkey%3E%20%3Cformdata%20id=%22locatorsearch%22%3E%20%3Cdataview"
                "%3Estore_default%3C/dataview%3E%20%3Climit%3E5000%3C/limit%3E%20%3Cgeolocs%3E%20%3Cgeoloc%3E%20"
                "%3Caddressline%3E"
                + str(zip_code)
                + "%3C/addressline%3E%20%3C/geoloc%3E%20%3C/geolocs%3E%20%3Csearchradius%3E5000%3C"
                "/searchradius%3E%20%3C/formdata%3E%20%3C/request%3E",
                headers=headers,
            )
        except:
            continue

        soup = BeautifulSoup(r.text, "lxml")

        locator_domain = base_url
        location_name = ""
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "benandjerrys"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "https://www.benandjerrys.ca/en/ice-cream-near-me"

        for script in soup.find_all("poi"):

            location_name = script.find("name").text
            street_address = (
                script.find("address1").text + " " + script.find("address2").text
            )
            city = script.find("city").text
            state = script.find("state").text
            zipp = script.find("postalcode").text.replace("'", "")
            if "00000" == zipp:
                zipp = "<MISSING>"
            country_code = script.find("country").text
            latitude = script.find("latitude").text
            longitude = script.find("longitude").text
            phone = script.find("cakephone").text.replace("&#xa0;", "")
            store_number = script.find("clientkey").text
            icon = script.find("icon").text.strip()
            if "Store" in icon:
                location_type = "Store"
            elif "shop" in icon.lower() or "default" in icon:
                location_type = "Scoop shops"
            else:
                continue

            if len(location_name.strip()) == 0:
                location_name = "<MISSING>"

            if len(street_address.strip()) == 0:
                street_address = "<MISSING>"

            if len(city.strip()) == 0:
                city = "<MISSING>"

            if len(state.strip()) == 0:
                state = "<MISSING>"

            if len(zipp.strip()) == 0:
                zipp = "<MISSING>"

            if len(country_code.strip()) == 0:
                country_code = "US"

            if len(latitude.strip()) == 0:
                latitude = "<MISSING>"

            if len(longitude.strip()) == 0:
                longitude = "<MISSING>"

            if len(phone.strip()) == 0:
                phone = "<MISSING>"

            if (
                len(script.find("sunday").text) > 0
                or len(script.find("monday").text) > 0
                or len(script.find("tuesday").text) > 0
                or len(script.find("wednesday").text) > 0
                or len(script.find("thursday").text) > 0
                or len(script.find("friday").text) > 0
                or len(script.find("saturday").text) > 0
            ):
                hours_of_operation = (
                    "Sunday : "
                    + script.find("sunday").text
                    + ", "
                    + "Monday : "
                    + script.find("monday").text
                    + ", "
                    + "Tuesday : "
                    + script.find("tuesday").text
                    + ", "
                    + "Wednesday : "
                    + script.find("wednesday").text
                    + ", "
                    + "Thursday : "
                    + script.find("thursday").text
                    + ", "
                    + "Friday : "
                    + script.find("friday").text
                    + ", "
                    + "Saturday : "
                    + script.find("saturday").text
                )
            else:
                hours_of_operation = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
