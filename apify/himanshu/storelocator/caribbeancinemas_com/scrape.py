from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("caribbeancinemas_com")
session = SgRequests()


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    elif "&q=" in map_link:
        latitude = map_link.split("&q=")[1].split(",")[0].strip()
        longitude = map_link.split("&q=")[1].split(",")[1].strip()
    elif "?q=" in map_link:
        latitude = map_link.split("?q=")[1].split(",")[0].strip()
        longitude = map_link.split("?q=")[1].split(",")[1].strip().split("&")[0].strip()

    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # it will used in store data.
    base_url = "https://caribbeancinemas.com/"
    locator_domain = "https://caribbeancinemas.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    }

    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    stores_sel = lxml.html.fromstring(r.text)

    footer = stores_sel.xpath(
        '//footer//div[contains(@class,"scale-with-grid one-fourth column")]'
    )
    for foot in footer:
        if "advert" in "".join(foot.xpath("@id")).strip():
            continue

        urls = foot.xpath(".//a")
        for u in urls:
            url_text = "".join(u.xpath(".//text()")).strip()
            if "ARUBA" != url_text and "PANAMA" != url_text and "TRINIDAD" != url_text:
                p_url = "".join(u.xpath("@href")).strip().split("/")
                if len(p_url) != 4:
                    page_url = "https:" + "".join(u.xpath("@href")).strip()
                else:
                    page_url = "".join(u.xpath("@href")).strip()

                if (
                    "caribbeancinemas.com" not in page_url
                    or "/?aruba" in page_url
                    or "/?trinidad" in page_url
                    or "penonome-cinemas" in page_url
                    or "santiago-cinemas" in page_url
                    or "guyana" in page_url
                ):
                    continue
                logger.info(page_url)
                rr = session.get(page_url, headers=headers)
                rr_soup = BeautifulSoup(rr.text, "lxml")
                store_sel = lxml.html.fromstring(rr.text)
                try:
                    coords = (
                        rr_soup.find_all("div", class_="section")[0]
                        .find("div", class_="column four-fifth")
                        .find("iframe")
                    )
                    map_link = coords["src"]
                    latitude, longitude = get_latlng(map_link)

                    info = (
                        rr_soup.find("div", class_="sections_group")
                        .find("div", class_="items_group clearfix")
                        .find("div", {"id": "cineinfo"})
                    )
                    location_name = info.h2.text.strip()

                    list_phone = list(info.find("li", class_="phone").stripped_strings)
                    if list_phone != []:
                        phone = list_phone[0].strip()
                    else:
                        phone = "<MISSING>"
                    address = info.find("li", class_="address")
                    list_address = list(address.stripped_strings)
                    if list_address == []:
                        street_address = "<MISSING>"
                        city = page_url.split("/")[-2].split("-")[0].strip()

                    else:
                        if len(list_address) > 1:
                            location_name = list_address[0].strip()
                            if len(list_address[-1].split(",")) > 1:
                                street_address = " ".join(
                                    list_address[-1].split(",")[:-1]
                                ).strip()
                                city = "<MISSING>"
                                state = "<MISSING>"
                            else:
                                if len(list_address[-1].split()) > 1:
                                    street_address = list_address[-1].strip()
                                    location_name = list_address[0].strip()
                                else:
                                    street_address = " ".join(
                                        list_address[0].split()[3:]
                                    ).strip()
                                    location_name = " ".join(
                                        list_address[0].split()[:3]
                                    )
                                city = "<MISSING>"
                                state = "<MISSING>"
                        else:
                            street_address = list_address[0].strip()
                            location_name = "<MISSING>"
                            city = "<MISSING>"
                            state = "<MISSING>"

                    if location_name == "<MISSING>":
                        location_name = "".join(
                            store_sel.xpath('//div[@class="contact_box"]/h2/b/text()')
                        ).strip()

                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )

                except:
                    continue

    link = (
        soup.find("nav", {"id": "menu"})
        .find("li", class_="menu-item menu-item-has-children")
        .find("ul", class_="sub-menu mfn-megamenu mfn-megamenu-5")
    )
    for li in link.find_all("li", class_="menu-item"):
        try:
            if "#MORE" != li.a["href"]:
                page_url = "https:" + li.a["href"]
                logger.info(page_url)
                r_loc = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(r_loc.text)
                soup_loc = BeautifulSoup(r_loc.text, "lxml")
                coords = (
                    soup_loc.find_all("div", class_="section")[0]
                    .find("div", class_="column four-fifth")
                    .find("iframe")
                )
                map_link = coords["src"]
                latitude, longitude = get_latlng(map_link)

                info = (
                    soup_loc.find("div", class_="sections_group")
                    .find("div", class_="items_group clearfix")
                    .find("div", {"id": "cineinfo"})
                )
                phone = info.find("li", class_="phone").text.strip()
                address = info.find("li", class_="address")
                list_address = list(address.stripped_strings)

                if len(list_address) > 1:
                    phone_list = re.findall(
                        re.compile(".?(\\(?\\d{3}\\D{0,3}\\d{3}\\D{0,3}\\d{4}).?"),
                        str(list_address[-1]),
                    )

                    if phone_list == []:
                        location_name = list_address[0].strip()
                        tag_address = list_address[1].split(",")
                        city = info.h2.text.strip()
                        if len(tag_address) > 1:
                            state = tag_address[-1].split()[0].strip()
                            zipp = tag_address[-1].split()[-1].strip()
                            street_address = " ".join(tag_address[:-1]).strip()
                        else:
                            street_address = tag_address[0].strip()
                            state = "<MISSING>"
                            zipp = "<MISSING>"

                    else:
                        location_name = info.h2.text.strip()
                        street_address = list_address[0].split(",")[0].strip()
                        city = list_address[0].split(",")[1].strip()
                        state = list_address[0].split(",")[-1].split()[0].strip()
                        zipp = list_address[0].split(",")[-1].split()[-1].strip()
                else:
                    location_name = info.h2.text.strip()
                    street_address = ",".join(list_address[0].split(",")[:-2]).strip()
                    city = list_address[0].split(",")[-2].strip()
                    state = list_address[0].split(",")[-1].split()[0].strip()
                    zipp = list_address[0].split(",")[-1].split()[-1].strip()
                if "Ponce" == state or "Hatillo" == state:
                    state = "<MISSING>"
                if (
                    "Guayama" not in city
                    and "Fajardo" not in city
                    and "Aguadilla" not in city
                ):
                    city = "<MISSING>"

                if location_name == "<MISSING>":
                    location_name = "".join(
                        store_sel.xpath('//div[@class="contact_box"]/h4/b/text()')
                    ).strip()

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )

        except:
            pass


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
