import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "thaibbquc_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://thaibbquc.com/"
MISSING = "<MISSING>"


def parse_address(address):
    address = address.replace(",", " ").replace("(IN THE HEART OF THAI TOWN)", "")
    address = usaddress.parse(address)
    i = 0
    street_address = ""
    city = ""
    state = ""
    zip_postal = ""
    while i < len(address):
        temp = address[i]
        if (
            temp[1].find("Address") != -1
            or temp[1].find("Street") != -1
            or temp[1].find("Recipient") != -1
            or temp[1].find("Occupancy") != -1
            or temp[1].find("BuildingName") != -1
            or temp[1].find("USPSBoxType") != -1
            or temp[1].find("USPSBoxID") != -1
        ):
            street_address = street_address + " " + temp[0]
        if temp[1].find("PlaceName") != -1:
            city = city + " " + temp[0]
        if temp[1].find("StateName") != -1:
            state = state + " " + temp[0]
        if temp[1].find("ZipCode") != -1:
            zip_postal = zip_postal + " " + temp[0]
        i += 1
    return street_address, city, state, zip_postal


def fetch_data():
    if True:
        url = "http://www.thaibbquc.com/location.html"
        r = session.get(url, headers=headers)
        loclist = BeautifulSoup(r.text, "html.parser")
        loclist = loclist.findAll("table")[-2].findAll("p")
        country_code = "US"
        for loc in loclist[:-1]:
            hours_of_operation = (
                loclist[-1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("HOURS OF OPERATION:", "")
                .replace("\n", " ")
                .replace("                            ", " ")
                .replace("*", "")
            )
            temp = loc.get_text(separator="|", strip=True).split("|")
            if len(temp) < 3:
                continue
            temp_2 = loc.findAll("strong")
            if len(temp_2) > 1:
                if loc.text.count("THAI") > 1:
                    temp_list = (
                        str(loc).replace("<strong><br/></strong>", "").split("THAI")
                    )
                    for t in temp_list[1:]:
                        t = BeautifulSoup(t, "html.parser")
                        t = t.get_text(separator="|", strip=True).split("|")
                        if "DELIVERY AVAILABLE" in t[-1]:
                            del t[-1]
                        location_name = "THAI " + t[0]
                        if "THAI ORIGINAL BBQ on 3RD STREET" in t[1]:
                            del t[1]
                        if len(t) > 4:
                            address = t[1] + " " + t[2]
                            phone = t[3].replace("TEL1:", "").split("TEL2:")[0]
                        else:
                            address = t[1]
                            phone = t[2].replace("TEL:", "").split("FAX")[0]
                        street_address, city, state, zip_postal = parse_address(address)
                        log.info(location_name)
                        yield SgRecord(
                            locator_domain=DOMAIN,
                            page_url=url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip_postal,
                            country_code=country_code,
                            store_number=MISSING,
                            phone=phone,
                            location_type=MISSING,
                            latitude=MISSING,
                            longitude=MISSING,
                            hours_of_operation=hours_of_operation,
                        )
            if "HOURS OF OPERATION" in loc.text:
                location_name = temp[0]
                address = temp[1] + " " + temp[2]
                phone = temp[3].replace("TEL:", "").split("FAX")[0]
                hours_of_operation = temp[-3] + " " + temp[-2] + " " + temp[-1]
                hours_of_operation = hours_of_operation.replace("SAT", "SAT ").replace(
                    "SUN", "SUN "
                )
            else:
                if "(IN THE HEART OF THAI TOWN)" in temp[1]:
                    del temp[1]
                location_name = temp[0]
                address = temp[1]
                phone = temp[2].replace("TEL:", "").split("FAX")[0]
            street_address, city, state, zip_postal = parse_address(address)
            log.info(location_name)
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
