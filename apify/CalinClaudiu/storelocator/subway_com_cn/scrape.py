from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests import SgRequests
from sgzip.dynamic import Grain_8
from sgzip.dynamic import DynamicGeoSearch
from sglogging import sglog
from sgscrape.sgrecord_id import SgRecordID
import json
from bs4 import BeautifulSoup as b4

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def strip_para(x):
    copy = []
    inside = False
    for i in x:
        if i == "<" or inside:
            inside = True
            continue
        elif i == ">":
            inside = False
            continue
        else:
            copy.append(i)
    return "".join(copy)


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def replac(x):
    x = str(x)
    x = x.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
    if len(x) < 1:
        return "<MISSING>"
    return x


class ExampleSearchIteration:
    def do(search, coord, http):
        # here you'd use self.__http, and call `found_location_at(lat, long)` for all records you find.
        lat, lng = coord

        url = str(
            f"https://locator-svc.subway.com/v3/GetLocations.ashx?callback=jQuery111103111319300901092_1617727334311&q=%7B%22InputText%22%3A%22%22%2C%22GeoCode%22%3A%7B%22name%22%3A%22%22%2C%22Latitude%22%3A{lat}%2C%22Longitude%22%3A{lng}%2C%22CountryCode%22%3A%22%22%7D%2C%22DetectedLocation%22%3A%7B%22Latitude%22%3A0%2C%22Longitude%22%3A0%2C%22Accuracy%22%3A0%7D%2C%22Paging%22%3A%7B%22StartIndex%22%3A0%2C%22PageSize%22%3A100%7D%2C%22ConsumerParameters%22%3A%7B%22metric%22%3Atrue%2C%22culture%22%3A%22en-AG%22%2C%22country%22%3A%22%22%2C%22size%22%3A%22D%22%2C%22template%22%3A%22%22%2C%22rtl%22%3Afalse%2C%22clientId%22%3A%2217%22%2C%22key%22%3A%22SUBWAY_PROD%22%7D%2C%22Filters%22%3A%5B%5D%2C%22LocationType%22%3A2%2C%22behavior%22%3A%22%22%2C%22FavoriteStores%22%3Anull%2C%22RecentStores%22%3Anull%2C%22Stats%22%3A%7B%22abc%22%3A%5B%7B%22N%22%3A%22geo%22%2C%22R%22%3A%22B%22%7D%5D%2C%22src%22%3A%22autocomplete%22%2C%22act%22%3A%22enter%22%2C%22c%22%3A%22subwayLocator%22%7D%7D&_=1617727334313".format(
                lat=lat, lng=lng
            )
        )
        headers = {}
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        locations = None
        try:
            logzilla.info(f"{url} <- in do")
            locations = SgRequests.raise_on_err(http.get(url, headers=headers)).text
            locations = locations.split("(", 1)[1]
            locations = locations.rsplit(")", 1)[0]
            locations = json.loads(locations)
        except Exception as e:
            logzilla.error(f"{e}")
        MISSING = "<MISSING>"
        if locations:
            firstfound = set()
            secondfound = set()
            foundstuff = {}
            for rec in locations["ResultData"]:
                try:
                    page_url = rec["OrderingUrl"]
                except Exception:
                    page_url = None

                try:
                    street_address = (
                        rec["Address"]["Address1"]
                        + ", "
                        + rec["Address"]["Address2"]
                        + ", "
                        + rec["Address"]["Address3"]
                    )
                except Exception:
                    street_address = None

                try:
                    city = rec["Address"]["City"]
                except Exception:
                    city = None

                try:
                    state = rec["Address"]["StateProvCode"]
                except Exception:
                    state = None

                try:
                    country_code = rec["Address"]["CountryCode"]
                except Exception:
                    country_code = None

                try:
                    zip_postal = rec["Address"]["PostalCode"]
                except Exception:
                    zip_postal = None

                try:
                    store_number = (
                        str(rec["LocationId"]["StoreNumber"])
                        + "-"
                        + str(rec["LocationId"]["SatelliteNumber"])
                    )
                except Exception:
                    store_number = ""

                try:
                    longitude = rec["Geo"]["Longitude"]
                except Exception:
                    longitude = None

                try:
                    latitude = rec["Geo"]["Latitude"]
                except Exception:
                    latitude = None

                current = {
                    "page_url": page_url if page_url else MISSING,
                    "location_name": MISSING,
                    "street_address": street_address if street_address else MISSING,
                    "city": city if city else MISSING,
                    "state": state if state else MISSING,
                    "zip_postal": zip_postal if zip_postal else MISSING,
                    "country_code": country_code if country_code else MISSING,
                    "store_number": store_number if store_number else MISSING,
                    "phone": MISSING,
                    "location_type": MISSING,
                    "latitude": latitude if latitude else MISSING,
                    "longitude": longitude if longitude else MISSING,
                    "locator_domain": "subway.com",
                    "hours_of_operation": MISSING,
                    "raw_address": MISSING,
                }
                foundstuff[current["store_number"]] = current
                firstfound.add(current["store_number"])
                search.found_location_at(latitude, longitude)
            i = 0
            for html in locations["ResultHtml"]:
                soup = b4(html, "lxml")
                i += 1
                if len(html) < 50:
                    continue
                hours = " ".join(
                    list(
                        soup.find(
                            "div", {"class": lambda x: x and "hoursTable" in x}
                        ).stripped_strings
                    )
                )

                storeno = soup.find("div", {"class": "location"})["data-id"]
                phone = soup.find("div", {"class": "locatorPhone"}).text
                foundstuff[storeno]["phone"] = phone if phone else MISSING
                foundstuff[storeno]["hours_of_operation"] = hours if hours else MISSING
                secondfound.add(storeno)
                yield SgRecord(
                    page_url=foundstuff[storeno]["page_url"],
                    location_name=foundstuff[storeno]["location_name"],
                    street_address=foundstuff[storeno]["street_address"],
                    city=foundstuff[storeno]["city"],
                    state=foundstuff[storeno]["state"],
                    zip_postal=foundstuff[storeno]["zip_postal"],
                    country_code=foundstuff[storeno]["country_code"],
                    store_number=foundstuff[storeno]["store_number"],
                    phone=foundstuff[storeno]["phone"],
                    location_type=foundstuff[storeno]["location_type"],
                    latitude=foundstuff[storeno]["latitude"],
                    longitude=foundstuff[storeno]["longitude"],
                    locator_domain=foundstuff[storeno]["locator_domain"],
                    hours_of_operation=foundstuff[storeno]["hours_of_operation"],
                    raw_address=foundstuff[storeno]["raw_address"],
                )
        this = []
        this = list(firstfound.symmetric_difference(secondfound))
        if len(this) > 0:
            for storenum in this:
                yield SgRecord(
                    page_url=foundstuff[storenum]["page_url"],
                    location_name=foundstuff[storenum]["location_name"],
                    street_address=foundstuff[storenum]["street_address"],
                    city=foundstuff[storenum]["city"],
                    state=foundstuff[storenum]["state"],
                    zip_postal=foundstuff[storenum]["zip_postal"],
                    country_code=foundstuff[storenum]["country_code"],
                    store_number=foundstuff[storenum]["store_number"],
                    phone=foundstuff[storenum]["phone"],
                    location_type=foundstuff[storenum]["location_type"],
                    latitude=foundstuff[storenum]["latitude"],
                    longitude=foundstuff[storenum]["longitude"],
                    locator_domain=foundstuff[storenum]["locator_domain"],
                    hours_of_operation=foundstuff[storenum]["hours_of_operation"],
                    raw_address=foundstuff[storenum]["raw_address"],
                )


