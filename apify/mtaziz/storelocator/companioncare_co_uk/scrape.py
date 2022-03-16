from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl
import json

logger = SgLogSetup().get_logger("companioncare_co_uk")
DOMAIN = "https://www.companioncare.co.uk"
URL_LOCATION = "https://www.companioncare.co.uk/find-a-practice/"

MISSING = "<MISSING>"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "origin": "https://www.companioncare.co.uk",
    "referer": "https://www.companioncare.co.uk/find-a-practice/",
    "authority": "api.woosmap.com",
}
session = SgRequests()


def fetch_data():
    API_ENDPOINT_URL = "https://api.woosmap.com/stores/"
    API_KEY = "woos-85314341-5e66-3ddf-bb9a-43b1ce46dbdc"
    for x in range(1, 900):
        url = f"{API_ENDPOINT_URL}{str(x)}?key={API_KEY}"
        r = session.get(url, headers=headers, timeout=180)
        if r.status_code != 200:
            logger.info("Website could not be reached : 404 Error Code Experienced")
            continue
        logger.info(f"\nPulling the data from {x}: {url} \n")
        data_json = json.loads(r.text)
        data_props = data_json["properties"]
        locator_domain = DOMAIN
        page_url = data_props["contact"]["website"] or MISSING

        # Two page URLs are found to be invalid so to fix it - manually hard-coded
        if "/link/a5a2ab067e6943ceabb8c383540b3b8e.aspx" in page_url:
            page_url = "https://www.vets4pets.com/practices/vets-in-plymouth/vets4pets-plymouth/"
        if "/link/ca07e39e80c6455fb3b8d6ec43277d29.aspx" in page_url:
            page_url = "https://www.vets4pets.com/practices/vets4pets-bridgend/"

        # Location Name
        location_name = data_props["name"] or MISSING

        # Address properties from JSON data
        address = data_props["address"]
        raw_address1 = f'{", ".join(address["lines"])}, {address["city"]}, {address["zipcode"]}, {address["country_code"]}'
        logger.info(f"\nRaw Address: {raw_address1}\n")
        raw_address1 = raw_address1.replace("None,", "")
        raw_address1 = " ".join(raw_address1.split())

        # Parse the raw address obtained from JSON address data using sgpostal
        pa = parse_address_intl(raw_address1)

        # Street Address from JSON also contains city or town names which is fixed using sgpostal

        street_address = pa.street_address_1
        street_address = street_address.replace("Inside Pets At Home ", "")
        street_address = street_address if street_address else MISSING
        city = address["city"] or MISSING

        # 71 City names found to be missing to deal with we can use sgpostal
        # Missing city names will be obtained from parsed address using sgpostal

        if MISSING in city:
            city = pa.city
        else:
            city = city

        if city == "(sat nav YO31 9BF)":
            city = "York"

        if city == "5Fl":
            city = "Telford"

        if city == " St. Annes-on-Sea":
            city = "Lytham St Annes"

        if city == "Park":
            city = MISSING

        # State name not found
        state = MISSING

        # Zip Code
        zip_postal = address["zipcode"]
        if zip_postal:
            zip_postal = zip_postal.strip()
        else:
            zip_postal = MISSING

        # Country Code
        country_code = address["country_code"]
        if country_code:
            country_code = country_code.strip()
        else:
            country_code = MISSING

        # Store Number
        store_number = data_props["store_id"]
        if store_number:
            store_number = store_number.strip()
        else:
            store_number = MISSING

        if "Unit 3, 31 Stockport Rd, Denton, M34 6DB, GB" in raw_address1:
            city = "Denton"

        # Phone
        phone = data_props["contact"]["phone"]
        if phone:
            phone = phone.strip()
        else:
            phone = MISSING

        types = data_props["types"]
        if types:
            location_type = ", ".join(types).strip()
        else:
            location_type = MISSING

        # Latitude and Longitude
        data_geo = data_json["geometry"]
        try:
            latitude = data_geo["coordinates"][-1]
        except:
            latitude = MISSING

        # Longitude
        try:
            longitude = data_geo["coordinates"][0]
        except:
            longitude = MISSING

        # Hours of Operation
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hoo = data_props["weekly_opening"]
        try:
            hoo_list = []
            for i in range(1, 8):
                i_str = str(i)
                j = i - 1
                if hoo[i_str]["hours"]:
                    day = f'{weekdays[j]} {hoo[i_str]["hours"][0]["start"]} - {hoo[i_str]["hours"][0]["end"]}'
                    hoo_list.append(day)
                else:
                    day = f"{weekdays[j]} Closed"
                    hoo_list.append(day)

            hours_of_operation = "; ".join(hoo_list)
        except:
            hours_of_operation = MISSING

        # Raw address helps crawl writer to understand better
        raw_address = raw_address1 if raw_address1 else MISSING

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
