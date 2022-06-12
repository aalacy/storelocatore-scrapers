import usaddress
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


log = sglog.SgLogSetup().get_logger(logger_name="fasttrackurgentcare")


def fetch_data():
    base_url = "https://www.fasttrackurgentcare.com/locations-and-hours/"
    with SgRequests() as session:
        r = session.get(base_url)
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
        soup = BeautifulSoup(r.text, "lxml")
        main = soup.find("div", {"id": "accordionExample"}).find_all(
            "div", {"class": "card"}
        )
        for location in main:
            lat = location.find("button")["data-lat"]
            lng = location.find("button")["data-lng"]
            name = location.find("button")["data-title"]

            st = (
                location.find("button")["data-address"]
                + " "
                + location.find("button")["data-citystzip"]
            )
            a = usaddress.tag(st, tag_mapping=tag)[0]
            address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            zip = a.get("postal")
            state = a.get("state")
            city = a.get("city")
            dt = list(
                location.find(
                    "div", {"class": "card-content text-left"}
                ).stripped_strings
            )
            hours = dt[4] + " " + dt[5]
            phone = dt[3]
            if "Learn" in hours:
                hours = dt[3] + " " + dt[4]
                phone = dt[2]
            page_url = location.find("a", {"class": "btn-sm btn-secondary-sm"})["href"]

            log.info(page_url)
            store_req = session.get(page_url)
            store_sel = lxml.html.fromstring(store_req.text)
            if (
                "coming soon"
                in "".join(store_sel.xpath("//article/h1//text()")).strip().lower()
            ):
                continue

            yield SgRecord(
                locator_domain="https://www.fasttrackurgentcare.com",
                page_url=page_url,
                location_name=name,
                street_address=address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="fasttrackurgentcare",
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
