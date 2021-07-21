import usaddress
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "yifangteausa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():

    if True:
        url = "https://yifangteausa.com/locations"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"data-ux": "ContentCard"})
        for loc in loclist[:-3]:
            temp1 = (
                loc.find("div", {"data-ux": "ContentCardText"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            temp = temp1[1:6]
            location_name = loc.find("div", {"data-ux": "Block"}).find("h4").text
            if "Coming Soon" in location_name:
                continue
            if len(temp) == 1 or not temp:
                continue
            if "Opening Hours:" in temp[0]:
                address = temp1[0]
            else:
                address = temp[0]
            if "DoorDash" in temp[-1]:
                del temp[-1]
                if "DoorDash" or "Shopping Mall" in temp[-1]:
                    del temp[-1]
            if "Shopping Mall" in temp[0]:
                address = temp[1]
            hours_of_operation = temp[-2] + " " + temp[-1]
            hours_of_operation = (
                hours_of_operation.replace("Opening Hours:", "")
                .replace("2020 Temporary \xa0Hours:", "")
                .replace("Hours:", "")
                .replace("Opening Hours", "")
            )
            if "Shopping Mall Hours" in hours_of_operation:
                hours_of_operation = "<MISSING>"
            if len(temp) > 2:
                if "Mon" in temp[-3]:
                    hours_of_operation = temp[-3] + " " + temp[-2] + " " + temp[-1]
                    hours_of_operation = (
                        hours_of_operation.replace("Opening Hours:", "")
                        .replace("2020 Temporary \xa0Hours:", "")
                        .replace("Hours:", "")
                        .replace("Opening Hours", "")
                    )
            if "Tel:" in temp[1]:
                if len(temp[1]) < 5:
                    phone = temp[2]
                else:
                    phone = temp[1].split("Tel:")[1]
                    phone = "".join(phone.split()).strip()
                    phone = phone.encode("ascii", "ignore")
                    phone = phone.decode("utf-8")
            else:
                phone = "<MISSING>"

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
            log.info(location_name)
            yield SgRecord(
                locator_domain="https://yifangteausa.com/",
                page_url="https://yifangteausa.com/locations",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
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
