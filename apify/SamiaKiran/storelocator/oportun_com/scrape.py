from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "oportun_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://oportun.com/"
MISSING = SgRecord.MISSING


def get_address(address):

    street_address = address[0]
    address = address[1].split(",")
    city = address[0]
    address = address[1].split()
    state = address[0]
    zip_postal = address[1]
    country_code = "US"
    return street_address, city, state, zip_postal, country_code


def fetch_data():
    if True:
        url = "https://oportun.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.findAll("section", {"class": "location-state"})
        for state in statelist:
            url = state.find("a")["href"]
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "location-card"})
            for loc in loclist:
                page_url = loc.findAll("a")[-1]["href"]
                r = session.get(page_url, headers=headers)
                temp_address = (
                    loc.find("address")
                    .get_text(separator="|", strip=True)
                    .split("|")[0]
                )
                if r.status_code != 200:
                    location_name = loc.find("h3").text
                    address = (
                        loc.find("address")
                        .get_text(separator="|", strip=True)
                        .split("|")
                    )
                    phone = loc.find("p", {"class": "phone"}).find("a").text
                    hours_of_operation = MISSING
                else:
                    page_url = r.url
                    log.info(page_url)
                    soup = BeautifulSoup(r.text, "html.parser")
                    temp = soup.find("div", {"class": "location-intro__content"})
                    if (
                        temp.find("address")
                        .get_text(separator="|", strip=True)
                        .split("|")[0]
                        != temp_address
                    ):
                        location_name = loc.find("h3").text
                        address = (
                            loc.find("address")
                            .get_text(separator="|", strip=True)
                            .split("|")
                        )
                        (
                            street_address,
                            city,
                            state,
                            zip_postal,
                            country_code,
                        ) = get_address(address)
                        phone = loc.find("p", {"class": "phone"}).find("a").text
                        hours_of_operation = (
                            temp.find("p", {"class": "hours"})
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                        )
                        yield SgRecord(
                            locator_domain=DOMAIN,
                            page_url=url,
                            location_name=location_name,
                            street_address=street_address.strip(),
                            city=city.strip(),
                            state=state.strip(),
                            zip_postal=zip_postal.strip(),
                            country_code="US",
                            store_number=MISSING,
                            phone=phone.strip(),
                            location_type=MISSING,
                            latitude=MISSING,
                            longitude=MISSING,
                            hours_of_operation=hours_of_operation,
                        )
                    phone = temp.select_one("a[href*=tel]").text
                    address = (
                        temp.find("address")
                        .get_text(separator="|", strip=True)
                        .split("|")
                    )
                    hours_of_operation = (
                        temp.find("p", {"class": "hours"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                    location_name = loc.get_text(separator="|", strip=True).split("|")[
                        0
                    ]
                street_address, city, state, zip_postal, country_code = get_address(
                    address
                )
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
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
