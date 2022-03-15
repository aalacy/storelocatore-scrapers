import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bankatcnb_bank")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    search_url = "https://www.bankatcnb.bank/_/api/branches/31.9685988/-99.9018131/500"
    stores_req = session.get(search_url, headers=headers).json()
    for loc in stores_req["branches"]:
        title = loc["name"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        hours = loc["description"]
        lat = loc["lat"]
        lng = loc["long"]
        phone = loc["phone"]
        hours = hours.replace(
            '<div><font color="#2f4550"><span style="font-size: 16px;"><b>Lobby</b></span></font></div><div><font color="#2f4550"><span style="font-size: 16px;">',
            "",
        )
        hours = hours.replace("</span></font></div>", "")
        hours = hours.replace(
            '</span></font></div><div><font color="#2f4550"><span style="font-size: 16px;">',
            "",
        )
        hours = hours.replace(
            '<div><font color="#2f4550"><span style="font-size: 16px;">', ""
        )
        hours = hours.replace("\n", "")
        hours = hours.replace("</div>", "")
        hours = hours.replace("<div>", "")
        hours = hours.replace("<b>", " ")
        hours = hours.replace("</b>", " ")
        hours = hours.replace("<h4>Hours</h4><strong>Lobby&nbsp;</strong>", "")
        hours = hours.replace("<br>", " ")
        hours = hours.replace(
            '<h4 style="box-sizing: border-box; -webkit-font-smoothing: antialiased; font-family: Montserrat, Helvetica, Arial, sans-serif; margin-top: 0.625rem; margin-bottom: 0.625rem; line-height: 1.4375rem;"><div style="font-family: &quot;SF Pro Text&quot;, system-ui, -apple-system, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 400;"><font color="#2f4550"><span style="font-size: 16px;"> Lobby <div style="font-family: &quot;SF Pro Text&quot;, system-ui, -apple-system, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 400;"><font color="#2f4550"><span style="font-size: 16px;">',
            " ",
        )
        hours = hours.replace(
            '<div style="font-family: &quot;SF Pro Text&quot;, system-ui, -apple-system, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 400;"><font color="#2f4550"><span style="font-size: 16px;">',
            " ",
        )
        hours = hours.replace(
            '<div style="font-family: &quot;SF Pro Text&quot;, system-ui, -apple-system, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 400;"><font color="#2f4550"><span style="font-size: 16px;"> ',
            " ",
        )
        hours = hours.replace("<strong>", " ")
        hours = hours.replace("&nbsp;", " ")
        hours = hours.split("Drive Thru")[0]
        hours = hours.replace(" Lobby ", "")
        hours = hours.replace("pm", "pm ")
        hours = hours.replace("  ", " ")
        hours = hours.replace("Friday", "Friday ")
        hours = hours.replace(" : ", ": ")
        hours = hours.strip()

        data.append(
            [
                "https://www.bankatcnb.bank/",
                search_url,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                lng,
                hours,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
