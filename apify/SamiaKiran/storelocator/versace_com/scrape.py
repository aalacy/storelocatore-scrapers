from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "versace_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://versace.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    country_list = [
        "https://boutiques.versace.com/us/en-us/united-states",
        "https://boutiques.versace.com/us/en-us/canada",
        "https://boutiques.versace.com/us/en-us/puerto-rico",
        "https://boutiques.versace.com/us/en-us/united-kingdom",
    ]
    if True:
        for country in country_list:
            log.info("Fetching Country's list...")
            r = session.get(country, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            linklist = soup.find("ul", {"class": "Directory-listLinks"}).findAll(
                "a", {"class": "Directory-listLink"}
            )
            for link in linklist:
                loc_link = link["href"]
                loc_link = loc_link.split("en-us/")[1]
                loc_link = "https://boutiques.versace.com/us/en-us/" + loc_link
                count = link["data-count"]
                count = int(count.replace(")", "").replace("(", ""))
                r = session.get(loc_link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                if count > 1:
                    loclist = soup.find(
                        "ul", {"class": "Directory-listTeasers Directory-row"}
                    ).findAll("li")
                    for loc in loclist:
                        loc_link = loc.find("a", {"class": "Teaser-link"})["href"]
                        loc_link = loc_link.split("en-us/")[1]
                        loc_link = "https://boutiques.versace.com/us/en-us/" + loc_link
                        r = session.get(loc_link, headers=headers, verify=False)
                        log.info(loc_link)
                        soup = BeautifulSoup(r.text, "html.parser")
                        address = soup.find("address", {"class": "c-address"})
                        street_address = address.find(
                            "meta", {"itemprop": "streetAddress"}
                        )["content"]
                        address = address.findAll("div", {"class": "c-AddressRow"})
                        city = (
                            address[-2].find("span", {"class": "c-address-city"}).text
                        )
                        try:
                            state = (
                                address[-2]
                                .find("abbr", {"itemprop": "addressRegion"})
                                .text
                            )
                        except:
                            state = MISSING
                        zip_postal = (
                            address[-2]
                            .find("span", {"class": "c-address-postal-code"})
                            .text
                        )
                        country_code = address[-1].text
                        latitude = soup.find("meta", {"itemprop": "latitude"})[
                            "content"
                        ]
                        longitude = soup.find("meta", {"itemprop": "longitude"})[
                            "content"
                        ]
                        try:
                            phone = soup.find("span", {"itemprop": "telephone"}).text
                        except:
                            phone = MISSING
                        location_name = soup.find(
                            "h1", {"class": "Hero-title"}
                        ).findAll("span")
                        location_name = (
                            location_name[0].text + " " + location_name[1].text
                        )
                        hourlist = (
                            soup.find("table", {"class": "c-hours-details"})
                            .find("tbody")
                            .findAll("tr")
                        )
                        hours_of_operation = ""
                        for hour in hourlist:
                            hours_of_operation = (
                                hours_of_operation + " " + hour["content"]
                            )
                        yield SgRecord(
                            locator_domain=DOMAIN,
                            page_url=loc_link,
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

                else:
                    log.info(loc_link)
                    address = soup.find("address", {"class": "c-address"})
                    street_address = address.find(
                        "meta", {"itemprop": "streetAddress"}
                    )["content"]
                    address = address.findAll("div", {"class": "c-AddressRow"})
                    city = address[-2].find("span", {"class": "c-address-city"}).text
                    try:
                        state = (
                            address[-2].find("abbr", {"itemprop": "addressRegion"}).text
                        )
                    except:
                        state = MISSING
                    zip_postal = (
                        address[-2]
                        .find("span", {"class": "c-address-postal-code"})
                        .text
                    )
                    country_code = address[-1].text
                    latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
                    longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
                    try:
                        phone = soup.find("span", {"itemprop": "telephone"}).text
                    except:
                        phone = MISSING
                    location_name = soup.find("h1", {"class": "Hero-title"}).findAll(
                        "span"
                    )
                    location_name = location_name[0].text + " " + location_name[1].text
                    hourlist = (
                        soup.find("table", {"class": "c-hours-details"})
                        .find("tbody")
                        .findAll("tr")
                    )
                    hours_of_operation = ""
                    for hour in hourlist:
                        hours_of_operation = hours_of_operation + " " + hour["content"]
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=loc_link,
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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
