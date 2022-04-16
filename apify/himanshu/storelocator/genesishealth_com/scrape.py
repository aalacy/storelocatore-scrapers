import re
import lxml.html
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("genesishealth_com")

session = SgRequests()


def fetch_data(sgw: SgWriter):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    base_url = "https://www.genesishealth.com"
    r = session.get(
        "https://www.genesishealth.com/facilities/location-search-results/",
        headers=headers,
    )
    soup = BeautifulSoup(r.text, "html.parser")

    for page in soup.find("div", {"class": "Pagination"}).find_all("option"):
        r1 = session.get(page["value"].replace("~", base_url))
        soup1 = BeautifulSoup(r1.text, "html.parser")
        for script in soup1.find("div", {"class": "LocationsList"}).find_all("li"):

            location_name = script.find("a")["title"]
            addr = list(script.find("p", {"class": "TheAddress"}).stripped_strings)
            if len(addr[:-1]) == 1:
                street_address = " ".join(addr[:-1])
            else:

                number = re.findall(r"[0-9]{4}|[0-9]{3}", addr[0])
                if number:
                    street_address = addr[0]
                else:
                    street_address = addr[1]
            city = addr[-1].split(",")[0]
            state = addr[-1].split(",")[1].split(" ")[1]
            if len(addr[-1].split(",")[1].split(" ")) == 3:
                zipp = addr[-1].split(",")[1].split(" ")[-1]
            else:
                zipp = "<MISSING>"
            try:
                phone = script.find("span", {"class": "Phone"}).text
            except:
                phone = "<MISSING>"

            url = script.find("a")["href"].replace("../", "").replace("amp;", "")
            if "http" in url:
                page_url = url
            elif "location-public-profile" in url:
                page_url = "https://www.genesishealth.com/facilities/" + url
            else:
                page_url = "https://www.genesishealth.com/" + url
            if "&id" in url:
                store_number = page_url.split("&id=")[-1]
            else:
                store_number = "<MISSING>"

            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = "<MISSING>"
            if "genesishealth.com" in page_url:

                logger.info(page_url)
                store_req = session.get(page_url)
                store_sel = lxml.html.fromstring(store_req.text)
                location_soup = BeautifulSoup(store_req.text, "html.parser")
                coords = location_soup.find("script", {"type": "application/ld+json"})
                if coords:
                    try:
                        lat = str(coords).split('"latitude": "')[1].split('"')[0]
                        lng = str(coords).split('"longitude": "')[1].split('"')[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                else:
                    lat = "<MISSING>"
                    lng = "<MISSING>"

                temp_hours = store_sel.xpath("//div[@class='DaySchedule ClearFix']")
                hours_list = []

                for hour in temp_hours:
                    day = "".join(hour.xpath('div[@class="Day"]/text()')).strip()
                    time = "".join(hour.xpath('div[@class="Times"]/text()')).strip()
                    hours_list.append(day + time)

                hours = "; ".join(hours_list).strip()

            row = SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
