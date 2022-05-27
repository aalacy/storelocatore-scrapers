import json
import re
import lxml.html
from time import sleep
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser

website = "hsbc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    search_urls = [
        "https://www.hsbc.com.ar/mapa/, https://www.hsbc.com.ar/branch-list/,Argentina",
        "https://www.hsbc.bm/branch-finder/, https://www.hsbc.bm/branch-list/, Bermuda",
        "https://www.hsbc.ca/branch-locator/, https://www.hsbc.ca/branch-list/, Canada",
        "https://www.hsbc.com.mx/contacto/sucursales/, https://www.hsbc.com.mx/contacto/directorio-de-sucursales/, Mexico",
        "https://www.us.hsbc.com/branch-locator/, https://www.us.hsbc.com/branch-list/, United States",
        "https://www.hsbc.com.au/branch-finder/, https://www.hsbc.com.au/branch-list/, Australia",
        "https://www.hsbc.com.cn/en-cn/branch-finder/, https://www.hsbc.com.cn/en-cn/help/contact/branch-finder/lists/, China",
        "https://www.hsbc.com.hk/branch-finder/, https://www.hsbc.com.hk/branch-finder/,  Hong Kong",
        "https://www.hsbc.co.in/branch-finder/, https://www.hsbc.co.in/branch-list/,  India",
        "https://www.hsbc.com.mo/branch-finder/, https://www.hsbc.com.mo/branch-list/, Macau",
        "https://www.hsbc.com.my/branch-finder/, https://www.hsbc.com.my/branch-list/, Malaysia",
        "https://www.hsbc.co.mu/branch-finder/, https://www.hsbc.co.mu/branch-list/,  Mauritius",
        "https://www.hsbc.com.ph/branch-finder/, https://www.hsbc.com.ph/branch-list/, Philippines",
        "https://www.hsbc.com.sg/branch-finder/, https://www.hsbc.com.sg/branch-list/, Singapore",
        "https://www.hsbc.lk/branch-finder/, https://www.hsbc.lk/branch-list/, Sri Lanka",
        "https://www.hsbc.com.tw/en-tw/branch-finder/, https://www.hsbc.com.tw/en-tw/branch-list/,   Taiwan",
        "https://www.hsbc.am/en-am/branch-finder/,https://www.hsbc.am/en-am/branch-list/, Armenia",
        "https://www.hsbc.gr/en-gr/branch-finder/,https://www.hsbc.gr/en-gr/branch-list/,Greece",
        "https://www.hsbc.com.mt/branch-finder/, https://www.hsbc.com.mt/branch-list/, Malta",
        "https://www.hsbc.co.uk/branch-finder/, https://www.hsbc.co.uk/branch-list/, UK",
        "https://www.hsbc.com.bh/branch-finder/, https://www.hsbc.com.bh/branch-finder/, Bahrain",
        "https://www.hsbc.com.eg/branch-finder/, https://www.hsbc.com.eg/branch-finder/, Egypt",
        "https://www.hsbc.co.om/branch-finder/, https://www.hsbc.co.om/branch-finder/,  Oman",
        "https://www.hsbc.com.qa/branch-finder/, https://www.hsbc.com.qa/branch-finder/, Qatar",
        "https://www.hsbc.ae/branch-finder/, https://www.hsbc.ae/branch-finder/, UAE",
    ]

    for url_country in search_urls:
        search_url = url_country.split(",")[0].strip()
        domain = (
            search_url.rsplit(".", 1)[0]
            + "."
            + search_url.rsplit(".", 1)[1].split("/")[0].strip()
        )
        log.info(search_url)
        home_req = session.get(search_url, headers=headers)
        home_sel = lxml.html.fromstring(home_req.text)
        try:
            data_files = eval(
                "".join(
                    home_sel.xpath(
                        '//div[@class="branchLocator"]/@data-dpws-tool-datafiles'
                    )
                ).strip()
            )

            for location in fetch_data_from_files(data_files, domain, url_country):
                yield location
        except:
            for location in fetch_data_from_site(home_sel, domain, session):
                yield location


