from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote as stdlib_unquote
from lxml import etree
import ssl
import html as ht


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("canadagoose_com")
MAX_WORKERS = 1

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Host": "hosted.where2getit.com",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
}


def fetch_records(idx, quoted_url, sgw: SgWriter):
    """
    NOTE: So far, I could not be able to make it work.
    I tried every method that I know of to circumvent the anti-scraping bot but
    unfortunately, could not make it using cloudscraper, SgFirefox, SgChrome, Chrome, requests, sgrequests with redsidential Proxy.
    However, found an alternative API source ( official ) which is a bit tricky but at least it does the job.
    """

    logger.info(f"[{idx}] PullingDataFrom: {stdlib_unquote(quoted_url)}")
    with SgRequests(proxy_country="us") as http:
        r = http.get(quoted_url, headers=headers)
        sel = etree.fromstring(bytes(r.text, encoding="utf-8"))
        pois = sel.xpath("//poi")
        for idx, p in enumerate(pois[0:]):
            locname = p.xpath(".//name/text()")[0]
            locname = " ".join(locname.split())
            if "canada goose" not in locname.lower():
                logger.info(f"This store is not it's own store: {locname} Dropping!")
                return
            logger.info(f"[{idx}] Name: {locname}")
            sta1 = "".join(p.xpath(".//address1/text()"))
            sta2 = "".join(p.xpath(".//address2/text()"))
            sta = ""
            if sta1 and sta2:
                sta = sta1 + ", " + sta2
            elif sta1 and not sta2:
                sta = sta1
            elif not sta1 and sta2:
                sta = sta2
            else:
                sta = ""
            city = "".join(p.xpath(".//city/text()"))
            state = ""
            state_state = "".join(p.xpath(".//state/text()"))
            state_province = "".join(p.xpath(".//province/text()"))
            if state_state:
                state = state_state
            else:
                if state_province:
                    state = state_province
                else:
                    state = ""

            pc = "".join(p.xpath(".//postalcode/text()"))
            country = "".join(p.xpath(".//country/text()"))
            phone = p.xpath(".//phone/text()")
            phone = "".join(phone)
            sn = "".join(p.xpath(".//clientkey/text()"))

            # hours
            frio = "".join(p.xpath(".//friopen/text()"))
            fric = "".join(p.xpath(".//friclose/text()"))
            sato = "".join(p.xpath(".//satopen/text()"))
            satc = "".join(p.xpath(".//satclose/text()"))
            suno = "".join(p.xpath(".//sunopen/text()"))
            sunc = "".join(p.xpath(".//sunclose/text()"))
            mono = "".join(p.xpath(".//monopen/text()"))
            monc = "".join(p.xpath(".//monclose/text()"))
            tueo = "".join(p.xpath(".//tueopen/text()"))
            tuec = "".join(p.xpath(".//tueclose/text()"))
            wedo = "".join(p.xpath(".//wedopen/text()"))
            wedc = "".join(p.xpath(".//wedclose/text()"))
            thro = "".join(p.xpath(".//thropen/text()"))
            thrc = "".join(p.xpath(".//thrclose/text()"))
            lat = "".join(p.xpath(".//latitude/text()"))
            lng = "".join(p.xpath(".//longitude/text()"))

            frioc = frio + " - " + fric if frio and fric else ""
            satoc = sato + " - " + satc if sato and satc else ""
            sunoc = suno + " - " + sunc if suno and sunc else ""
            monoc = mono + " - " + monc if mono and monc else ""
            tueoc = tueo + " - " + tuec if tueo and tuec else ""
            wedoc = wedo + " - " + wedc if wedo and wedc else ""
            throc = thro + " - " + thrc if thro and thrc else ""

            hours = f"{frioc}; {satoc}; {sunoc}; {monoc}; {tueoc}; {wedoc}; {throc}"
            hours = hours.replace("; ; ; ; ; ;", "").strip()

            sta = " ".join(sta.split())
            sta = ht.unescape(sta)
            website = "".join(p.xpath(".//website/text()"))

            item = SgRecord(
                locator_domain="canadagoose.com",
                page_url=website,
                location_name=locname,
                street_address=sta,
                city=city,
                state=state,
                zip_postal=pc,
                country_code=country,
                store_number=sn,
                phone=phone,
                location_type="",
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
                raw_address=sta,
            )

            sgw.write_row(item)


