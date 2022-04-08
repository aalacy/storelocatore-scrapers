import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sglogging import SgLogSetup
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("")

locator_domain = "https://www.specsavers.co.uk"
base_url = "https://www.specsavers.co.uk/stores/full-store-list"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "mt.v=2.27095391.1646420965404; _gcl_au=1.1.513502921.1646420967; _scid=3782b7b3-5683-4c70-b931-070b4a152cf1; _cs_c=1; EG-U-ID=C55cca9264-6a4f-42d3-a0d5-3f0726977d0c; LMUID=ff7ccd63-8921-8f73-c056-32b10ceebcab; _pin_unauth=dWlkPVpqZzRaVEl6TkRRdE5qUXlaUzAwTlRjd0xXRXdPVGN0WTJVMVpEazROVFJpWXpFdw; cookie-agreed=2; hl=gb_en; _hjSessionUser_131995=eyJpZCI6ImI4NDBmNTFkLTkwNzYtNTNmZC04OGJiLWYzNTMzYWUzYmJhNCIsImNyZWF0ZWQiOjE2NDY0MjA5NzEyMjcsImV4aXN0aW5nIjp0cnVlfQ==; OptanonAlertBoxClosed=2022-03-08T07:06:25.623Z; _gid=GA1.3.840936065.1649183820; EG-S-ID=A961983ddc-741c-4021-8b82-96da44397bf7; _sctr=1|1649142000000; EG_CUST_SEC=true; EXP_ID_VALUE=1508136,1578890; EXP_KEY_VALUE=Required-GraphQL_1508136,T148-Book-Stores-50_1578890; EXP_SPLIT_VALUE=Experiment,A; EXP_DIMENSION_NUMBER=126,133; __cf_bm=P_FK8FHqQi0H_C9vkOLl5qYFIE8kT1TF.tVQeXQXLKE-1649232914-0-Aepu9/VkVYI+CPh46ahA5f2Nlv8k8cf6pywyGntHuGVOItqiqo27neveqlW47tHOMVCFcdWWeeV3/XjBvanuLisa7fEjFJxAnjgknNBUTUG6; mt.sc=%7B%22i%22%3A1649232939406%2C%22d%22%3A%5B%5D%7D; LMSID=3ac045bc-c729-ca05-2499-53eae4a7301a; _hjSession_131995=eyJpZCI6IjhhZDBlMjQ5LTYwYTMtNDk4NS04ODgzLWQxMWQ5ZjkwMmYxMiIsImNyZWF0ZWQiOjE2NDkyMzI5NDQ0NDksImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; _cs_id=22c0088c-9d9b-a017-945d-e578bf2b74f6.1646420969.9.1649233561.1649232947.1554308191.1680584969055; _cs_s=3.0.0.1649235361642; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Apr+06+2022+01%3A29%3A11+GMT-0700+(Pacific+Daylight+Time)&version=6.32.0&isIABGlobal=false&hosts=&consentId=b644c8ca-396b-4cce-9e48-584ace32e1bf&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=%3B; _ga_RZ4VEZM7YG=GS1.1.1649232939.10.1.1649233751.0; _ga=GA1.3.523839279.1646420968; _dc_gtm_UA-78250785-1=1; _gat_UA-78250785-1=1; _uetsid=619a8e50b50f11ecbaa95f3ab4cebf25; _uetvid=9d1a25e09bee11ecba79c50c7fccae94; _yfpc=1553035878142; _hjIncludedInSessionSample=0; _dd_s=rum=1&id=04e7db54-64e6-426e-a46d-043ad68af0b4&created=1649233559331&expire=1649234653151",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

max_workers = 1


def fetchConcurrentSingle(link):
    page_url = "https://www.specsavers.co.uk/stores/" + link["href"]
    logger.info(page_url)
    res = request_with_retries(page_url)
    if res.status_code == 200:
        soup = bs(res.text, "lxml")
        location_type = "Hearing Centre" if "hearing" in page_url else "Optician"
        try:
            addr = list(soup.select_one("div.store p").stripped_strings)
        except:
            addr = (
                soup.select_one("a#contact-info_location-text").text.strip().split(",")
            )
        return page_url, res, soup, location_type, addr


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        store_links = soup.select("div.item-list ul li a")
        for page_url, res, soup, location_type, addr in fetchConcurrentList(
            store_links
        ):
            with SgRequests(proxy_country="us") as http:
                try:
                    detail_url = soup.find(
                        "script", src=re.compile(r"https://knowledgetags.yextpages.net")
                    )["src"].replace("&amp;", "&")
                    res2 = http.get(detail_url)
                    _ = json.loads(res2.text.split("Yext._embed(")[1].strip()[:-1])[
                        "entities"
                    ][0]["attributes"]
                    if _.get("yextDisplayLat"):
                        latitude = _["yextDisplayLat"]
                        longitude = _["yextDisplayLng"]
                    else:
                        latitude = _["displayLat"]
                        longitude = _["displayLng"]
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_["name"],
                        street_address=_["address"],
                        city=_["city"],
                        state=_.get("state"),
                        zip_postal=_["zip"],
                        phone=_["phone"],
                        locator_domain=locator_domain,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation="; ".join(_.get("hours", [])),
                        location_type=location_type,
                        country_code=_["countryCode"],
                        raw_address=" ".join(addr).replace("\n", "").replace("\r", ""),
                    )
                except:
                    location_type = (
                        "Hearing Centre" if "hearing" in page_url else "Optician"
                    )
                    try:
                        addr = list(soup.select_one("div.store p").stripped_strings)
                    except:
                        import pdb

                        pdb.set_trace()
                        open("w.html", "w").write(res.text)
                    street_address = " ".join(addr[:-3])
                    if street_address.endswith(","):
                        street_address = street_address[:-1]
                    try:
                        coord = json.loads(
                            res.text.split("var position =")[1].split(";")[0]
                        )
                    except:
                        coord = {"lat": "", "lng": ""}
                    hours = [
                        tr["content"]
                        for tr in soup.select("table.opening--day-and-time tr")
                    ]
                    try:
                        location_name = soup.select_one(
                            "h1.store-header--title"
                        ).text.strip()
                    except:
                        location_name = soup.select_one(
                            "h1.general-information__store-name"
                        ).text.strip()
                    yield SgRecord(
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=addr[-3].replace(",", ""),
                        state=addr[-2].replace(",", ""),
                        zip_postal=addr[-1].replace(",", ""),
                        phone=soup.select_one(
                            "span.contact--store-telephone--text"
                        ).text.strip(),
                        locator_domain=locator_domain,
                        latitude=coord.get("lat"),
                        longitude=coord.get("lng"),
                        hours_of_operation="; ".join(hours),
                        location_type=location_type,
                        country_code="UK",
                        raw_address=" ".join(addr).replace("\n", "").replace("\r", ""),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