def get_links(url, http):
    try:
        if url["count"] == "(1)":
            return (False, [url])
        urlB = "https://restaurants.subway.com/"
        headers = {}
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        logzilla.info(f"{url} <- in get-links")
        index = SgRequests.raise_on_err(
            http.get(urlB + url["link"], headers=headers)
        ).text
        data = b4(index, "lxml")
        data = data.find(
            "ul", {"class": lambda x: x and "Directory-list" in x}
        ).find_all("li")
        index = []
        for link in data:
            z = link.find("a", {"href": True, "data-count": True})
            if z:
                index.append(
                    {
                        "link": link.find("a", {"href": True})["href"],
                        "count": z["data-count"],
                    }
                )
            else:
                index.append(
                    {"link": link.find("a", {"href": True})["href"], "count": "idk"}
                )
        if url["count"] != "idk":
            return (False, index)
        else:
            return (True, index)
    except Exception:
        return (False, [])


final = []


def recu(index, http):
    global final
    for i in index:
        data = get_links(i, http)
        if data[0]:
            recu(data[1], http)
        else:
            for j in data[1]:
                if j["count"] != "idk" and j["count"] != "(1)":
                    recu([j], http)
                else:
                    final.append(j)


def grab_initial(http, state):
    global final
    index = get_links({"link": "", "count": "idk"}, http)
    recu(index[1], http)
    return final