def fetch_data_from_site(home_sel, domain, session):
    locations = []
    urls = home_sel.xpath(
        '//table[@class="desktop"]/tbody/tr/td/a[contains(@href, "branch-list")]/@href'
    )
    for url in urls:
        page_url = f"{domain}{url}"
        html = session.get(page_url).text
        page = lxml.html.fromstring(html)
        data = json.loads(page.xpath('//script[@type="application/ld+json"]/text()')[0])

        location_name = data["name"]

        address = data["address"]
        street_address = address["streetAddress"].strip()
        city = address["addressLocality"]
        postal = address["postalCode"]
        country_code = address["addressCountry"]

        geo = data["geo"]
        latitude = geo["latitude"]
        longitude = geo["longitude"]

        contact = data["contactPoint"]
        phone = contact[0]["telephone"]

        hours = []
        for hour in data["openingHoursSpecification"]:
            day = re.sub("http://schema.org/", "", hour["dayOfWeek"])
            opens = hour["opens"]
            closes = hour["closes"]

            hours.append(f"{day}: {opens}-{closes}")
        hours_of_operation = ",".join(hours)

        locations.append(
            SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                phone=phone,
                raw_address=f"{street_address}, {city}, {postal}",
            )
        )

    return locations


def resolve_phone(store):
    if "phoneNumber" not in store:
        return None

    phones = store["phoneNumber"]
    phone_nums = phones.get("existingCustomers") or phones.get("newCustomers")

    phone = re.split(r"\s*\/\s*", str(phone_nums))[0]
    phone = phone.rsplit("  ")[0]
    if len(re.sub("[^0-9]", "", phone)) < 5:
        phone = phone_nums

    match = re.search(r"(\(\d+\) \d+-\d+)", phone_nums)
    if match:
        phone = match.group(1)

    match = re.search(r"(\d+) o", phone)
    if match:
        phone = match.group(1)

    return phone


def fetch_data_from_files(data_files, domain, url_country):
    locations = []
    for key in data_files.keys():
        url = data_files[key]
        sleep(5)
        stores_req = session.get(
            domain + url.replace(".cdata", ".udata"),
            headers=headers,
        )
        stores = json.loads(stores_req.text)[key]

        for store in stores:
            locator_domain = website
            location_name = re.sub('\n', '', store["name"])

            city = store["address"].get("townOrCity", "<MISSING>")
            state = store["address"].get("stateRegionCounty", "<MISSING>")
            zip = store["address"].get("postcode", "<MISSING>")
            country_code = url_country.split(",")[2].strip()

            if state == country_code:
                state = None

            cleaned_zip = SgRecord.MISSING
            if zip != SgRecord.MISSING:
                cleaned_zip = re.sub(
                    rf"\s*({country_code}|SWIFT:)\s*", "", str(zip), re.IGNORECASE
                )
                if re.search("po box", cleaned_zip, re.IGNORECASE):
                    cleaned_zip = SgRecord.MISSING

            phone = resolve_phone(store)

            street_address = ""
            if "street" in store["address"]:
                address = (
                    store["address"]["street"]
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("\n", "")
                    .replace("?", "-")
                    .strip()
                    .replace("---", "-")
                    .strip()
                )

                parsed = parse_address(International_Parser(), address)
                if (
                    parsed.street_address_1 is not None
                    and len(parsed.street_address_1) > 5
                ):
                    street_address = address
                else:
                    street_address = re.sub(rf",\s*{city}", "", address)

            store_number = "<MISSING>"
            location_type = store["Type"]

            hours_list = []
            if "openingTimes" in store:
                hours = store["openingTimes"]
                for day in hours.keys():
                    if "open" in hours[day] and "close" in hours[day]:
                        try:
                            time = hours[day]["open"] + "-" + hours[day]["close"]
                            if "N/A" not in time:
                                hours_list.append(day + ":" + time)
                        except Exception as e:
                            log.error(e)
                            raise e

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store["coordinates"]["lat"]
            longitude = store["coordinates"]["lng"]
            url_formatted_name = re.sub(
                r"\s+", "-", re.sub(r"[^a-zA-Z0-9\s]", "", location_name.strip())
            ).lower()
            page_url = (
                f"{url_country.split(',')[1].strip()}{url_formatted_name}"
                if location_type == "Branch"
                else None
            )

            raw_address = f"{address}, {city}"
            if cleaned_zip != SgRecord.MISSING:
                raw_address = f"{raw_address}, {cleaned_zip}"

            locations.append(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=cleaned_zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
            )

    return locations


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.COUNTRY_CODE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
