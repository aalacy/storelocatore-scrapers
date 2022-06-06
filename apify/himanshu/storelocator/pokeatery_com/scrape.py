from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pokeatery.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

session = SgRequests()


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    base_url = "http://www.pokeatery.com/"
    soup = bs(session.get(base_url).text, "lxml")

    for url in soup.find("ul", {"class": "sub-menu"}).find_all("a"):
        phone = ""
        page_url = url["href"]
        log.info(page_url)
        store_req = session.get(page_url)
        location_soup = bs(store_req.text, "lxml")
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//h1[@class="headline__primary"]/text()')
        ).strip()

        map_link = "".join(
            store_sel.xpath('//div[@class="c-hero__map gmap"]/@data-url')
        ).strip()
        latitude, longitude = get_latlng(map_link)

        p_tag = location_soup.find_all("div", {"class": "container"})[1].find_all("p")

        if len(p_tag) == 3:
            hours = (
                "; ".join(list(p_tag[0].stripped_strings)).split("Hours:")[1].strip()
            )
            raw_address = list(p_tag[2].stripped_strings)

            street_address = raw_address[1].strip()
            city = raw_address[2].strip().split(",")[0]
            state = raw_address[2].strip().split(",")[1].strip().split()[0]
            zipp = raw_address[2].strip().split(",")[1].strip().split()[1]
            phone = raw_address[3].strip()
        elif len(p_tag) == 4:
            hours = (
                "; ".join(list(p_tag[0].stripped_strings)).split("Hours:")[1].strip()
            )
            addr = list(p_tag[2].stripped_strings)

            street_address = addr[0].split(",")[0].split("\r\n")[0]
            city = addr[0].split(",")[0].split("\r\n")[1]
            state = addr[0].split(",")[1].split("\r\n")[0].split()[0]
            zipp = addr[0].split(",")[1].split("\r\n")[0].split()[1]
            phone = addr[0].split(",")[1].split("\r\n")[1]

        elif len(p_tag) == 5:
            hours = (
                "; ".join(list(p_tag[0].stripped_strings)).split("Hours:")[1].strip()
            )
            raw_address = ", ".join(list(p_tag[2].stripped_strings)).strip()
            if "Call" in raw_address:
                raw_address = ", ".join(list(p_tag[3].stripped_strings)).strip()

            raw_address = raw_address.replace("Austin,", ", Austin,").strip()
            if "(" in raw_address:
                phone = "(" + raw_address.split("(")[1].strip().split(",")[0].strip()
                raw_address = raw_address.split("(")[0].strip()
            else:
                phone = "<MISSING>"

            if "@" in raw_address:
                raw_address = ", ".join(raw_address.split(",")[:-1]).strip()

            raw_address = raw_address.split(",")
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].strip().split()[0]
            zipp = raw_address[2].strip().split()[1]

        if len(hours) > 0 and hours[0] == ";":
            hours = "".join(hours[1:]).strip()

        yield SgRecord(
            locator_domain=base_url,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
