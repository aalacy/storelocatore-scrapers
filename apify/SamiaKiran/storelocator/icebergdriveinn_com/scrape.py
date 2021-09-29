import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "icebergdriveinn_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://icebergdriveinn.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://icebergdriveinn.com/pages/iceberg-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div",
            {"class": "gf_column gf_col-lg-3 gf_col-md-3 gf_col-sm-6 gf_col-xs-12"},
        )
        for loc in loclist:
            try:
                location_name = loc.find("h3").text
            except:
                continue
            log.info(location_name)
            temp = loc.findAll("div", {"data-gemlang": "en"})
            if len(temp) == 3:
                if "(" in temp[1].text:
                    address = temp[1].text.split("(")
                    phone = "(" + address[1]
                    address = address[0]
                    hours_of_operation = " ".join(
                        x.get_text(separator="|", strip=True).replace("|", " ")
                        for x in temp[2:]
                    )
                else:
                    address = (
                        temp[0].get_text(separator="|", strip=True).replace("|", " ")
                    )
                    phone = temp[1].text
                    address = address[0]
                    hours_of_operation = " ".join(
                        x.get_text(separator="|", strip=True).replace("|", " ")
                        for x in temp[2:]
                    )
            else:
                address = temp[1].get_text(separator="|", strip=True).split("|")
                phone = address[-1]
                address = " ".join(x for x in address[:-1])
                hours_of_operation = MISSING
            phone = phone.replace("Delivery through DoorDash", "")
            address = address.replace(",", " ").replace("99Fillmore", "99 Fillmore")
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

            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
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
