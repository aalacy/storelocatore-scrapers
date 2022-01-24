from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries

log = SgLogSetup().get_logger("bostonmarket_com")
session = SgRequests()

headers = {
    "authority": "www.bostonmarket.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # for global locations
    countries = SearchableCountries.ALL
    for country in countries:
        if country == "PR" or country == "US":
            continue
        stores_req = session.get(
            f"https://www.bostonmarket.com/location/search?country={country}&l=en",
            headers=headers,
        )
        if "response" in stores_req.text:
            total = json.loads(stores_req.text)["response"]["count"]
            if total > 0:
                stores = json.loads(stores_req.text)["response"]["entities"]
                for store in stores:
                    store_number = "<MISSING>"
                    page_url = store.get("url", "<MISSING>")
                    if page_url != "<MISSING>":
                        page_url = "https://www.bostonmarket.com/location/" + page_url
                        location_r = session.get(page_url, headers=headers)
                        location_soup = BeautifulSoup(location_r.text, "lxml")
                        store_number = (
                            location_soup.find("div", {"class": "Core-id"})
                            .text.split("#")[-1]
                            .strip()
                        )
                    locator_domain = "bostonmarket.com"
                    location_name = store["profile"]["name"]
                    addr = store["profile"]["address"]
                    street_address = addr["line1"]
                    if addr["line2"] and len(addr["line2"]) > 0:
                        street_address = street_address + ", " + addr["line2"]

                    if addr["line3"] and len(addr["line3"]) > 0:
                        street_address = street_address + ", " + addr["line3"]

                    city = addr["city"]
                    if city:
                        location_name = location_name + " " + city

                    state = addr["region"]
                    zip = addr["postalCode"]

                    country_code = addr["countryCode"]
                    if country_code == "US" or country_code == "PR":
                        continue
                    phone = "<MISSING>"
                    try:
                        phone = store["profile"]["mainPhone"]["display"]
                    except:
                        pass

                    location_type = "Restaurant"
                    hours_list = []
                    try:
                        hours = store["profile"]["hours"]["normalHours"]
                        for hour in hours:
                            day = hour["day"]
                            if hour["isClosed"] is False:
                                time = (
                                    str(hour["intervals"][0]["start"])
                                    + " - "
                                    + str(hour["intervals"][0]["end"])
                                )
                                hours_list.append(day + ":" + time)
                            else:
                                hours_list.append(day + ":Closed")

                    except:
                        pass

                    hours_of_operation = "; ".join(hours_list).strip()

                    latitude = store["profile"]["yextDisplayCoordinate"]["lat"]
                    longitude = store["profile"]["yextDisplayCoordinate"]["long"]
                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )
    ######################################################################
    base_url = "https://www.bostonmarket.com/"

    r_state = session.get("https://www.bostonmarket.com/location/")
    soup_state = BeautifulSoup(r_state.text, "lxml")

    for state_link in soup_state.find_all("a", {"class": "Directory-listLink"}):
        s_link = state_link["href"]
        if state_link["data-count"] == "(1)":
            page_url = "https://www.bostonmarket.com/location/" + s_link
            log.info(page_url)
            location_r = session.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")

            location_name = (
                "Boston Market"
                + " "
                + location_soup.find("div", {"class": "Core-location"}).text.strip()
            )
            if "Ramstein, Miesenbach" in location_name:
                continue
            street_address = location_soup.find("meta", {"itemprop": "streetAddress"})[
                "content"
            ]
            city = location_soup.find("span", {"class": "c-address-city"}).text.strip()
            try:
                state = location_soup.find(
                    "abbr", {"itemprop": "addressRegion"}
                ).text.strip()
            except:
                state = "<MISSING>"
            if "689 N Terminal Road" in street_address:
                state = "PR"
            zipp = location_soup.find(
                "span", {"class": "c-address-postal-code"}
            ).text.strip()
            try:
                phone = location_soup.find("div", {"itemprop": "telephone"}).text
            except:
                phone = "<MISSING>"
            latitude = location_soup.find("meta", {"itemprop": "latitude"})["content"]
            longitude = location_soup.find("meta", {"itemprop": "longitude"})["content"]
            store_number = (
                location_soup.find("div", {"class": "Core-id"})
                .text.split("#")[-1]
                .strip()
            )
            try:
                hours = " ".join(
                    list(
                        location_soup.find("table", {"class": "c-hours-details"})
                        .find("tbody")
                        .stripped_strings
                    )
                ).strip()
            except:
                hours = "<MISSING>"

            yield SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US" if zipp.replace("-", "").isdigit() else "CA",
                store_number=store_number,
                phone=phone,
                location_type="Restaurant",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours,
            )
        else:
            city_link = "https://www.bostonmarket.com/location/" + state_link["href"]
            city_r = session.get(city_link)
            city_soup = BeautifulSoup(city_r.text, "lxml")

            for location in city_soup.find_all("a", {"class": "Directory-listLink"}):
                if location["data-count"] == "(1)":

                    page_url = (
                        "https://www.bostonmarket.com/location/" + location["href"]
                    )
                    log.info(page_url)
                    location_r = session.get(page_url)
                    location_soup = BeautifulSoup(location_r.text, "lxml")
                    location_name = (
                        "Boston Market"
                        + " "
                        + location_soup.find(
                            "div", {"class": "Core-location"}
                        ).text.strip()
                    )
                    if "Ramstein, Miesenbach" in location_name:
                        continue
                    street_address = location_soup.find(
                        "meta", {"itemprop": "streetAddress"}
                    )["content"]
                    city = location_soup.find(
                        "span", {"class": "c-address-city"}
                    ).text.strip()
                    state = location_soup.find(
                        "abbr", {"itemprop": "addressRegion"}
                    ).text.strip()
                    zipp = location_soup.find(
                        "span", {"class": "c-address-postal-code"}
                    ).text.strip()
                    try:
                        phone = location_soup.find(
                            "div", {"itemprop": "telephone"}
                        ).text
                    except:
                        phone = "<MISSING>"
                    latitude = location_soup.find("meta", {"itemprop": "latitude"})[
                        "content"
                    ]
                    longitude = location_soup.find("meta", {"itemprop": "longitude"})[
                        "content"
                    ]
                    store_number = (
                        location_soup.find("div", {"class": "Core-id"})
                        .text.split("#")[-1]
                        .strip()
                    )
                    try:
                        hours = " ".join(
                            list(
                                location_soup.find(
                                    "table", {"class": "c-hours-details"}
                                )
                                .find("tbody")
                                .stripped_strings
                            )
                        ).strip()
                    except:
                        hours = "<MISSING>"

                    yield SgRecord(
                        locator_domain=base_url,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code="US" if zipp.replace("-", "").isdigit() else "CA",
                        store_number=store_number,
                        phone=phone,
                        location_type="Restaurant",
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours,
                    )
                else:
                    store_link = (
                        "https://www.bostonmarket.com/location/" + location["href"]
                    )
                    store_r = session.get(store_link)
                    store_soup = BeautifulSoup(store_r.text, "lxml")

                    for location in store_soup.find_all(
                        "a", {"class": "Teaser-titleLink"}
                    ):
                        page_url = location["href"].replace(
                            "..", "https://www.bostonmarket.com/location"
                        )
                        location_r = session.get(page_url)
                        location_soup = BeautifulSoup(location_r.text, "lxml")

                        log.info(page_url)
                        location_name = (
                            "Boston Market"
                            + " "
                            + location_soup.find(
                                "div", {"class": "Core-location"}
                            ).text.strip()
                        )
                        if "Ramstein, Miesenbach" in location_name:
                            continue
                        street_address = location_soup.find(
                            "meta", {"itemprop": "streetAddress"}
                        )["content"]
                        city = location_soup.find(
                            "span", {"class": "c-address-city"}
                        ).text.strip()
                        state = location_soup.find(
                            "abbr", {"itemprop": "addressRegion"}
                        ).text.strip()
                        zipp = location_soup.find(
                            "span", {"class": "c-address-postal-code"}
                        ).text.strip()
                        try:
                            phone = location_soup.find(
                                "div", {"itemprop": "telephone"}
                            ).text
                        except:
                            phone = "<MISSING>"
                        latitude = location_soup.find("meta", {"itemprop": "latitude"})[
                            "content"
                        ]
                        longitude = location_soup.find(
                            "meta", {"itemprop": "longitude"}
                        )["content"]
                        store_number = (
                            location_soup.find("div", {"class": "Core-id"})
                            .text.split("#")[-1]
                            .strip()
                        )
                        try:
                            hours = " ".join(
                                list(
                                    location_soup.find(
                                        "table", {"class": "c-hours-details"}
                                    )
                                    .find("tbody")
                                    .stripped_strings
                                )
                            ).strip()
                        except:
                            hours = "<MISSING>"

                        yield SgRecord(
                            locator_domain=base_url,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zipp,
                            country_code="US"
                            if zipp.replace("-", "").isdigit()
                            else "CA",
                            store_number=store_number,
                            phone=phone,
                            location_type="Restaurant",
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours,
                        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
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
