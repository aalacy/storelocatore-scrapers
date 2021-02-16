import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("nike_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://nike.brickworksoftware.com/api/v3/stores.json"
    r = session.get(url, headers=headers, timeout=90)
    website = "nike.com"
    typ = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"slug":"' in line:
            items = line.split('"slug":"')
            for item in items:
                if '"name":"' in item:
                    name = item.split('"name":"')[1].split('"')[0]
                    loc = "https://www.nike.com/us/retail/s/" + item.split('"')[0]
                    add = item.split('"address_1":"')[1].split('"')[0]
                    try:
                        add = add + " " + item.split('"address_2":"')[1].split('"')[0]
                    except:
                        pass
                    city = item.split('"city":"')[1].split('"')[0]
                    try:
                        state = item.split('"state":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    try:
                        country = item.split('"country_code":"')[1].split('"')[0]
                    except:
                        country = "<MISSING>"
                    try:
                        zc = item.split('"postal_code":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    try:
                        store = item.split('"number":"')[1].split('"')[0]
                    except:
                        store = "<MISSING>"
                    try:
                        phone = item.split('"phone_number":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    try:
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    try:
                        days = (
                            item.split('"regular_hours":[{')[1]
                            .split("]")[0]
                            .split('"start_time":"')
                        )
                        hours = ""
                        for day in days:
                            if '"end_time":"' in day:
                                if '"closed":true' in day:
                                    hrs = (
                                        day.split('"display_day":"')[1].split('"')[0]
                                        + ": Closed"
                                    )
                                else:
                                    hrs = (
                                        day.split('"display_day":"')[1].split('"')[0]
                                        + ": "
                                        + day.split('"display_start_time":"')[1].split(
                                            '"'
                                        )[0]
                                        + "-"
                                        + day.split('"display_end_time":"')[1].split(
                                            '"'
                                        )[0]
                                    )
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                    except:
                        hours = "<MISSING>"
                    if country == "CA" or country == "US" or country == "GB":
                        if country == "GB":
                            state = "<MISSING>"
                        if (
                            "Outlets " in add
                            and "Napa Premium" not in add
                            and "80 Premium" not in add
                            and "1 Premium Outlets" not in add
                            and "One Premium Outlets" not in add
                            and "5701" not in add
                            and "100 Premium" not in add
                        ):
                            add = add.split("Outlets ")[1]
                        if "- Pittsburgh " in add:
                            add = add.split("- Pittsburgh ")[1]
                        if "Outles " in add:
                            add = add.split("Outles ")[1]
                        if "- Lancaster " in add:
                            add = add.split("- Lancaster ")[1]
                        if (
                            "Outlet Center " in add
                            and "1025 Outlet" not in add
                            and "199 Outlet" not in add
                        ):
                            add = add.split("Outlet Center ")[1]
                        if "Rehoboth Beach " in add:
                            add = add.split("Rehoboth Beach ")[1]
                        if "Sugarloaf Mills " in add:
                            add = add.split("Sugarloaf Mills ")[1]
                        if "- Williamsburg " in add:
                            add = add.split("- Williamsburg ")[1]
                        if "Pigeon Forge " in add:
                            add = add.split("Pigeon Forge ")[1]
                        add = add.replace("Seaside Factory Stores ", "")
                        add = add.replace("Arundel Mills 7000", "7000")
                        add = add.replace("- Howell ", "")
                        add = add.replace("- Smithfield ", "")
                        add = add.replace("at Silverthorne ", "")
                        add = add.replace("Portland International Airport ", "")
                        if (
                            "Factory Stores " in add
                            and "4642" not in add
                            and "615" not in add
                        ):
                            add = add.split("Factory Stores ")[1]
                        add = add.replace("- South ", "")
                        add = add.replace("- Park City ", "")
                        add = add.replace("The Outlet Shoppes at Oshkosh ", "")
                        add = add.replace("at Castle Rock ", "")
                        add = add.replace("Settlers Green Outlet Village ", "")
                        add = add.replace("- Myrtle Beach ", "")
                        add = add.replace("Silver Sands Factory Store ", "")
                        add = add.replace("The Forum Shops at Caesars ", "")
                        add = add.replace("- Hilton Head ", "")
                        add = add.replace("- Jeffersonville ", "")
                        add = add.replace("Shoppes at the Parkway - Celebration ", "")
                        add = add.replace("- Charleston ", "")
                        add = add.replace("- Sevierville ", "")
                        add = add.replace("Ontario Mills ", "")
                        add = add.replace("- North ", "")
                        add = add.replace("The Great Mall ", "")
                        add = add.replace("Legends at Village West ", "")
                        add = add.replace("Louisiana Boardwalk ", "")
                        add = add.replace("Arizona Mills Mall ", "")
                        add = add.replace("Grapevine Mills 3", "3")
                        add = add.replace("Gurnee Mills 6", "6")
                        add = add.replace("- The Walk ", "")
                        add = add.replace("Wisconsin Dells Outlet Center ", "")
                        add = add.replace("- Locust Grove ", "")
                        add = add.replace("- Fort Myers ", "")
                        add = add.replace("at Loveland ", "")
                        add = add.replace("South Plaza Shopping Center ", "")
                        add = add.replace("The Outlet Shoppes at El Paso ", "")
                        add = add.replace("- Gonzales ", "")
                        add = add.replace("- Branson", "")
                        add = add.replace("of Niagara Falls ", "")
                        add = add.replace("- Deer Park ", "")
                        add = add.replace("Opry Mills Mall ", "")
                        add = add.replace("Potomac Mills 2700", "2700")
                        add = add.replace("Concord Mills 8", "8")
                        add = add.replace("The Shops at Terrell ", "")
                        add = add.replace("Dolphin Mall ", "")
                        add = add.replace("at Orange ", "")
                        add = add.replace("Omaha - Nebraska Crossings ", "")
                        add = add.replace("- Grand Rapids ", "")
                        add = add.replace("Plaza San Clemente ", "")
                        add = add.replace("Lenox Square ", "")
                        add = add.replace("- International Drive ", "")
                        add = add.replace("Village at Meridian ", "")
                        add = add.replace("West End Shopping Center Lubbock ", "")
                        add = add.replace("of Chicago - Rosemont ", "")
                        add = add.replace("at Tejon Pkwy. ", "")
                        add = add.replace("Nike Factory Store ", "")
                        add = add.replace("- National Harbor ", "")
                        add = add.replace("of Mississippi ", "")
                        add = add.replace("Auburn - Outlet Collection of Seattle ", "")
                        add = add.replace("at Barstow ", "")
                        add = add.replace("Sky View Center ", "")
                        add = add.replace("The Shoppes at Broad ", "")
                        add = add.replace("Outlet Mall of Georgia ", "")
                        add = add.replace("at Rainbow Harbor ", "")
                        add = add.replace("- Foxwoods ", "")
                        add = add.replace("The Outlet Shoppes of the Bluegrass ", "")
                        add = add.replace("Twin Cities ", "")
                        add = add.replace("of Little Rock ", "")
                        add = add.replace("South Coast Plaza ", "")
                        add = add.replace("Fashion Valley Mall ", "")
                        add = add.replace("at Traverse Mountain ", "")
                        add = add.replace("- Galveston/Houston ", "")
                        add = add.replace("One Colorado ", "")
                        add = add.replace("at Legends ", "")
                        add = add.replace("Cool Springs Pointe ", "")
                        add = add.replace("Great Lakes Crossing ", "")
                        add = add.replace("Jordan Landing ", "")
                        add = add.replace("The Outlet Shoppes at Atlanta ", "")
                        add = add.replace("The Outlet Shoppes at Burlington ", "")
                        add = add.replace("at Bergen Town Center ", "")
                        add = add.replace("NorthPark Center ", "")
                        add = add.replace("Grand Prairie 29", "29")
                        add = add.replace("The Sands Shopping Center - Oceanside ", "")
                        add = add.replace("Mall of America ", "")
                        add = add.replace("Kress Building ", "")
                        add = add.replace("- Mebane ", "")
                        add = add.replace("Jordan Creek Town Center ", "")
                        add = add.replace("Silverado Ranch Plaza ", "")
                        add = add.replace("- Westgate ", "")
                        add = add.replace("at Columbus ", "")
                        add = add.replace("The Shops at Pembroke Gardens ", "")
                        add = add.replace("Barracks Road Shopping Center ", "")
                        add = add.replace("- Daytona Beach ", "")
                        add = add.replace("at Montehiedra ", "")
                        add = add.replace("Livingston designer outlet ", "")
                        add = add.replace("Thurrock Shopping Park ", "")
                        add = add.replace("Parkgate Shopping Park ", "")
                        add = add.replace("Cheshire Oaks Designer Outlet ", "")
                        add = add.replace("Braintree Outlet Village ", "")
                        add = add.replace("East Midlands Designer Outlet ", "")
                        add = add.replace("One Stop Shopping Park ", "")
                        add = add.replace("East Midlands Designer Outlet ", "")
                        add = add.replace("Strathkelvin Retail Park ", "")
                        add = add.replace("Swindon Designer Outlet Village ", "")
                        add = add.replace("York Designer Outlet ", "")
                        add = add.replace("Manchester Fort Retail Park ", "")
                        add = add.replace("Kingsmere Retail Park ", "")
                        add = add.replace("Scarborough Town Centre ", "")
                        add = add.replace("Winter Garden Village ", "")
                        add = add.replace("Square One Shopping Centre ", "")
                        add = add.replace("Celebration Pointe 4", "4")
                        add = add.replace("Marketplace at Factoria ", "")
                        add = add.replace("- Fort Worth ", "")
                        add = add.replace("The Promenade at Westlake ", "")
                        add = add.replace("of Des Moines ", "")
                        add = add.replace("Valencia Marketplace ", "")
                        add = add.replace("Country Club Plaza ", "")
                        add = add.replace("Rolling Hills Plaza ", "")
                        add = add.replace("Mountain Grove at Citrus Plaza ", "")
                        add = add.replace("Resorts World Birmingham ", "")
                        add = add.replace("Arnison Retail Park ", "")
                        add = add.replace("The Outlet Shoppes at Laredo ", "")
                        add = add.replace("Elliott's Field Retail Park ", "")
                        add = add.replace("The Eaton Center ", "")
                        add = add.replace("Burloak Centre ", "")
                        add = add.replace("Gretna Gateway Outlet Village ", "")
                        add = add.replace("London Designer Outlet ", "")
                        add = add.replace("Kingsgate Retail Park ", "")
                        add = add.replace(
                            "Affinity Sterling Mills Outlet Shopping ", ""
                        )
                        add = add.replace("Manchester Fort Retail Park ", "")
                        add = add.replace("York Designer Outlet ", "")
                        add = add.replace("Swindon Designer Outlet Village ", "")
                        add = add.replace("One Stop Shopping Park ", "")
                        if state != "FR":
                            if "Nike Factory Store - Merrimack" in name:
                                add = "80 Premium Outlets Blvd."
                            yield [
                                website,
                                loc,
                                name,
                                add,
                                city,
                                state,
                                zc,
                                country,
                                store,
                                phone,
                                typ,
                                lat,
                                lng,
                                hours,
                            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