def parse_loc(soup, url):
    try:
        page_url = url
    except Exception:
        page_url = "<MISSING>"

    try:
        street_address = soup.find("meta", {"itemprop": "streetAddress"})["content"]
    except Exception:
        street_address = "<MISSING>"

    try:
        city = soup.find("meta", {"itemprop": "addressLocality"})["content"]
    except Exception:
        city = "<MISSING>"

    try:
        state = soup.find(
            "abbr", {"class": lambda x: x and "state" in x, "itemprop": "addressRegion"}
        ).text.strip()
    except Exception:
        state = "<MISSING>"

    try:
        country_code = soup.find(
            "abbr",
            {"class": lambda x: x and "country" in x, "itemprop": "addressCountry"},
        ).text.strip()
    except Exception:
        country_code = "<MISSING>"

    try:
        zip_postal = soup.find(
            "span", {"class": "c-address-postal-code", "itemprop": "postalCode"}
        ).text.strip()
    except Exception:
        zip_postal = "<MISSING>"

    try:
        scripts = soup.find_all("script", {"type": "text/javascript"})
        thescript = None
        for i in scripts:
            if "storeID" in i.text:
                thescript = i.text
        store_number = thescript.split('storeID"')[1]
        store_number = store_number.split('"', 1)[1]
        store_number = store_number.split('"', 1)[0]
    except Exception:
        store_number = "<MISSING>"

    try:
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
    except Exception:
        longitude = "<MISSING>"

    try:
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
    except Exception:
        latitude = "<MISSING>"

    try:
        hours = soup.find("table", {"class": "c-hours-details"}).find_all(
            "tr", {"itemprop": "openingHours", "content": True}
        )
        li = []
        for i in hours:
            li.append(i["content"])
        hours = "; ".join(li)
    except Exception:
        hours = "<MISSING>"

    try:
        phone = soup.find(
            "div", {"class": lambda x: x and "hone" in x, "itemprop": "telephone"}
        ).text.strip()
    except Exception:
        phone = "<MISSING>"

    return SgRecord(
        page_url=page_url,
        location_name="<MISSING>",
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type="<MISSING>",
        latitude=latitude,
        longitude=longitude,
        locator_domain="https://restaurants.subway.com/",
        hours_of_operation=hours,
        raw_address="<MISSING>",
    )


def fetch_main(state, http):
    urlB = "https://restaurants.subway.com/"
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    for next_r in state.request_stack_iter():
        logzilla.info(f"{urlB + next_r.url} <- INDEX!")
        try:
            index = SgRequests.raise_on_err(
                http.get(urlB + next_r.url, headers=headers)
            ).text
        except Exception as e:
            if "404" in str(e) or "503" in str(e):
                continue
            else:
                raise str(e)
        data = b4(index, "lxml")
        yield parse_loc(data, str(urlB + next_r.url))


def dattafetch(search, http1):
    for coord in search:
        for item in ExampleSearchIteration.do(search, coord, http1):
            yield item


if __name__ == "__main__":

    state = CrawlStateSingleton.get_instance()

    tocrawl = [
        "cn",
        "kz",
        "ir",
        "sa",
        "rw",
        "sb",
        "sc",
        "sd",
        "sg",
        "sj",
        "sl",
        "sm",
        "sn",
        "so",
        "sr",
        "sv",
        "sy",
        "sz",
        "td",
        "tg",
        "th",
        "tj",
        "tm",
        "tn",
        "to",
        "tr",
        "tv",
        "tw",
        "ua",
        "ug",
        "uy",
        "uz",
        "va",
        "ve",
        "vi",
        "vn",
        "vu",
        "wf",
        "xg",
        "xw",
        "ye",
        "yt",
        "za",
        "zm",
        "zw",
        "ad",
        "ae",
        "af",
        "al",
        "am",
        "ao",
        "ar",
        "as",
        "at",
        "aw",
        "ax",
        "az",
    ]
    # Also reflected in readme.md

    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search = DynamicGeoSearch(
        country_codes=tocrawl,
        granularity=Grain_8(),
        expected_search_radius_miles=8,
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                },
                fail_on_empty_id=True,
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests() as http1:
            for rec in dattafetch(search, http1):
                writer.write_row(rec)
