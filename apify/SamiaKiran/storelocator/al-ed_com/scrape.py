import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "al-ed_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "al-ed.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://al-ed.com",
    "referer": "https://al-ed.com/storelocator",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

DOMAIN = "https://al-ed.com"
MISSING = SgRecord.MISSING

payload = "lat=0&lng=0&radius=0&product=0&category=0&sortByDistance=false"


def fetch_data():
    if True:
        url = "https://al-ed.com/storelocator"
        r = session.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        page_no = soup.find("a", {"class": "page"}).findAll("span")[-1].text
        page_no = int(page_no) + 1
        for x in range(1, page_no):
            url = "https://al-ed.com/amlocator/index/ajax/?p=" + str(x)
            loclist = session.post(url, headers=headers, data=payload).json()["items"]
            for loc in loclist:
                store_number = loc["id"]
                latitude = loc["lat"]
                longitude = loc["lng"]
                temp = loc["popup_html"]
                loc = BeautifulSoup(temp, "html.parser")
                page_url = loc.find("a", {"class": "amlocator-link"})["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                address = soup.find(
                    "div", {"class": "amlocator-location-info"}
                ).findAll("div", {"class": "amlocator-block"})
                raw_address = address[4].findAll("span")[-1].text
                pa = parse_address_intl(raw_address)
                try:
                    street_address = pa.street_address_1 + " " + pa.street_address_2
                except:
                    street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING

                location_name = html.unescape(soup.find("h1").text)
                phone = soup.find("div", {"class": "amlocator-block -contact"}).findAll(
                    "div", {"class": "amlocator-block"}
                )
                phone = phone[1].find("a").text
                hour_list = soup.find(
                    "div", {"class": "amlocator-schedule-table"}
                ).findAll("div", {"class": "amlocator-row"})
                hours_of_operation = ""
                for hour in hour_list:
                    hour = hour.findAll("span")[:-2]
                    day = hour[0].text
                    time = hour[1].text
                    hours_of_operation = hours_of_operation + " " + day + " " + time
                if city == MISSING:
                    zip_postal = address[0].findAll("span")[-1].text
                    state = address[2].findAll("span")[-1].text
                    city = address[3].findAll("span")[-1].text
                if "," not in raw_address:
                    raw_address = (
                        raw_address + " " + city + ", " + state + " " + zip_postal
                    )
                country_code = "US"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
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
