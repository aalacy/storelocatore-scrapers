from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "wingmachine_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://wingmachine.com/location.php"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var myLatlng =")[1:]
        for loc in loclist:
            address = loc.split('icon: pin,cntent: "')[1].split('"}', 1)[0]
            address = BeautifulSoup(address, "html.parser")
            address = address.get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            location_name = address[0]
            phone = address[2]
            address = address[1].split(",")
            city = address[0]
            state = address[1]
            zip_postal = "<MISSING>"
            latitude, longitude = loc.split("LatLng(")[1].split(")", 1)[0].split(",")
            hours = loc.split("('#hours_block').html('")[1].split("');", 1)[0]
            hours = BeautifulSoup(hours, "html.parser")
            day_list = hours.findAll("dt")
            time_list = hours.findAll("dd")
            hours_of_operation = ""
            for d, t in zip(day_list, time_list):
                day = d.text
                time = t.text
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + time + " ".strip()
                )
            yield SgRecord(
                locator_domain="https://wingmachine.com/",
                page_url="https://wingmachine.com/location.php",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="CA",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude.strip(),
                longitude=longitude.strip(),
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
