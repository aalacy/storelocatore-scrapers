from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "texashealth_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.texashealth.org"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        type_url = "https://www.texashealth.org//sxa/search/facets/?f=type&s={E6D4398E-5377-4F52-A622-BA5985AA0E05}|{489713F2-2F53-486A-A99A-125A4921BB4F}&sig=location-search"
        type_list = session.get(type_url, headers=headers).json()["Facets"][0]["Values"]
        for location_type in type_list:
            log.info(f"{location_type['Count']} {location_type['Name']} Locations...")
            location_type = location_type["Name"]
            url = (
                "https://www.texashealth.org//sxa/search/results/?s={E6D4398E-5377-4F52-A622-BA5985AA0E05}|{489713F2-2F53-486A-A99A-125A4921BB4F}&itemid={AF045BC3-3192-47D4-9F02-14F252C53DC8}&sig=location-search&type="
                + location_type
                + "&g=32.735687%7C-97.10806559999997&o=DistanceMi%2CAscending&p=125&v=%7B46E173AB-F518-41E7-BFB5-00206EDBA9E6%7D"
            )
            loclist = session.get(url, headers=headers).json()["Results"]
            country_code = "US"
            for loc in loclist:
                store_number = loc["Id"]
                page_url = DOMAIN + loc["Url"]
                log.info(page_url)
                html = BeautifulSoup(loc["Html"], "html.parser")
                location_name = html.find(
                    "div", {"class": "profile-key-data field-navigationtitle"}
                ).text
                phone = html.find("a", {"class": "field-phone-number"}).text
                try:
                    street_address = (
                        html.find("div", {"class": "field-address-line-1"}).text
                        + " "
                        + html.find("div", {"class": "field-address-line-2"}).text
                    )
                except:
                    street_address = html.find(
                        "div", {"class": "field-address-line-1"}
                    ).text
                city = (
                    html.find("span", {"class": "field-city"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace(",", "")
                )
                state = (
                    html.find("span", {"class": "field-state"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                zip_postal = (
                    html.find("span", {"class": "field-zip-code"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                latitude = loc["Geospatial"]["Latitude"]
                longitude = loc["Geospatial"]["Longitude"]
                html = BeautifulSoup(loc["Html"], "html.parser")
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=MISSING,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
