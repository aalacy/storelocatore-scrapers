from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name="bubbakoos.com")


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.bubbakoos.com/"
    r = session.get("https://www.bubbakoos.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for location in soup.find_all("div", {"class": "location_part my-3"}):
        page_url = base_url + location.find("a")["href"]
        log.info(page_url)
        location_request = session.get(page_url, headers=headers)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        store_sel = lxml.html.fromstring(location_request.text)
        name = location.find("a").text
        phone = "<MISSING>"
        if location_soup.find("a", {"href": re.compile("tel:")}) is None:
            phone = "<MISSING>"
        else:
            phone = (
                location_soup.find("a", {"href": re.compile("tel:")})
                .text.strip()
                .replace("TACO", "8226")
            )

        hours = (
            " ".join(
                store_sel.xpath('//div[@class="contact_details_sec"]/p/span//text()')
            )
            .strip()
            .replace("–", "-")
        )
        if "Open 7 Days:" == hours:
            section = store_sel.xpath('//div[@class="contact_details_sec"]/p')
            for sec in section:
                if len("".join(sec.xpath("span/text()")).strip()) > 0:
                    hours = (
                        "Open 7 Days:"
                        + " ".join(sec.xpath("text()"))
                        .strip()
                        .replace("\n", "")
                        .strip()
                    )
                    break

        hours = (
            " ".join(hours.split("\n"))
            .strip()
            .replace("\r", "")
            .strip()
            .replace("   ", " ")
            .strip()
        )
        address = " ".join(list(location.find_all("p")[0].stripped_strings))
        store_zip = " ".join(list(location.find_all("p")[2].stripped_strings))
        if store_zip == "":
            address = " ".join(list(location.find_all("p")[1].stripped_strings))
            store_zip = " ".join(list(location.find_all("p")[3].stripped_strings))
        city_state = " ".join(
            list(
                location_soup.find("div", {"class": "contact_details_sec"})
                .find_all("p")[0]
                .stripped_strings
            )
        )

        latitude = ""
        longitude = ""
        if location_soup.find("iframe") is None:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        else:
            geo_location = location_soup.find("iframe")["src"]
            latitude = geo_location.split("!3d")[1].split("!")[0]
            longitude = geo_location.split("!2d")[1].split("!")[0]

        yield SgRecord(
            locator_domain="https://www.bubbakoos.com",
            page_url=page_url,
            location_name=name,
            street_address=address,
            city=city_state.split(",")[0],
            state=city_state.split(",")[1],
            zip_postal=store_zip,
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="bubbakoo's burrito's",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours,
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
