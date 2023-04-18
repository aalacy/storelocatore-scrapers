from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sgselenium import SgChrome
from sglogging import SgLogSetup
import re
from urllib.parse import urljoin, urlparse
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("lithia")

locator_domain = "https://www.lithia.com"
base_url = "https://www.lithia.com/service-locations/index.htm"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def get_sp(url, http, driver):
    res = http.get(url, headers=_headers)
    res_txt = None
    if res.status_code != 200:
        try:
            driver.get(url)
            res_txt = driver.page_source
        except:
            pass
    else:
        res_txt = res.text
    return res_txt


def record_initial_requests(http, driver):
    driver.get(base_url)
    soup = bs(driver.page_source, "lxml")
    store_list = soup.select("li.info-window")
    logger.info(len(store_list))
    for _ in store_list:
        page_url = _.strong.a["href"]
        street_address = (
            city
        ) = zip_postal = _state = raw_address = latitude = longitude = ""
        if _.select_one("p.adr a"):
            raw_address = " ".join(_.select_one("p.adr a").stripped_strings)
        if not raw_address:
            logger.info("==========")
            continue
        if _.select_one("span.street-address"):
            street_address = _.select_one("span.street-address").text.strip()
        if _.select_one("span.locality"):
            city = _.select_one("span.locality").text.strip()
        if _.select_one("span.region"):
            _state = _.select_one("span.region").text.strip()
        if _.select_one("span.postal-code"):
            zip_postal = _.select_one("span.postal-code").text.strip()
        location_name = _.strong.text.strip()
        if _.select_one("span.latitude"):
            latitude = _.select_one("span.latitude").text.strip()
        if _.select_one("span.longitude"):
            longitude = _.select_one("span.longitude").text.strip()
        id = ""
        for cls in _["class"]:
            if cls.startswith("info-window-"):
                id = cls.split("-")[-1].strip()
                break
        country_code = "US"
        if zip_postal and not zip_postal.replace("-", "").isdigit():
            country_code = "CA"
        store = dict(
            id=id,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=_state,
            zip_postal=zip_postal,
            latitude=latitude,
            longitude=longitude,
            country_code=country_code,
            raw_address=raw_address,
        )
        phone = ""
        hours = []
        if page_url == "#":
            yield _d(store, phone, hours, base_url)
            continue
        _url = urlparse(page_url).netloc
        if not _url:
            continue
        page_url = "https://" + _url
        logger.info(page_url)
        is_chrome_try = False
        try:
            sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
        except:
            try:
                if "www" not in page_url:
                    url = "https://www." + urlparse(page_url).netloc
                    sp1 = bs(http.get(url, headers=_headers).text, "lxml")
                else:
                    is_chrome_try = True
                    driver.get(page_url)
                    sp1 = bs(driver.page_source, "lxml")
            except:
                if not is_chrome_try:
                    driver.get(page_url)
                    sp1 = bs(driver.page_source, "lxml")
                else:
                    logger.info("wwwww ========")
                    yield _d(store, phone, hours, base_url)
                    continue

        if sp1.select("table.mabel-bhi-businesshours"):
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("table.mabel-bhi-businesshours")[0].select("tr")
            ]
            _addr = sp1.select_one("span.fusion-contact-info-phone-number").text.strip()
            phone = _addr.split("|")[0].split("!")[-1].strip()
            store["zip_postal"] = _addr.split("|")[-1].split()[-1]
            store["raw_address"] = _addr.split("|")[-1]
        elif sp1.select("div#hours1-app-root ul li"):
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div#hours1-app-root ul li")
            ]
            phone = sp1.select_one("li.phone1 span.value").text.strip()
        elif sp1.select_one("a.header-contact__link"):
            hr_info = bs(
                sp1.select_one("a.header-contact__link.header-contact__hours-link")[
                    "data-content"
                ],
                "lxml",
            )
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in hr_info.select("table.schedule-table tr")
            ]
            ph_info = bs(
                sp1.select_one("a.header-contact__link.header-contact__phones-link")[
                    "data-content"
                ],
                "lxml",
            )
            phone = ph_info.a.text.strip()
        else:
            url = sp1.find("a", string=re.compile(r"^Contact us", re.I))
            if url and url["href"] != "#":
                contact_url = url["href"]
                if not contact_url.startswith("http"):
                    contact_url = page_url + contact_url
                logger.info(contact_url)
                res2 = get_sp(contact_url, http, driver)
                sp2 = bs(
                    res2,
                    "lxml",
                )
                if sp2.select_one("li.phone-main a"):
                    phone = list(sp2.select_one("li.phone-main a").stripped_strings)[0]
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in sp2.select("span.hours-sales ul li")
                    ]
                elif sp2.select_one("li.phone1 span.value"):
                    phone, hours = _ddc_hr(sp2)
                elif sp2.select_one("span.callNowClass"):
                    phone = sp2.select_one("span.callNowClass").text.strip()
                elif sp2.select_one("span.header_phone_number"):
                    phone = sp2.select_one("span.header_phone_number").text.strip()
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in sp2.select("div.hours-wrapper")[0].select("table tr")
                    ]
                else:
                    pass
            elif sp1.select_one("a[data-location='page-schedule-service-button']"):
                contact_url = sp1.select_one(
                    "a[data-location='page-schedule-service-button']"
                )["href"]
                if not contact_url.startswith("http"):
                    contact_url = page_url + contact_url
                logger.info(contact_url)
                res2 = get_sp(contact_url, http, driver)
                sp2 = bs(res2, "lxml")
                if sp2.select_one("li.phone1 span.value"):
                    phone, hours = _ddc_hr(sp2)
            elif sp1.select_one('a[data-action="maplinkout"]'):
                contact_url = sp1.select_one('a[data-action="maplinkout"]')["href"]
                if not contact_url.startswith("http"):
                    contact_url = page_url + contact_url
                logger.info(contact_url)
                res2 = get_sp(contact_url, http, driver)
                sp2 = bs(res2, "lxml")
                if sp2.select_one("li.phone1 span.value"):
                    phone, hours = _ddc_hr(sp2)
                elif sp2.select_one('span[itemprop="telephone"]'):
                    phone = sp2.select_one('span[itemprop="telephone"]').text.strip()
                if sp2.select_one('dl[itemprop="openingHoursSpecification"]'):
                    days = [dd.text.strip() for dd in sp2.select("dt")]
                    times = [" - ".join(dd.stripped_strings) for dd in sp2.select("dd")]
                    for x in range(len(days)):
                        hours.append(f"{days[x]}: {times[x]}")
            elif sp1.find("a", href=re.compile(r"^/hours")):
                url = page_url + sp1.find("a", href=re.compile(r"^/hours"))["href"]
                logger.info(url)
                res2 = get_sp(url, http, driver)
                sp2 = bs(res2, "lxml")
                if sp2.select_one("a.callNowClass span"):
                    phone = sp2.select_one("a.callNowClass span").text.strip()
                if sp2.select_one("a.callNowClass"):
                    phone = sp2.select_one("a.callNowClass").text.strip()
                elif sp2.select_one('span[itemprop="telephone"]'):
                    phone = sp2.select_one('span[itemprop="telephone"]').text.strip()

                _hr = sp2.find("strong", string=re.compile(r"Sales"))
                if _hr:
                    hours = [
                        " ".join(hh.stripped_strings)
                        for hh in _hr.find_parent("div").select("p")[1:]
                    ]
                elif sp2.select("div#SalesHours table tbody tr"):
                    for hh in sp2.select("div#SalesHours table tbody tr"):
                        td = list(hh.stripped_strings)
                        hours.append(f"{td[0]}: {td[1]} - {td[2]}")
                else:
                    hours = [
                        " ".join(hh.stripped_strings)
                        for hh in sp2.select("div.widget-hours div#panel1 div.row")[1:]
                    ]
            elif sp1.select('div[data-name="section-1-row"] > div'):
                for loc in sp1.select('div[data-name="section-1-row"] > div'):
                    url = loc.select_one("div.cta-content a.btn")["href"]
                    if not url.startswith("http"):
                        url = page_url + url
                    if url.endswith("/"):
                        url = url[:-1]
                    logger.info(url)
                    res2 = get_sp(url, http, driver)
                    sp2 = bs(res2, "lxml")
                    if sp2.select_one("p.adr a"):
                        contact_url = sp2.select_one("p.adr a")["href"]
                        if not contact_url.startswith("http"):
                            contact_url = urljoin(url, contact_url)
                        logger.info(contact_url)
                        sp3 = bs(http.get(contact_url, headers=_headers).text, "lxml")
                        if sp3.select_one("li.phone1 span.value"):
                            phone, hours = _ddc_hr(sp3)
                            yield _d(store, phone, hours, url)
                            continue
                continue
            elif sp1.find("", string=re.compile(r"HOURS OF OPERATION:", re.I)):
                hours = list(
                    sp1.find("", string=re.compile(r"HOURS OF OPERATION:", re.I))
                    .find_parent()
                    .stripped_strings
                )[1:]
            elif sp1.find("a", href=re.compile(r"/directions", re.I)):
                contact_url = sp1.find("a", href=re.compile(r"/directions", re.I))[
                    "href"
                ]
                if not contact_url.startswith("http"):
                    contact_url = page_url + contact_url
                logger.info(contact_url)
                res2 = get_sp(contact_url, http, driver)
                sp2 = bs(res2, "lxml")
                if sp2.select_one("li.phone1 span.value"):
                    phone, hours = _ddc_hr(sp2)
            elif sp1.find("a", href=re.compile(r"/schedule", re.I)):
                contact_url = sp1.find("a", href=re.compile(r"/schedule", re.I))["href"]
                if not contact_url.startswith("http"):
                    contact_url = page_url + contact_url
                logger.info(contact_url)
                res2 = get_sp(contact_url, http, driver)
                sp2 = bs(res2, "lxml")
                phone = sp2.select_one(
                    "div.widget-hours div#panel1 div.row a"
                ).text.strip()
                hours = [
                    " ".join(hh.stripped_strings)
                    for hh in sp2.select("div.widget-hours div#panel1 div.row")[1:]
                ]

        yield _d(store, phone, hours, page_url)


def _ddc_hr(sp1):
    hours = []
    phone = sp1.select_one("li.phone1 span.value").text.strip()
    if sp1.select("ul.ddc-hours  li"):
        hours = [
            ": ".join(hh.stripped_strings)
            for hh in sp1.select("ul.ddc-hours")[0].select("li")
        ]

    return phone, hours


def _d(store, phone, hours, page_url):
    return SgRecord(
        page_url=page_url,
        store_number=store["id"],
        location_name=store["location_name"],
        street_address=store["street_address"],
        city=store["city"],
        state=store["state"],
        zip_postal=store["zip_postal"],
        latitude=store["latitude"],
        longitude=store["longitude"],
        country_code=store["country_code"],
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours).replace("\u200b", ""),
        raw_address=store["raw_address"],
    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        with SgRequests(
            proxy_country="us",
            retries_with_fresh_proxy_ip=1,
            dont_retry_status_codes=set([500, 501, 503]),
        ) as http:
            with SgChrome() as driver:
                for rec in record_initial_requests(http, driver):
                    writer.write_row(rec)
