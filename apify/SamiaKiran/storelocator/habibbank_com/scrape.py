from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "habibbank_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://habibbank.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        country_list = [
            "https://www.habibbank.com/uk/home/ukFindus.html",
            "https://habibbank.com/group/home/groupNetwork.html",
        ]
        for country_url in country_list:
            r = session.get(country_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                flag = 0
                loclist = str(
                    soup.find("div", {"class": "noticeBox"}).find("td")
                ).split("</dl>")[1:-1]
            except:
                flag = 1
                loclist = soup.find("table").find("td").findAll("dl")
            for loc in loclist:
                if flag == 0:
                    temp_var = BeautifulSoup(loc, "html.parser")
                    location_name = temp_var.find("h3").text
                    phone = (
                        temp_var.get_text(separator="|", strip=True)
                        .split("|")[-2]
                        .split("+")[1]
                    )
                    phone = "+" + phone
                    raw_address = (
                        temp_var.get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .split(", United Kingdom")[0]
                        .replace(location_name, "")
                    )
                    country_code = "United Kingdom"
                else:
                    country_code = loc.find("h3").text
                    if "HEAD OFFICE" in country_code:
                        continue
                    location_name = loc.find("dt").text.replace(",", "")
                    raw_address = (
                        loc.get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .replace(country_code, "")
                        .split(",")
                    )
                    try:
                        phone = raw_address[-1].split("☎")[1].split("✉")[0]
                    except:
                        phone = raw_address[-1].split("☎")[1].split("(")[0]
                    phone = phone.replace("(toll free from China) ", "")

                    if "Bank" in raw_address[0]:
                        raw_address = " ".join(raw_address[1:-1])
                    else:
                        raw_address = " ".join(raw_address[:-1])
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                log.info(location_name)
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=country_url,
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
                    hours_of_operation=MISSING,
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
