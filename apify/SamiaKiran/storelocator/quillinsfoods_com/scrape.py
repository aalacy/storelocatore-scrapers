import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "quillinsfoods_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    temp = []
    if True:
        url = "https://quillinsfoods.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"id": "menu-footer-locals"}).findAll("li")
        for loc in loclist:
            location_name = loc.find("a")
            page_url = location_name["href"]
            log.info(page_url)
            location_name = location_name.text
            r = session.get(page_url, headers=headers)
            loc = BeautifulSoup(r.text, "html.parser")
            temp_list = loc.findAll("div", {"class": "et_pb_text_inner"})
            hours_of_operation = (
                temp_list[1].text.replace("HOURS", "").replace("\n", " ")
            )
            phone = (
                loc.find("div", {"class": "et_pb_team_member_description"})
                .find("div")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            if len(phone) > 3:
                phone = phone[2]
            else:
                phone = phone[1].replace("PH ", "")
            extra = temp_list[3].find("strong").text
            address = temp_list[3].text.replace(extra, "").replace(" | ", "")
            coords = loc.find("iframe")["src"]
            r = session.get(coords, headers=headers)
            coords = r.text.split("],0],")[0].rsplit("[null,null,", 1)[1].split(",")
            latitude = coords[0]
            longitude = coords[1]
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
                locator_domain="https://costlessfoods.com/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
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
