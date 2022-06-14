from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
import tenacity
from lxml import html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

logger = SgLogSetup().get_logger("carlsjr_com")


STORE_LOCATOR = "https://locations.carlsjr.com/index.html"
headers_special = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests(verify_ssl=False) as http:
        response = http.get(url, headers=headers_special)
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def get_state_urls():
    r = get_response(0, STORE_LOCATOR)
    sel = html.fromstring(r.text, "lxml")
    state_hrefs = sel.xpath('//a[contains(@class, "Directory-listLink")]/@href')
    state_links = ["https://locations.carlsjr.com/" + href for href in state_hrefs]
    return state_links


def get_store_urls(state_links, store_urls):

    """
    This returns the list of store urls. It extracts the store urls from State-based and City-based store locators in a Recursive
    In another word, it keeps extracting store urls until state and city store locator becomes empty
    """
    if not state_links:
        return
    statelink = state_links[0]
    r2 = get_response(0, statelink)
    sel2 = html.fromstring(r2.text)
    if r2.status_code == 200:
        state_links.remove(statelink)
        city_hrefs = sel2.xpath('//a[contains(@class, "Directory-listLink")]/@href')
        ctalink = sel2.xpath('//a[contains(@class, "Teaser-ctaLink")]/@href')
        if city_hrefs:
            for i in city_hrefs:
                if i.count("/") > 1:
                    j = "https://locations.carlsjr.com/" + i
                    store_urls.append(j)
                else:
                    j = "https://locations.carlsjr.com/" + i
                    state_links.append(j)
        if ctalink:
            for i in ctalink:
                if i.count("/") > 1:
                    j = "https://locations.carlsjr.com/" + i.replace("../", "")
                    store_urls.append(j)
                else:
                    j = "https://locations.carlsjr.com/" + i
                    state_links.append(j)
        get_store_urls(state_links, store_urls)
    return store_urls


def fetch_data(sgw: SgWriter):
    state_links = get_state_urls()
    logger.info(f"StateUrls: {state_links}")
    logger.info("PullingStoreUrls from state urls!")
    final_links = get_store_urls(state_links, [])
    logger.info("Processing " + str(len(final_links)) + " links ...")
    count_green_burrito = 0
    for num, final_link in enumerate(final_links[0:]):
        logger.info(f"[{num}] PullingContentFrom : {final_link}")
        final_link = final_link.replace("--", "-")
        req = get_response(num, final_link)
        logger.info(f"[{num}] HttpStatus: {req.status_code}")
        base = BeautifulSoup(req.text, "lxml")
        logger.info(f"[StoreNum: {num}] | [CountGreenBurrito: {count_green_burrito}]")
        if num == 200 and count_green_burrito < 2:
            raise Exception(
                "Crawler Intentionally Failed Due to Green Burrito is not available"
            )
        try:
            core_feature_list = base.find(class_="Core-featuresList").text.lower()
            logger.info(f"CoreFeatureList: {core_feature_list} | {final_link}")
            if "green burrito" in core_feature_list:
                count_green_burrito += 1
            else:
                continue
        except:
            continue

        location_name = base.h1.text.strip()
        street_address = base.find(itemprop="streetAddress")["content"]
        state = base.find(itemprop="addressRegion").text.strip()
        zip_code = base.find(itemprop="postalCode").text.strip()
        city = base.find(class_="Address-field Address-city").text.strip()
        country_code = "US"

        try:
            phone = base.find(itemprop="telephone").text.strip()
            if not phone:
                phone = ""
        except:
            phone = ""
        try:
            store_number = base.main["itemid"].split("#")[1]
        except:
            store_number = ""
        location_type = ""

        try:
            hours_of_operation = (
                " ".join(list(base.find(class_="c-hours-details").stripped_strings))
                .replace("Day of the Week Hours", "")
                .strip()
            )
        except:
            hours_of_operation = ""

        latitude = base.find(itemprop="latitude")["content"]
        longitude = base.find(itemprop="longitude")["content"]
        item = SgRecord(
            locator_domain="carlsjr.com",
            page_url=final_link,
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
        )

        sgw.write_row(item)


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)


if __name__ == "__main__":
    scrape()
