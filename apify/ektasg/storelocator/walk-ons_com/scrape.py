import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "walk-ons_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://walk-ons.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url_list = []
        url = "https://walk-ons.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "locationItem col-md-6 text-left"})
        for loc in loclist:
            temp_loc = loc.find("div").findAll("div")
            temp_var = temp_loc[0].find("a")
            try:
                page_url = temp_var["href"]
                if page_url in url_list:
                    page_url = MISSING
                url_list.append(page_url)
            except:
                break
            location_name = temp_var.find("span", {"class": "locationName"}).text
            log.info(location_name)
            latitude = MISSING
            longitude = MISSING
            phone = temp_loc[3].text
            address = (
                temp_loc[1].get_text(separator="|", strip=True).replace("|", "")
                + " "
                + temp_loc[2].get_text(separator="|", strip=True).replace("|", "")
            )
            if page_url:
                r = session.get(page_url, headers=headers)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "html.parser")
                    latitude = str(soup).split("lat: ", 1)[1].split(",", 1)[0]
                    longitude = str(soup).split("lng: ", 1)[1].split(",", 1)[0]
            if "Hours" in loc.text:
                hours_of_operation = (
                    str(loc).split("Hours</strong></div>")[1].split("</div>")[0]
                )
                hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
                hours_of_operation = hours_of_operation.get_text(
                    separator="|", strip=True
                ).replace("|", " ")
            else:
                hours_of_operation = (
                    soup.find("table")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Day of the Week Hours", "")
                )
            country_code = "US"
            address = address.replace(",", " ")
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
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
