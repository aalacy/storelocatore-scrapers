from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

DOMAIN = "balduccis.com"
BASE_URL = "https://balduccis.com"
LOCATION_URL = "https://www.balduccis.com/locations"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "SSESS3b97c8171ee6f6af857ff5c3d10778f7=XPKqllTv7Tchkq052o0lZVPVsgHlXuBjTWLr_CjXrNI; btIdentify=defd8bef-36a3-4e74-f43d-c7c3a1989199; _bts=c0e88c23-49e5-4955-e6f2-17597b7461e2; _bti=%7B%22app_id%22%3A%22balduccis%22%2C%22attributes%22%3A%5B%7B%22name%22%3A%22created_at%22%2C%22value%22%3A%222021-07-24T01%3A03%3A47%2B00%3A00%22%7D%2C%7B%22name%22%3A%22last_updated%22%2C%22value%22%3A%222021-07-24T01%3A03%3A47%2B00%3A00%22%7D%5D%2C%22bsin%22%3A%22VrlfTumfEihci7DNyY6denUDyXMkyT8XZ4qnDBt%2BlEJ%2FEnOP%2FiIB72ZuxiVV9kMnY%2F%2Fmph6KjykNH2SW29%2BXdw%3D%3D%22%2C%22created_at%22%3A%222021-07-24T01%3A03%3A47%2B00%3A00%22%2C%22last_updated%22%3A%222021-07-24T01%3A03%3A47%2B00%3A00%22%7D; _ga=GA1.2.790374023.1627088628; _gid=GA1.2.418177363.1627088628; SSESS18260c83a1c65a0980df4f89ff7b90f2=UjEdJC_tkuwgOn0eFAgp0I0MvAvNEXJrOxygRf-JExw; _gcl_au=1.1.1004552590.1627094453; _gat=1; xdibx=N4Ig-mBGAeDGCuAnRIBcoAOGAuBnNAjAGwBMA7AAwCcArDQMwAsAHBTQDQgYBusAdtjQlOufKmLlqDKk3r1OPXP0GphIREgA2aECE6atOgPSaA9rACG2AJam--fXkKlKtejMZyAvpwgwMiACm3GigACYWAJ5iANoSrtJMjGQAuj7gUNDBgQJiwOl-cNZhOgQAZoGQsIxhgQC0FhSBjHWMLGV1zGSwzHVsdGSMFJD0NMR18VLuBDL0IF5AA__",
    "Host": "www.balduccis.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field.strip()


def get_latlong(soup):
    element = soup.find("script", {"type": "application/json"}).string
    data = json.loads(element)
    key = list(data["maps"].keys())[0]
    latitude = data["maps"][key]["locations"][0]["lat"]
    longitude = data["maps"][key]["locations"][0]["lon"]
    return latitude, longitude


def fetch_store_url():
    soup = pull_content(LOCATION_URL)
    links = (
        soup.find("div", {"class": "view-store-location-list"})
        .find("div", "view-content")
        .find_all("a", text="View Store Details")
    )
    store_links = []
    for row in links:
        store_links.append(BASE_URL + row["href"])
    log.info("Found {} store links".format(len(store_links)))
    return store_links


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_url()
    for page_url in store_urls:
        soup = pull_content(page_url)
        content = soup.find("div", {"id": "content-area"})
        location_name = soup.find("h1", {"class": "page-title"}).text.strip()
        address = content.find("p", {"class": "address"})
        addr2 = address.find("span", {"class": "address-line2"})
        organization = address.find("span", {"class": "organization"})
        street_address = address.find("span", {"class": "address-line1"}).text.strip()
        if addr2:
            street_address = f'{address.find("span", {"class": "address-line1"}).text.strip()}, {addr2.text.strip()}'
        if organization:
            raw_address = f'{organization.text.strip()}, {address.find("span", {"class": "address-line1"}).text.strip()}'
        else:
            raw_address = street_address
        city = address.find("span", {"class": "locality"}).text.strip()
        state = address.find("span", {"class": "administrative-area"}).text.strip()
        zip_code = address.find("span", {"class": "postal-code"}).text.strip()
        phone = content.find("div", {"class": "field--name-field-phone"})
        if phone:
            phone = phone.find("div", {"class": "field__item"}).text.strip()
        else:
            phone = MISSING
        hours_of_operation = MISSING
        hoo = content.find("div", {"class": "field--name-field-store-hours"})
        if hoo:
            hoo = hoo.find_all("div", {"class": "paragraph--type--store-hours-group"})
            hours_of_operation = ""
            for hours in hoo:
                hours_of_operation += ", " + hours.get_text(strip=True, separator=":")
        hours_of_operation = hours_of_operation.lstrip(",").strip()
        store_number = MISSING
        country_code = address.find("span", {"class": "country"}).text.strip()
        if len(location_name.split(",")) > 1:
            location_type = "STORES"
        else:
            location_type = "TO-GO"
            street_address = (
                "{}, {}".format(
                    organization.text.replace("Bloomberg Children's Center", "")
                    .replace("Philadelphia International Airport ", "")
                    .strip(),
                    address.find("span", {"class": "address-line1"}).text,
                )
                .lstrip(",")
                .strip()
            )
        latitude, longitude = get_latlong(soup)
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
