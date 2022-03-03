from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape import sgpostal as parser
import json

session = SgRequests()
website = "gogamexchange_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
DOMAIN = "https://www.gogamexchange.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://cdn.storelocatorwidgets.com/json/7466089a00db248cead92022a5760e27?callback=slw&_=1632749515966"
        stores_req = session.get(url, headers=headers).text
        stores_req = stores_req.split('],"stores"')[1]
        stores_req = '{"stores"' + stores_req
        stores_req = stores_req.rstrip(")")
        contents = json.loads(stores_req)
        for loc in contents["stores"]:
            storeid = loc["storeid"]
            title = loc["name"]
            address = loc["data"]["address"]
            address = address.replace("\n", " ").strip()
            parsed = parser.parse_address_usa(address)
            street1 = (
                parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
            )
            street = (
                (street1 + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else street1
            )
            city = parsed.city if parsed.city else "<MISSING>"
            state = parsed.state if parsed.state else "<MISSING>"
            pcode = parsed.postcode if parsed.postcode else "<MISSING>"
            link = loc["data"]["website"]
            phone = loc["data"]["phone"]
            hours = (
                "Mon:"
                + loc["data"]["hours_Monday"]
                + " Tues: "
                + loc["data"]["hours_Tuesday"]
                + " Wed: "
                + loc["data"]["hours_Wednesday"]
                + " Thurs: "
                + loc["data"]["hours_Thursday"]
                + " Fri: "
                + loc["data"]["hours_Friday"]
                + " Sat: "
                + loc["data"]["hours_Saturday"]
                + "Sun:  "
                + loc["data"]["hours_Sunday"]
            )
            lat = loc["data"]["map_lat"]
            lng = loc["data"]["map_lng"]
            state = state.strip()
            if state == "<MISSING>":
                pcode = pcode.strip()
                pcode = list(pcode)
                state = pcode[0] + pcode[1]
                pcode = pcode[2] + pcode[3] + pcode[4] + pcode[5] + pcode[6]
            if pcode == "<MISSING>":
                state = address.split(",")[-1].strip()
                state = list(state)
                pcode = state[2] + state[3] + state[4] + state[5] + state[6]
                state = state[0] + state[1]
            if state == "Rock":
                city = "Little Rock"
                state = "AR"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link.strip(),
                location_name=title.strip(),
                street_address=street.strip(),
                city=city,
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=storeid,
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE},
                fail_on_empty_id=True,
            )
            .with_truncate(SgRecord.Headers.LATITUDE, 3)
            .with_truncate(SgRecord.Headers.LONGITUDE, 3)
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
