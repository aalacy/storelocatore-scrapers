from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "mcalistersdeli_com "
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://mcalistersdeli.com/"
MISSING = SgRecord.MISSING


def store_data(soup):
    location_name = soup.find("h2", {"class": "Core-title"}).text

    try:
        phone = soup.find("div", {"itemprop": "telephone"}).text
    except:
        phone = ""
    try:
        street_address = (
            soup.find("span", {"class": "c-address-street-1"}).text
            + " "
            + soup.find("span", {"class": "c-address-street-2"}).text
        )
    except:
        street_address = soup.find("span", {"class": "c-address-street-1"}).text
    city = soup.find("span", {"class": "c-address-city"}).text
    state = soup.find("abbr", {"class": "c-address-state"}).text
    zip_postal = soup.find("span", {"class": "c-address-postal-code"}).text
    country_code = "US"
    hours_of_operation = soup.findAll("tr", {"itemprop": "openingHours"})
    hours_of_operation = "  ".join(
        x.get_text(separator="|", strip=True).replace("|", " ")
        for x in hours_of_operation
    )
    latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
    longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
    return (
        location_name,
        phone,
        street_address,
        city,
        state,
        zip_postal,
        hours_of_operation,
        latitude,
        longitude,
        country_code,
    )


def fetch_data():
    if True:
        url = "https://www.mcalistersdeli.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.find("ul", {"class": "Directory-listLinks"}).findAll("li")
        for state in statelist:
            state_url = (
                "https://locations.mcalistersdeli.com/" + state.find("a")["href"]
            )
            r = session.get(state_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            if state.find("a")["data-count"] == "(1)":
                log.info(state_url)
                (
                    location_name,
                    phone,
                    street_address,
                    city,
                    state,
                    zip_postal,
                    hours_of_operation,
                    latitude,
                    longitude,
                    country_code,
                ) = store_data(soup)
                if not hours_of_operation:
                    continue
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=state_url,
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
                citylist = soup.find("ul", {"class": "Directory-listLinks"}).findAll(
                    "li"
                )
                for city in citylist:
                    city_url = (
                        "https://locations.mcalistersdeli.com/" + city.find("a")["href"]
                    )
                    r = session.get(city_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    if city.find("a")["data-count"] == "(1)":
                        log.info(city_url)
                        (
                            location_name,
                            phone,
                            street_address,
                            city,
                            state,
                            zip_postal,
                            hours_of_operation,
                            latitude,
                            longitude,
                            country_code,
                        ) = store_data(soup)
                        if not hours_of_operation:
                            continue
                        yield SgRecord(
                            locator_domain=DOMAIN,
                            page_url=city_url,
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
                        loclist = soup.find(
                            "ul", {"class": "Directory-listTeasers Directory-row"}
                        ).findAll("li")
                        for loc in loclist:
                            page_url = (
                                "https://locations.mcalistersdeli.com/"
                                + loc.find("a")["href"].replace("../", "")
                            )
                            log.info(page_url)
                            r = session.get(page_url, headers=headers)
                            soup = BeautifulSoup(r.text, "html.parser")
                            (
                                location_name,
                                phone,
                                street_address,
                                city,
                                state,
                                zip_postal,
                                hours_of_operation,
                                latitude,
                                longitude,
                                country_code,
                            ) = store_data(soup)
                            if not hours_of_operation:
                                continue
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
