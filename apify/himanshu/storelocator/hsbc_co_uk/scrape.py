from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("hsbc_co_uk")
session = SgRequests()


def fetch_data():
    r = session.get("https://api.hsbc.com/open-banking/v2.2/atms").json()
    attr = r["data"][0]["Brand"][0]["ATM"]

    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    for data in attr:
        try:
            location_name = data["Location"]["Site"]["Name"]
        except:
            location_name = "<MISSING>"

        try:
            street_address = data["Location"]["PostalAddress"]["StreetName"]
        except:
            street_address = "<MISSING>"

        try:
            if data["Location"]["PostalAddress"]["TownName"] == "3":
                city = "<MISSING>"
            else:
                city = data["Location"]["PostalAddress"]["TownName"]
        except:
            city = "<MISSING>"

        state = "<MISSING>"
        try:
            zipp = data["Location"]["PostalAddress"]["PostCode"]
        except:
            zipp = "<MISSING>"

        try:
            country_code = data["Location"]["PostalAddress"]["Country"]
        except:
            country_code = "<MISSING>"

        store_number = data["Identification"]
        phone = "<MISSING>"
        location_type = "ATM"
        try:
            latitude = data["Location"]["PostalAddress"]["GeoLocation"][
                "GeographicCoordinates"
            ]["Latitude"]
        except:
            latitude = "<MISSING>"

        try:
            longitude = data["Location"]["PostalAddress"]["GeoLocation"][
                "GeographicCoordinates"
            ]["Longitude"]
        except:
            longitude = "<MISSING>"

        hours_of_operation = "24 HOURS"
        page_url = "<MISSING>"

        yield SgRecord(
            locator_domain="https://hsbc.co.uk/",
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
    r1 = session.get("https://api.hsbc.com/open-banking/v2.1/branches").json()
    attr1 = r1["data"][0]["Brand"][0]["Branch"]

    for data1 in attr1:

        try:
            location_name = data1["Name"]
        except:
            location_name = "<MISSING>"

        try:
            street_address = (
                data1["PostalAddress"]["BuildingNumber"]
                + " "
                + data1["PostalAddress"]["StreetName"]
            )
        except:
            street_address = "<MISSING>"

        try:
            city = data1["PostalAddress"]["TownName"]
        except:
            city = "<MISSING>"

        try:
            state = "<MISSING>"
        except:
            state = "<MISSING>"

        try:
            zipp = data1["PostalAddress"]["PostCode"]
        except:
            zipp = "<MISSING>"

        try:
            country_code = data1["PostalAddress"]["Country"]
        except:
            country_code = "<MISSING>"

        try:
            store_number = data1["Identification"]
        except:
            store_number = "<MISSING>"

        try:
            phone = data1["ContactInfo"][0]["ContactContent"]
        except:
            phone = "<MISSING>"

        try:
            location_type = data1["Type"] + " Branch"
        except:
            location_type = "<MISSING>"

        try:
            latitude = data1["PostalAddress"]["GeoLocation"]["GeographicCoordinates"][
                "Latitude"
            ]
        except:
            latitude = "<MISSING>"

        try:
            longitude = data1["PostalAddress"]["GeoLocation"]["GeographicCoordinates"][
                "Longitude"
            ]
        except:
            longitude = "<MISSING>"

        try:
            hours_list = []
            availability = data1["Availability"]["StandardAvailability"]["Day"]
            for week in availability:
                for time in week["OpeningHours"]:
                    hours_list.append(
                        week["Name"]
                        + ": "
                        + time["OpeningTime"].replace(".000Z", "").strip()
                        + " - "
                        + time["ClosingTime"].replace(".000Z", "").strip()
                    )

            hours_of_operation = "; ".join(hours_list).strip()
        except:
            hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"

        yield SgRecord(
            locator_domain="https://hsbc.co.uk/",
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


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
