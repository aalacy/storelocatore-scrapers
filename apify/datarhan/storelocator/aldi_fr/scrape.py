import re
from lxml import etree
from urllib.parse import urljoin
from time import sleep
from random import randint, uniform
import threading
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.static import static_zipcode_list, SearchableCountries
from sgscrape.sgpostal import International_Parser, parse_address
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import pikepdf
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt

local = threading.local()


def get_session(refresh=False):
    if not hasattr(local, "session") or refresh:
        local.session = SgRequests()

    return local.session


def check_is_in_france(addr, tracker, session):
    copy = list(addr)
    key = ", ".join(copy)
    if tracker.get(key, None) is not None:
        return tracker.get(key)

    while len(copy):
        addr = ", ".join(copy)

        if is_french_city(addr, session):
            tracker[key] = True
            return True
        else:
            tracker[addr] = False
            copy.pop()

    tracker[key] = False
    return False


def is_french_city(city, session, retry=0):
    try:
        if "France" in city:
            return True

        params = {
            "q": city,
            "appid": "F2DD9E3AA45F7512D9C6CA9A150CBA7F76556B81",
            "structuredaddress": True,
        }
        data = session.get(
            "https://www.bing.com/api/v6/Places/AutoSuggest", params=params
        ).json()
        is_french = False
        for item in data["value"]:
            if item["_type"] == "PostalAddress" and item["countryIso"] == "FR":
                is_french = True
                break

            elif item["_type"] == "Place" and item["address"]["countryIso"] == "FR":
                is_french = True
                break

        return is_french
    except:
        if retry < 3:
            return is_french_city(city, SgRequests(), retry + 1)


@retry(stop=stop_after_attempt(3))
def fetch_locations(code, tracker):
    sleep(uniform(0, 5))
    start_url = "https://www.yellowmap.de/partners/AldiNord/Html/Poi.aspx"
    domain = "aldi.fr"

    session = get_session()
    search_url = "https://www.yellowmap.de/Partners/AldiNord/Search.aspx?BC=ALDI|ALDN&Search=1&Layout2=True&Locale=fr-FR&PoiListMinSearchOnCountZeroMaxRadius=50000&SupportsStoreServices=true&Country=F&Zip={}&Town=&Street=&Radius=100000"
    response = session.get(search_url.format(code))

    while hasattr(response, "base_exception"):
        session = get_session(True)
        response = session.get(search_url.format(code))
    session_id = response.url.params.get("SessionGuid")
    hdr = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    }

    frm = {
        "SessionGuid": session_id,
        "View": "",
        "ClearParas": "AdminUnitID,AdminUnitName,WhereCondition",
        "ClearGroups": "GeoMap,MapNav",
        "Locale": "fr-FR",
        "Loc": "",
    }

    response = session.post(start_url, headers=hdr, data=frm)
    dom = etree.HTML(
        response.text.replace('<?xml version="1.0" encoding="utf-8"?>', "")
    )
    if "Le nombre maximum des demandes de votre IP" in response.text:
        return []

    all_locations = dom.xpath('//tr[@class="ItemTemplate"]')
    all_locations += dom.xpath('//tr[@class="AlternatingItemTemplate"]')
    next_page = dom.xpath('//a[@title="page suivante"]/@href')
    while next_page:
        sleep(randint(0, 10))
        response = session.get(urljoin(start_url, next_page[0]))
        response = session.post(start_url, headers=hdr, data=frm)
        dom = etree.HTML(
            response.text.replace('<?xml version="1.0" encoding="utf-8"?>', "")
        )
        all_locations += dom.xpath('//td[@class="ItemTemplateColumnLocation"]')
        all_locations += dom.xpath(
            '//td[@class="AlternatingItemTemplateColumnLocation"]'
        )
        next_page = dom.xpath('//a[@title="page suivante"]/@href')

    items = []
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//p[@class="PoiListItemTitle"]/text()')[0]
        raw_adr = poi_html.xpath(".//address/text()")
        raw_adr = [e.strip() for e in raw_adr]
        addr = parse_address(International_Parser(), " ".join(raw_adr))

        if not check_is_in_france(raw_adr, tracker, session):
            continue

        hoo = poi_html.xpath('.//td[contains(@class,"OpeningHours")]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.aldi.fr/magasins-et-horaires-d-ouverture.html",
            location_name=clean(location_name.title()),
            street_address=clean(raw_adr[0].title()),
            city=addr.city,
            zip_postal=addr.postcode,
            hours_of_operation=hoo,
        )

        items.append(item)

    return items


def clean(string):
    return re.sub(r"\s\s+", " ", string)


def fetch_urls(session):
    url = "https://www.gps-data-team.com/pdf/ALDI_fr.pdf"
    response = session.get(url)
    file = BytesIO(response.content)
    pdf_file = pikepdf.Pdf.open(file)
    urls = []
    # iterate over PDF pages
    for page in pdf_file.pages:
        for annots in page.get("/Annots"):
            uri = annots.get("/A").get("/URI")
            if uri is not None:
                page_url = str(uri)
                if "ALDI-" in page_url and "pdf" not in page_url:
                    page_url = page_url.encode("cp1252").decode("utf-8")
                    urls.append(page_url)

    return urls


def fetch_location(page_url, session, tracker):
    response = session.get(page_url)
    soup = BeautifulSoup(response.text, "lxml")
    location_name = soup.find("a", itemprop="url").text

    address = ", ".join(
        tag
        for tag in soup.find("span", itemprop="streetAddress").contents
        if isinstance(tag, str)
    )
    addr = parse_address(International_Parser(), address)

    latitude = soup.find("span", itemprop="latitude").text
    longitude = soup.find("span", itemprop="longitude").text

    if tracker.get(address) or tracker.get(addr.street_address_1):
        return None

    street_address = addr.street_address_1
    city = addr.city
    postal = addr.postcode

    return SgRecord(
        locator_domain="aldi.fr",
        page_url="https://www.aldi.fr/magasins-et-horaires-d-ouverture.html",
        location_name=clean(location_name.title()),
        latitude=latitude,
        longitude=longitude,
        street_address=clean(street_address.title()),
        city=city,
        zip_postal=postal,
        country_code="FR",
    )


def fetch_data():
    with ThreadPoolExecutor() as executor, SgRequests() as session:
        tracker = {}
        all_codes = static_zipcode_list(5, country_code=SearchableCountries.FRANCE)

        futures = [
            executor.submit(fetch_locations, code, tracker) for code in all_codes
        ]
        for future in as_completed(futures):
            for poi in future.result():
                yield poi

        urls = fetch_urls(session)
        futures = [
            executor.submit(fetch_location, url, session, tracker) for url in urls
        ]
        for future in as_completed(futures):
            if future.result():
                yield future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=20000,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
