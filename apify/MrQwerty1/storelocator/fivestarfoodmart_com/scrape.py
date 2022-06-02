import usaddress
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import sglog

website = "fivestarfoodmart.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    locator_domain = "https://www.fivestarfoodmart.com/"
    page_url = "https://www.fivestarfoodmart.com/locations/"
    api_url = "https://www.fivestarfoodmart.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxL8pMUdJRKi5JLCpRsjLQUcpJzUsvyVCy0jXUUcpNLIgHSlspGSrVAgD+yBkc"

    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["meta"]

    for j in js:
        line = j.get("address")

        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"

        if city == "<MISSING>" and state == "<MISSING>":
            street_address = line.split(",")[0]
            city = line.split(",")[1].strip()
            state = line.split(",")[-1].strip()
            if city == state:
                city = " ".join(line.split()[2:4]).replace(",", "").strip()
                street_address = street_address.replace(city, "")

        if "," in state:
            state = state.split(",")[0].strip()

        if street_address == "3689 Kentucky 54, Owensboro, KY":
            street_address = "3689 Kentucky 54"
            city = "Owensboro"
            state = "KY"
            postal = "<MISSING>"

        country_code = "US"
        location_name = j.get("title")
        store_number = location_name.split("#")[-1]
        phone = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
