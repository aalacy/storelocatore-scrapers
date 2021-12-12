# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "saintcinnamon.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
LOCATION_URL = "http://www.saintcinnamon.com/locations.html"
MISSING = SgRecord.MISSING
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}


def get_location_data():
    with SgRequests() as session:
        search_res = session.get(LOCATION_URL, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        # List of countries and states
        state_or_country = search_sel.xpath("//tr//td/p//descendant::strong/text()")
        state_or_country = [" ".join(i.split()) for i in state_or_country]
        state_or_country = [i for i in state_or_country if i]
        log.info(f"List of Countries or States: {state_or_country}")

        # Data cleaning and Sanitization
        data = search_sel.xpath("//td/p//text()")
        data = [" ".join(i.split()) for i in data]
        data = [i for i in data if i]
        data = " ".join(data)
        data_state_country = {}
        locations = []
        list_of_states_or_countries = [
            "ONTARIO",
            "QUEBEC",
            "NEW BRUNSWICK",
            "NOVA SCOTIA",
            "INDONESIA",
            "PHILIPPINES",
        ]
        if list_of_states_or_countries == state_or_country:
            data_state_country["ONTARIO"] = data.split("QUEBEC")[0]
            log.info(f"ON Data: {data_state_country}")
            other_state_or_country = data.split("QUEBEC")[1]
            quebec1 = other_state_or_country.split("NEW BRUNSWICK")[0]
            log.info(f"ON Data: {data_state_country}")

            temp1 = other_state_or_country.split("NEW BRUNSWICK")[1]
            data_state_country["NEW BRUNSWICK"] = temp1.split("NOVA SCOTIA")[0]

            temp2 = temp1.split("NOVA SCOTIA")[1]

            data_state_country["NOVA SCOTIA"] = temp2.split("INDONESIA")[0]
            temp3 = temp2.split("INDONESIA")[1]

            data_state_country["INDONESIA"] = temp3.split("PHILIPPINES")[0]
            temp4 = temp3.split("PHILIPPINES")[1]
            data_state_country["PHILIPPINES"] = temp4.split(
                "Saint Cinnamon Bake Shoppe at La Place"
            )[0]

            quebec2 = (
                "Saint Cinnamon Bake Shoppe at La Place"
                + " "
                + temp4.split("Saint Cinnamon Bake Shoppe at La Place")[1]
            )
            quebec = quebec1 + " " + quebec2
            data_state_country["QUEBEC"] = quebec
        else:

            # If the countries and states (Ontario, Quebec,
            # New Brunswick, Nova Scotia, Indonesia, and Philippines) are not found in page source,
            # the scraper will fail as there may be new state or country.
            # This had to be hard-coded as that the data on the page source
            # is unstructured.
            log.info("Match not found with the listed countries! ")
            raise Exception(
                "Please check the page source if there was new country/state added, if so, the code needs to be updated accordingly!!"
            )

        for k, v in data_state_country.items():
            v1 = list(
                map(
                    lambda x: ("Saint Cinnamo" + x).strip(),
                    v.split("Saint Cinnamo")[1:],
                )
            )
            v1 = [
                location.replace(" at", "")
                .replace("Saint Cinnamon Bake Shoppe", "")
                .strip()
                for location in v1
            ]
            for i in v1:
                if k == "ONTARIO":
                    if not " ON ".lower() in i.lower():
                        j = i + " ON"
                        locations.append(j)
                    else:
                        locations.append(i)

                if k == "QUEBEC":
                    if not " QC ".lower() in i.lower():
                        j = i + " QC"
                        locations.append(j)
                    else:
                        locations.append(i)

                if k == "NEW BRUNSWICK":
                    if not "NEW BRUNSWICK".lower() in i.lower():
                        j = i + " New Brunswick"
                        locations.append(j)
                    else:
                        locations.append(i)

                if k == "NOVA SCOTIA":
                    if not "NOVA SCOTIA".lower() in i.lower():
                        j = i + " Nova Scotia"
                        locations.append(j)
                    else:
                        locations.append(i)

                if k == "INDONESIA":
                    if not "INDONESIA".lower() in i.lower():
                        j = i + " Indonesia"
                        locations.append(j)
                    else:
                        locations.append(i)

                if k == "PHILIPPINES":
                    if not "PHILIPPINES".lower() in i.lower():
                        j = i + " Philippines"
                        locations.append(j)
                    else:
                        locations.append(i)
        return locations


def fetch_data():
    locations_list = get_location_data()
    for location in locations_list:
        page_url = LOCATION_URL
        locator_domain = website
        raw_address = location
        location_name = "Saint Cinnamon Bake Shoppe"
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        if zip is not None and zip == "1405":
            zip = MISSING
            street_address = street_address + " 1405"

        country_code = (
            "CA"
            if ("Indonesia" not in location and "Philippines" not in location)
            else "ID"
            if "Indonesia" in location
            else "PH"
        )

        if city == "C-018":
            city = MISSING
        if city == "Plaza":
            city = MISSING
        if city == "50-1360":
            city = MISSING
        if city == "02-1250":
            city = MISSING

        store_number = MISSING

        location_type = MISSING

        phone = MISSING

        hours_of_operation = MISSING

        latitude = MISSING
        longitude = MISSING

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