def generate_api_endpoint_urls():
    api_endpoint_urls = []
    list_of_countries = {
        1: ("AD", "Andorra"),
        2: ("AU", "Australia"),
        3: ("AT", "Austria"),
        4: ("AZ", "Azerbaijan"),
        5: ("BE", "Belgium"),
        6: ("CA", "Canada"),
        7: ("CN", "Mainland China 中国大陆"),
        8: ("HK", "Hong Kong S.A.R. 香港特别行政区 "),
        9: ("MO", "China - Macau"),
        10: ("TW", "Taiwan 台湾地区"),
        11: ("CY", "Cyprus"),
        12: ("CZ", "Czech Republic"),
        13: ("DK", "Denmark"),
        14: ("EE", "Estonia"),
        15: ("FI", "Finland"),
        16: ("FR", "France"),
        17: ("DE", "Germany"),
        18: ("GR", "Greece"),
        19: ("GL", "Greenland"),
        20: ("HU", "Hungary"),
        21: ("IS", "Iceland"),
        22: ("IE", "Ireland"),
        23: ("IT", "Italy"),
        24: ("JP", "Japan"),
        25: ("JO", "Jordan"),
        26: ("KZ", "Kazakhstan"),
        27: ("KP", "Korea, People Republic Of"),
        28: ("KW", "Kuwait"),
        29: ("LV", "Latvia"),
        30: ("LB", "Lebanon"),
        31: ("LT", "Lithuania"),
        32: ("LU", "Luxembourg"),
        33: ("MX", "Mexico"),
        34: ("MC", "Monaco"),
        35: ("MN", "Mongolia"),
        36: ("NL", "Netherlands"),
        37: ("NZ", "New Zealand"),
        38: ("NO", "Norway"),
        39: ("PL", "Poland"),
        40: ("PT", "Portugal"),
        41: ("QA", "Qatar"),
        42: ("RO", "Romania"),
        43: ("RU", "Russia"),
        44: ("SK", "Slovakia"),
        45: ("ES", "Spain"),
        46: ("SE", "Sweden"),
        47: ("CH", "Switzerland"),
        48: ("TR", "Turkey"),
        49: ("UA", "Ukraine"),
        50: ("AE", "United Arab Emirates"),
        51: ("UK", "United Kingdom"),
        52: ("US", "United States of America"),
    }
    WHERE_TO_GET = "https://hosted.where2getit.com/canadagoose/ajax?"
    APPKEY = "8949AAF8-550E-11DE-B2D5-479533A3DD35"
    LIMIT = 1000
    RADIUS = 5000

    for country_to_crawl in list_of_countries:
        COUNTRY_CODE = list_of_countries[country_to_crawl][0]
        logger.info(f"CountryCode: {COUNTRY_CODE}")
        url_formed = f"{WHERE_TO_GET}&xml_request=%3Crequest%3E%3Cappkey%3E{APPKEY}%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EStoreLocator%3C%2Fobjectname%3E%3Climit%3E{LIMIT}%3C%2Flimit%3E%3Corder%3Erank%3A%3Anumeric%3C%2Forder%3E%3Cwhere%3E%3Ccity%3E%3Cne%3EQuam%3C%2Fne%3E%3C%2Fcity%3E%3Ccountry%3E%3Ceq%3E{COUNTRY_CODE}%3C%2Feq%3E%3C%2Fcountry%3E%3C%2Fwhere%3E%3Cradiusuom%3E{RADIUS}%3C%2Fradiusuom%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
        logger.info(f"Quoted_URL: {url_formed}")
        logger.info(f"Unquoted_URL: {stdlib_unquote(url_formed)}")
        api_endpoint_urls.append(url_formed)
    return api_endpoint_urls


def fetch_data(sgw: SgWriter):
    API_ENDPOINT_URL__US = [
        "https://hosted.where2getit.com/canadagoose/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8949AAF8-550E-11DE-B2D5-479533A3DD35%3C%2Fappkey%3E%3Cgeoip%3E1%3C%2Fgeoip%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Corder%3Erank%3A%3Anumeric%2C_DISTANCE%3C%2Forder%3E%3Catleast%3E1%3C%2Fatleast%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3Ccountry%3E%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E5000%3C%2Fsearchradius%3E%3Cradiusuom%3Emile%3C%2Fradiusuom%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    ]
    API_ENDPOINT_URLS = generate_api_endpoint_urls()
    API_ENDPOINT_URLS.extend(API_ENDPOINT_URL__US)

    # API ENDPOINT URL: Structure of the URL
    # This is just for understanding how the URL would be construcuted.
    # https://hosted.where2getit.com/canadagoose/ajax?
    # &xml_request=<request><appkey>8949AAF8-550E-11DE-B2D5-479533A3DD35</appkey><geoip>1</geoip>
    # <formdata+id="locatorsearch">
    # <dataview>store_default</dataview><order>rank::numeric,_DISTANCE</order>
    # <atleast>1</atleast><geolocs><geoloc><addressline></addressline><longitude></longitude><latitude></latitude>
    # <country></country></geoloc></geolocs><searchradius>10|25|50|100|250|350|500</searchradius>
    # <radiusuom>mile</radiusuom></formdata></request>

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records, idx, api_url, sgw)
            for idx, api_url in enumerate(API_ENDPOINT_URLS[6:10])
        ]
        tasks.extend(task_us)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")  # noqa


if __name__ == "__main__":
    scrape()
