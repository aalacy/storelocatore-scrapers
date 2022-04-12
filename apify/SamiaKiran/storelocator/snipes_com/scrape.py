import json
import html
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from tenacity import retry, stop_after_attempt
import tenacity
import random
import time

session = SgRequests()
website = "snipes_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.snipes.com/"
MISSING = SgRecord.MISSING


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(1, 3))
        if response.status_code == 200:
            log.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.snipes.com/storefinder"
        r = session.get(url, headers=headers)
        country_list = r.text.split('data-template-attrs="')[1].split(
            '" data-is-dialog-link'
        )[0]
        country_list = country_list.split("url&quot;:&quot;")[1:]
        log.info("Fetching each country's Store Locator...")
        linklist = []
        for country in country_list:
            country = country.split("&quot;")[0]
            country = "https://" + country + "/storefinder"
            if "usa" in country:
                continue
            if country in linklist:
                continue
            linklist.append(country)
        for link in linklist:
            if "www.snipes.at" in link:
                country_code = "Austria"
            elif "www.snipes.nl" in link:
                country_code = "Netherlands"
            elif "www.snipes.fr" in link:
                country_code = "France"
            elif "www.snipes.ch" in link:
                country_code = "Switzerland"
            elif "www.snipes.it" in link:
                country_code = "Italy"
            elif "www.snipes.es" in link:
                country_code = "Spain"
            elif "www.snipes.be" in link:
                country_code = "Belgium"
            elif "www.snipes.pl" in link:
                country_code = "Poland"
            elif "www.snipes.com" in link:
                country_code = "Germany"
            r = session.get(link, headers=headers)
            log.info(
                f"Fetching Stores from {country_code} >> Response Status: {r.status_code}"
            )

            try:
                loclist = (
                    r.text.split('data-locations="')[1]
                    .split("data-icon=")[0]
                    .replace('}]"', "}]")
                )
            except Exception as e:
                log.info(f"loclist Error: {e}")
                response = get_response(country_code, link)
                try:
                    loclist = (
                        response.text.split('data-locations="')[1]
                        .split("data-icon=")[0]
                        .replace('}]"', "}]")
                    )
                except:
                    continue

            loclist = BeautifulSoup(loclist, "html.parser")
            try:
                loclist = json.loads(str(loclist))
            except Exception as e:
                log.info(f"loclist JSON Error: {e}")
                continue

            for loc in loclist:
                store_number = loc["id"]
                page_url = "https://www.snipes.com/storedetails?sid=" + store_number
                log.info(page_url)
                location_name = loc["name"] + " Store"
                latitude = loc["latitude"]
                longitude = loc["longitude"]
                loc = loc["infoWindowHtml"]
                loc = (
                    loc.replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .replace("\n", "")
                    .strip()
                )
                soup = BeautifulSoup(loc, "html.parser")
                address = soup.findAll(
                    "div", {"class": "b-store-locator-result-address-section"}
                )
                address = " ".join(x.text for x in address)
                address = strip_accents(address)
                raw_address = html.unescape(address)
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING

                try:
                    phone = soup.select_one("a[href*=tel]")["href"].replace("tel:", "")
                except Exception as e:
                    log.info(f"Phone Error: {e}")
                    phone = MISSING

                hours_of_operation = strip_accents(
                    soup.find(
                        "div",
                        {
                            "class": "b-store-locator-store-hours b-store-map-view-section"
                        },
                    )
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                if (
                    hours_of_operation
                    == "Montag: - Dienstag: - Mittwoch: - Donnerstag: - Freitag: - Samstag: - Sonntag: -"
                ):
                    hours_of_operation = MISSING
                elif (
                    hours_of_operation
                    == "maandag: - dinsdag: - woensdag: - donderdag: - vrijdag: - zaterdag: - zondag: -"
                ):
                    hours_of_operation = MISSING
                elif (
                    hours_of_operation
                    == "Lundi: - Mardi: - Mercredi: - Jeudi: - Vendredi: - Samedi: - Dimanche: -"
                ):
                    hours_of_operation = MISSING
                elif "Jueves: - Viernes: -" in hours_of_operation:
                    hours_of_operation = MISSING
                if city is MISSING:
                    city = raw_address.split()[-1]

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
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
                    raw_address=raw_address,
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
