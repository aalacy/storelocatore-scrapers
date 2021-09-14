from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger(logger_name="ubs.com")


def fetch_data():
    headers = {
        "authority": "www.ubs.com",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    base_url = "https://www.ubs.com"
    try:
        with SgRequests() as session:
            r = session.get(
                "https://www.ubs.com/locations/_jcr_content.lofisearch.all.en.data",
                headers=headers,
            ).json()
            for i in r["hits"]["hits"]:
                if (
                    "/en/ca" in str(i["fields"]["id"])
                    or "/en/us" in str(i["fields"]["id"])
                    or "/en/pr" in str(i["fields"]["id"])
                ):
                    href = ""
                    location_name = ""
                    street_address = ""
                    city = ""
                    state = ""
                    zipp = ""
                    country_code = ""
                    phone = ""
                    location_type = ""
                    latitude = ""
                    longitude = ""
                    hours_of_operation = ""
                    if "/en/ca" in str(i["fields"]["id"]):
                        street_address = "".join(
                            str(i["fields"]["bu_podAddress"])
                            .replace("['", "")
                            .replace("']", "")
                            .split(",")[:-1]
                        )
                        city = (
                            str(i["fields"]["bu_podAddress"])
                            .replace("['", "")
                            .replace("']", "")
                            .split(",")[-1]
                            .split(" ")[1]
                        )
                        state = (
                            str(i["fields"]["bu_podAddress"])
                            .replace("['", "")
                            .replace("']", "")
                            .split(",")[-1]
                            .split(" ")[2]
                        )
                        zipp = " ".join(
                            str(i["fields"]["bu_podAddress"])
                            .replace("['", "")
                            .replace("']", "")
                            .split(",")[-1]
                            .split(" ")[3:]
                        )
                        latitude = (
                            str(i["fields"]["latitude"])
                            .replace("[", "")
                            .replace("]", "")
                        )
                        longitude = (
                            str(i["fields"]["longitude"])
                            .replace("[", "")
                            .replace("]", "")
                        )
                        location_type = (
                            str(i["fields"]["pod_locationType"])
                            .replace("['", "")
                            .replace("']", "")
                        )
                        location_name = (
                            str(i["fields"]["title"])
                            .replace("['", "")
                            .replace("']", "")
                        )
                        country_code = "CA"
                        link = (
                            "https://www.ubs.com/locations/_jcr_content.location._en_ca_"
                            + str(city.replace(" ", "-").lower())
                            + "_"
                            + str(street_address.replace(" ", "-").lower())
                            + ".en.data"
                        )
                        log.info(link)
                        r1 = session.get(link, headers=headers).json()
                        phone = r1["telephoneNumber"]
                        href = "https://www.ubs.com" + str(r1["poDs"][0]["url"])

                        r4 = session.get(href)
                        soup1 = BeautifulSoup(r4.text, "lxml")
                        hours = soup1.find(
                            "table",
                            {"class": "loFi-poi__location__details__schedule__hours"},
                        )
                        if hours:
                            hours_of_operation = " ".join(
                                list(hours.stripped_strings)[0:]
                            )
                        else:
                            hours_of_operation = "<MISSING>"

                    elif "/en/us" in str(i["fields"]["id"]):
                        street_address = "".join(
                            str(i["fields"]["bu_podAddress"])
                            .replace("['", "")
                            .replace("']", "")
                            .replace('["', "")
                            .split(",")[:-1]
                        )
                        city = (
                            str(i["fields"]["bu_city"])
                            .replace("['", "")
                            .replace("']", "")
                        )
                        state = (
                            str(i["fields"]["bu_podAddress"])
                            .split(",")[-1]
                            .split(" ")[-2]
                        )
                        zipp = (
                            str(i["fields"]["bu_podAddress"])
                            .replace("']", "")
                            .replace('"]', "")
                            .split(",")[-1]
                            .split(" ")[-1]
                        )
                        latitude = (
                            str(i["fields"]["latitude"])
                            .replace("[", "")
                            .replace("]", "")
                        )
                        longitude = (
                            str(i["fields"]["longitude"])
                            .replace("[", "")
                            .replace("]", "")
                        )
                        location_type = (
                            str(i["fields"]["pod_locationType"])
                            .replace("['", "")
                            .replace("']", "")
                        )
                        location_name = (
                            str(i["fields"]["title"])
                            .replace("['", "")
                            .replace("']", "")
                        )
                        country_code = "US"
                        link = (
                            "https://www.ubs.com/locations/_jcr_content.location._en_us_"
                            + str(city.replace(" ", "-").replace(".", "").lower())
                            + "_"
                            + str(
                                street_address.replace(" ", "-")
                                .replace("'", "-")
                                .replace(".", "")
                                .lower()
                            )
                            + ".en.data"
                        )
                        log.info(link)
                        r2 = session.get(link, headers=headers).json()
                        for k in r2["poDs"]:
                            href = "https://www.ubs.com" + str(k["url"])

                            r3 = session.get(href)
                            soup = BeautifulSoup(r3.text, "lxml")
                            phone = "<MISSING>"
                            if soup.find(
                                "dd", {"class": "loFi-details__detail__info__phone"}
                            ):
                                phone = soup.find(
                                    "dd", {"class": "loFi-details__detail__info__phone"}
                                ).text
                            else:
                                phone = "<MISSING>"
                            hours = soup.find(
                                "table",
                                {
                                    "class": "loFi-poi__location__details__schedule__hours"
                                },
                            )
                            if hours:
                                hours_of_operation = " ".join(
                                    list(hours.stripped_strings)[0:]
                                )
                            else:
                                hours_of_operation = "<MISSING>"

                    elif "/en/pr" in str(i["fields"]["id"]):
                        street_address = "".join(
                            str(i["fields"]["bu_podAddress"])
                            .replace("['", "")
                            .replace("']", "")
                            .replace('["', "")
                            .split(",")[:-1]
                        )
                        city = (
                            str(i["fields"]["bu_city"])
                            .replace("['", "")
                            .replace("']", "")
                        )
                        state = (
                            i["fields"]["bu_podAddress"][0]
                            .split(",")[-1]
                            .strip()
                            .split(" ", 1)[-1]
                        )

                        zipp = (
                            i["fields"]["bu_podAddress"][0]
                            .split(",")[-1]
                            .strip()
                            .split(" ", 1)[0]
                        )

                        latitude = (
                            str(i["fields"]["latitude"])
                            .replace("[", "")
                            .replace("]", "")
                        )
                        longitude = (
                            str(i["fields"]["longitude"])
                            .replace("[", "")
                            .replace("]", "")
                        )
                        location_type = (
                            str(i["fields"]["pod_locationType"])
                            .replace("['", "")
                            .replace("']", "")
                        )
                        location_name = (
                            str(i["fields"]["title"])
                            .replace("['", "")
                            .replace("']", "")
                        )
                        country_code = "Puerto Rico"
                        link = (
                            "https://www.ubs.com/locations/_jcr_content.location._en_pr_"
                            + str(city.replace(" ", "-").replace(".", "").lower())
                            + "_"
                            + str(
                                street_address.replace(" ", "-")
                                .replace("'", "-")
                                .replace(".", "")
                                .lower()
                            )
                            + ".en.data"
                        )
                        log.info(link)
                        r2 = session.get(link, headers=headers).json()
                        for k in r2["poDs"]:
                            href = "https://www.ubs.com" + str(k["url"])

                            r3 = session.get(href)
                            soup = BeautifulSoup(r3.text, "lxml")
                            phone = "<MISSING>"
                            if soup.find(
                                "dd", {"class": "loFi-details__detail__info__phone"}
                            ):
                                phone = soup.find(
                                    "dd", {"class": "loFi-details__detail__info__phone"}
                                ).text
                            else:
                                phone = "<MISSING>"
                            hours = soup.find(
                                "table",
                                {
                                    "class": "loFi-poi__location__details__schedule__hours"
                                },
                            )
                            if hours:
                                hours_of_operation = " ".join(
                                    list(hours.stripped_strings)[0:]
                                )
                            else:
                                hours_of_operation = "<MISSING>"
                    yield SgRecord(
                        locator_domain=base_url,
                        page_url=href,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code=country_code,
                        store_number="<MISSING>",
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )
    except:
        pass


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
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
