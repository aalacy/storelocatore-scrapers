import json
import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "childrens_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    url = "https://www.childrens.com/wps/FusionService/api/public/query/Childrens/Childrens?rows=36&fq=%7B!tag%3DmainCategory_s%7DmainCategory_s:%22locations%22&pt=33.645739899999995,72.9921794"
    content = session.get(url, headers=headers).json()
    res = content["response"]
    docs = res["docs"]
    lnk = []
    lnk.append("none")
    p = 0
    for i in range(0, len(docs)):
        loc = docs[i]
        l = str(loc)
        pg = (l.split("'id': '"))[1].split("'")[0]
        page_url = pg
        page = session.get(page_url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        try:
            loc = soup.find("h1", itemprop="name").text
            location_name = loc
        except:
            continue
        else:
            loc = loc.replace("\u2120", "")
            loc = loc.replace("\n", "")
            try:
                hrt = soup.find("span", class_="open-hours")
                hrt = hrt["data-hours"]
                det = hrt.split(",")
                hours_of_operation = ""
                for dt in det:

                    start, end = dt.lstrip().split(" ", 1)[1].split("-")
                    end, tag = end.split(":")

                    endtime = (int)(end) - 12
                    if endtime == 11:
                        hours_of_operation = (
                            hours_of_operation
                            + dt.lstrip().split(" ", 1)[0]
                            + " 24 Hours "
                        )
                    else:

                        hours_of_operation = (
                            hours_of_operation
                            + dt.lstrip().split(" ", 1)[0]
                            + " "
                            + start
                            + " am - "
                            + str(endtime)
                            + ":"
                            + tag
                            + " pm "
                        )
            except:
                try:
                    hours_of_operation = soup.find(
                        "div", {"class": "custom-hours"}
                    ).text
                except:
                    hours_of_operation = "<MISSING>"
            else:
                hours_of_operation = hours_of_operation.replace(" +", "")
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            if hours_of_operation.find("Appointments") > -1:
                hours_of_operation = "<MISSING>"
            hours_of_operation = (
                hours_of_operation.replace("\n", " ")
                .replace("Su-", "Sun - ")
                .replace("Mo-", "Mon - ")
                .replace("Th ", "Thurs ")
                .replace("Fr ", "Fri ")
                .replace("Sa ", "Sat ")
            )
            street_address = soup.find("span", itemprop="streetAddress").text
            street_address = street_address.replace("\n", "")
            for i in range(1, 10):
                street_address = street_address.replace("  ", " ")
            street_address = street_address.lstrip()
            city = soup.find("span", itemprop="addressLocality").text
            city = city.replace(",", "")
            state = soup.find("span", itemprop="addressRegion").text
            zip_postal = soup.find("span", itemprop="postalCode").text
            phone = soup.find("span", itemprop="telephone").text
            if phone.find("CHILD") > -1:
                phone = "844-424-4537"
            coord = (
                soup.find("a", {"class": "directions-link"})["href"]
                .split("@", 1)[1]
                .split("/data")[0]
            )
            latitude, longitude = coord.split(",", 1)
            longitude = longitude.split(",", 1)[0]
            log.info(page_url)
            if loc in lnk:
                pass

            else:
                yield SgRecord(
                    locator_domain="https://www.childrens.com/",
                    page_url=page_url,
                    location_name=location_name.strip(),
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
