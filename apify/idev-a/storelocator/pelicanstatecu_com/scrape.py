from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from urllib.parse import urljoin
from lxml import html

locator_domain = "https://www.pelicanstatecu.com/"
base_url = "https://www.pelicanstatecu.com/about-us/locations-hours.html"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


crawled = []


def get_first(lst):
    lst = lst or []
    return lst[0] if len(lst) > 0 else ""


def get_id_from_link(link):
    link = link.split("id=")[1]
    link = link[: link.find("&")]
    return link


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        soup = html.fromstring(res.text.replace("\xa0", " "))
        for href in soup.xpath('//ul[@class="locList"]/li[@class="loc"]'):
            name = href.xpath("./@data-title")[0]
            if name not in crawled:
                crawled.append(name)
                url = get_first(href.xpath('.//a[@class="seeDetails"]/@href'))
                if not url:
                    continue
                page_url = urljoin(base_url, url)
                hours_of_operation = ""
                t1 = href.xpath('.//div[@class="lobbyHours"]/h5')
                if t1:
                    for t in t1:
                        hours_of_operation += t.xpath("./text()")[0]
                        hours_of_operation += ": "
                        hours_of_operation += ": ".join(
                            t.xpath("./following-sibling::div[1]/span/text()")
                        )
                        hours_of_operation += ";"
                latitude = get_first(href.xpath("./@data-latitude"))
                longitude = get_first(href.xpath("./@data-longitude"))
                street_address = " ".join(
                    href.xpath("./@data-address1 | ./@data-address2")
                )
                city = get_first(href.xpath("./@data-city"))
                state = get_first(href.xpath("./@data-state"))
                zip_postal = get_first(href.xpath("./@data-zip"))
                phone = get_first(
                    href.xpath(
                        './/div[@class="contact"]//div[span="Phone"]/span[@class="value"]/text()'
                    )
                )
                store_number = ""
                try:
                    store_number = get_id_from_link(page_url)
                except:
                    pass

                yield SgRecord(
                    page_url=page_url,
                    store_number=store_number,
                    location_name=name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code="us",
                    latitude=latitude,
                    longitude=longitude,
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation.replace("Lobby Hours:", ""),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
