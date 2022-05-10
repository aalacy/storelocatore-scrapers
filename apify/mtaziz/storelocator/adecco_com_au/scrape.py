# -*- coding: utf-8 -*-
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome, SgSelenium
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import SgLogSetup
import ssl
from sgpostal.sgpostal import parse_address_intl

start_url = "https://www.adecco.com.au/our-locations/"
try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("adecco_com_au")


def get_headers_for(url: str) -> dict:
    with SgChrome(executable_path=ChromeDriverManager().install()) as chrome:
        headers = SgSelenium.get_default_headers_for(chrome, url)
    return headers  # type: ignore


def get_store_urls():
    with SgRequests() as http:
        response = http.get(start_url, headers=headers)
        dom = html.fromstring(response.text, "lxml")
        hrefs = dom.xpath('//div[@class="location-list"]//a/@href')
        locations = ["https://www.adecco.com.au" + i for i in hrefs]
        return locations


def fetch_data():
    store_urls = get_store_urls()
    for snum, store_url in enumerate(store_urls[0:]):
        logger.info(f"Pulling content for : {store_url}")
        with SgRequests() as http:
            r = http.get(store_url, headers=headers)
            sel = html.fromstring(r.text, "lxml")

            ln = "".join(sel.xpath('//div[@class="contact-meta-info"]/h6/text()'))
            ln = " ".join(ln.split())
            ph = "".join(
                sel.xpath(
                    '//div[@class="contact-meta-info"]//a[contains(@href, "tel")]/@href'
                )
            )
            ph = ph.replace("tel:", "")
            add = sel.xpath(
                '//div[@class="contact-meta-info"]/small[contains(text(), "Address")]/following-sibling::p/text()'
            )

            ra = ""
            if "https://www.adecco.com.au/canberra" in store_url:
                ra = " ".join("".join(add).split())
            elif "https://www.adecco.com.au/albury-wodonga" in store_url:
                ra = "Level 3/553 Kiewa St, Albury NSW 2640"
            else:
                ra = [" ".join(i.split()) for i in add]
                ra = ", ".join(ra)

            map_holder = sel.xpath('//div[@class="map-holder"]/iframe/@src')
            lat = ""
            lng = ""
            try:
                lng = map_holder[0].split("!2d")[-1].split("!2m")[0].split("!3d")[0]
                lat = map_holder[0].split("!2d")[-1].split("!2m")[0].split("!3d")[-1]
            except:
                lat = ""
                lng = ""
            if "!3m2!1i1024!2i" in lat:
                lat = lat.split("!3m2!1i1024!2i")[0]

            lis = sel.xpath('//div[contains(@class, "branch-locator__opening")]/ul/li')
            hoo = []
            for li in lis:
                daytimes = li.xpath(".//text()")
                daytimes = [" ".join(i.split()) for i in daytimes]
                daytimes = [i for i in daytimes if i]
                hoo_raw = " ".join(daytimes)
                hoo.append(hoo_raw)
            hours_of_operation = "; ".join(hoo)

            if ",," in ra:
                ra = ra.replace(",,", ",")

            sta = ""
            city = ""
            zc = ""
            state = ""

            pai = parse_address_intl(ra)
            sta1 = pai.street_address_1
            sta2 = pai.street_address_2
            if sta1 is not None and sta2 is not None:
                sta = sta1 + ", " + sta2
            elif sta1 is not None and sta2 is None:
                sta = sta1
            elif sta1 is None and sta2 is not None:
                sta = sta2
            else:
                sta = ""

            city = pai.city
            if city is None:
                city = store_url.split("/")[-1].title().replace("-", " ")

            logger.info(f"City: {city}")
            state = pai.state.upper()
            logger.info(f"state: {state}")
            zc = pai.postcode
            logger.info(f"zc: {zc}")

            logger.info(f"[{snum}] | {store_url} | [{ra}]")

            item = SgRecord(
                locator_domain="adecco.com.au",
                page_url=store_url,
                location_name=ln,
                street_address=sta,
                city=city,
                state=state,
                zip_postal=zc,
                country_code="AU",
                store_number="",
                phone=ph,
                location_type="",
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours_of_operation,
                raw_address=ra,
            )
            yield item


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
    logger.info("Pulling Headers")
    headers = get_headers_for(start_url)
    logger.info("Scrape Started")
    scrape()
    logger.info("Scrape Finished!")
