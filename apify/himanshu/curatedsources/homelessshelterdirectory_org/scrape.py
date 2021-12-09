from requests.exceptions import RequestException  # ignore_check
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED
import threading
import random
import time
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import SgLogSetup
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("homelessshelterdirectory_org")


show_logs = False
thread_local = threading.local()
max_workers = 64
base_url = "https://www.homelessshelterdirectory.org/"


def sleep(min=0.5, max=2.5):
    duration = random.uniform(min, max)
    time.sleep(duration)


def log(*args, **kwargs):
    if show_logs is True:
        logger.info(" ".join(map(str, args)), **kwargs)
        logger.info("")


def get_session(reset=False):
    # give each thread its own session object.
    # when using proxy, each thread's session will have a unique IP, and we'll switch IPs every 10 requests
    if (
        (not hasattr(thread_local, "session"))
        or (hasattr(thread_local, "request_count") and thread_local.request_count == 10)
        or (reset is True)
    ):
        thread_local.session = SgRequests()
        reset_request_count()
        # print out what the new IP is ...
        if show_logs is True:
            r = thread_local.session.get("https://jsonip.com/")
            log(
                f"new IP for thread id {threading.current_thread().ident}: {r.json()['ip']}"
            )

    return thread_local.session


def reset_request_count():
    if hasattr(thread_local, "request_count"):
        thread_local.request_count = 0


def increment_request_count():
    if not hasattr(thread_local, "request_count"):
        thread_local.request_count = 1
    else:
        thread_local.request_count += 1


def get(url, attempt=1):

    if attempt == 5:
        log(
            f"***** cannot get {url} on thread {threading.current_thread().ident} after {attempt} tries. giving up *****"
        )
        return None

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,la;q=0.8",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        sleep()
        session = get_session()
        session.get_session().cookies.clear()
        log(f"getting {url}")
        r = session.get(url, headers=headers, timeout=15)
        log(f"status for {url} >>> ", r.status_code)
        r.raise_for_status()
        increment_request_count()
        return r

    except (RequestException, OSError) as err:
        if err.response is not None and err.response.status_code == 404:
            log(f"Got 404 getting {url}")
            return None

        # attempt to handle 403 forbidden and other errors such as "cannot connect to proxy, timed out, etc"
        log(f"***** error getting {url} on thread {threading.current_thread().ident}")
        log(err)
        log("****** resetting session")
        session = get_session(reset=True)
        # try this request again
        return get(url, attempt=attempt + 1)


def crawl_state_url(state_url):
    city_urls = []
    r = get(state_url)
    if not r:
        return city_urls

    if len(r.text) > 0:
        state_sel = lxml.html.fromstring(r.text)
        cities = state_sel.xpath("//table//tr[position()>1]/td[1]/a/@href")
        for url in cities:
            city_urls.append(url)

    return city_urls


def crawl_city_url(url):
    location_urls = []
    r = get(url)
    if not r:
        return location_urls
    soup = bs(r.content.decode("utf-8", "ignore"), "lxml")
    for url in soup.find_all("a", {"class": "btn btn_red"}):
        page_url = url["href"]
        if "homelessshelterdirectory.org" not in page_url:
            continue
        location_urls.append(page_url)
    return location_urls


def crawl_location_url(url):
    r = get(url)
    if not r:
        return None
    location_soup = bs(r.content.decode("utf-8", "ignore"), "lxml")
    if len(r.text) > 0:
        location_sel = lxml.html.fromstring(r.text)

        try:
            location_name = location_soup.find("h1", {"class": "entry_title"}).text
        except:
            location_name = "<MISSING>"

        addr = list(
            location_soup.find("div", {"class": "col col_4_of_12"})
            .find("p")
            .stripped_strings
        )
        street_address = addr[1]
        city = addr[-1].split(",")[0]
        state = addr[-1].split(",")[1].split("-")[0]
        if len(addr[-1].split(",")[1].split("-")) == 2:
            zipp = addr[-1].split(",")[1].split()[-1]
        else:
            zipp = "<MISSING>"
        phone = "".join(
            location_sel.xpath(
                '//div[@class="col col_8_of_12"]//a[contains(@href,"tel:")]/text()'
            )
        ).strip()

        if "ext" in phone.lower():
            phone = phone.lower().split("ext")[0].strip()
        if "or" in phone:
            phone = phone.split("or")[0]
        store_number = "<MISSING>"

        lat = "<MISSING>"
        lng = "<MISSING>"
        update_date = location_sel.xpath('//span[@class="meta_date"]/text()')
        if len(update_date) > 0:
            update_date = (
                "".join(update_date[0]).strip().replace("Last updated", "").strip()
            )
        else:
            update_date = "<MISSING>"

        hours = location_sel.xpath('//div[@class="col col_12_of_12 hours"]/ul/li')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("text()")).strip()
            time = "".join(hour.xpath("span/text()")).strip()
            hours_list.append(day + ": " + time)

        hours_of_operation = "; ".join(hours_list).strip()

        return SgRecord(
            locator_domain=base_url,
            page_url=url,
            location_name=location_name,
            street_address=street_address.replace("?", "").strip(),
            city=city,
            state=state,
            zip_postal=zipp,
            country_code="US",
            store_number=store_number,
            phone=phone,
            location_type=update_date,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
        )


def fetch_data():

    state_urls = []
    city_urls = []
    loc_urls = []

    r = get(base_url)
    if not r:
        logger.info("could not get initial locator page. giving up")
        raise SystemExit

    soup = bs(r.content, "lxml")
    for s_link in soup.find_all("area", {"shape": "poly"}):
        log(s_link["href"])
        state_urls.append(s_link["href"])
        # break

    for url in state_urls:
        log(url)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(crawl_state_url, url) for url in state_urls]
        # return when all finished or after 20 min regardless
        done, not_done = wait(futures, timeout=1200, return_when=ALL_COMPLETED)
        log(f"Done crawl_state futures: {len(done)}")
        log(f"Not Done crawl_state futures: {len(not_done)}")
        for result in futures:
            try:
                cities_in_state = result.result()
                city_urls.extend(cities_in_state)
            except Exception as ex:
                log(f"crawl_state_url with result {result} threw exception: {ex}")

    log(f"found {len(city_urls)} city urls")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(crawl_city_url, url) for url in city_urls]
        # return when all finished or after 2 hours regardless
        done, not_done = wait(futures, timeout=7200, return_when=ALL_COMPLETED)
        log(f"Done crawl_city futures: {len(done)}")
        log(f"Not Done crawl_city futures: {len(not_done)}")
        for result in futures:
            location_urls = []
            try:
                location_urls = result.result()
            except Exception as ex:
                log(f"crawl_city_url with result {result} threw exception: {ex}")
            for url in location_urls:
                if url not in loc_urls:
                    loc_urls.append(url)

    log(f"found {len(loc_urls)} location urls")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(crawl_location_url, url) for url in loc_urls]
        for result in as_completed(futures):
            store = None
            try:
                store = result.result()
            except Exception as ex:
                log(f"crawl_location_url with result {result} threw exception: {ex}")
                raise
            if store:
                yield store


def scrape():
    log("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log(f"No of records being processed: {count}")
    log("Finished")


if __name__ == "__main__":
    scrape()
