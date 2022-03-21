import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tuffy_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.tuffy.com"
MISSING = SgRecord.MISSING


def fetch_data():
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "ME",
        "MD",
        "MI",
        "MN",
        "MS",
        "MO",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "PA",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WV",
        "WI",
    ]
    for statenow in states:
        coordlist = []
        url = "https://www.tuffy.com/location_search?zip_code=" + statenow
        r = session.get(url, headers=headers)
        if r.status_code != 200:
            continue
        log.info(url)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll("div", {"class": "contact-info"})
        if len(divlist) == 0:
            continue
        latlnglist = r.text.split("var locations = [", 1)[1].split("];", 1)[0]
        while True:
            try:
                temp, latlnglist = latlnglist.split("(", 1)[1].split("),", 1)
                coordlist.append(temp)
            except:
                break

        for j in range(0, len(divlist)):
            div = divlist[j]
            location_name = div.find("h2").text.strip().split("T", 1)[1]
            location_name = "T" + location_name
            log.info(location_name)
            address = (
                div.find("address")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            try:
                address = address.split("MANAGER", 1)[0]
            except:
                pass
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
            country_code = "US"
            phone = (
                div.find("span", {"class": "tel"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            hours = (
                div.find("div", {"class": "schedule-holder"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            latitude, longitude = coordlist[j].split(", ")
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
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours,
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
