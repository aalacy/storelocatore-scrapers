# Duplicate lat/lng pairs reported by validator

As of version 0.0.19 of sgvalidator, this scraper is getting flagged by the duplication validator for having records with lat/lng values pointing to multiple addresses. However, the addresses only differ in the suite numbers.

```
AssertionError: [31mFound 6 <lat, lng> pair(s) that belong to multiple addresses. Examples:
             latitude            longitude                                     street_address  num_addrs
4          44.6408697  -63.586628399999995  {5991 Spring Garden Road, Suite 100, 5991 Spri...          2
7          44.6496567  -63.575649399999975  {5201 Duke Street, 5201 Duke St., Level A, Sui...          2
10  44.65669399999999   -63.52954920000002        {240 Baker Dr., Suite 201, 240 Baker Drive}          2
12         44.6630063   -63.65766050000002             {287 Lacewood Drive, 287 Lacewood Dr.}          2
19         44.6862873   -63.87504819999998  {5110 St. Margaret's Bay Road, Suite 202, 5110...          2
50  46.12225129999999   -64.77123879999999  {565 Elmwood Drive, Suite 203, 565 Elmwood Drive}          2
```

```
{
  "locator_domain": "lawtons.ca",
  "location_name": "Lawtons Drugs Spring Garden Road",
  "street_address": "5991 Spring Garden Road, Suite 100",
  "city": "Halifax",
  "state": "NS",
  "zip": "B3H 1Y6",
  "country_code": "<MISSING>",
  "store_number": "1063",
  "phone": "(902) 423-9430",
  "location_type": "Bus Tickets, Home HealthCare, Pharmacy, Post Office, Walk-In Clinic",
  "latitude": "44.6408697",
  "longitude": "-63.586628399999995",
  "hours_of_operation": "\nMonday - Friday: 8:30 am - 9:00 pm\nSaturday: 9:00 am - 5:00 pm\nSunday: 11:00 am - 5:00 pm"
}
```

```
{
  "locator_domain": "lawtons.ca",
  "location_name": "The Family Focus Medical Clinic",
  "street_address": "5991 Spring Garden Road, Suite 201",
  "city": "Halifax",
  "state": "NS",
  "zip": "<MISSING>",
  "country_code": "<MISSING>",
  "store_number": "1124",
  "phone": "902-420-2038",
  "location_type": "Walk-In Clinic",
  "latitude": "44.6408697",
  "longitude": "-63.586628399999995",
  "hours_of_operation": "Monday - Friday: 8:30am - 9pm\nWeekends & Holidays: 11am - 5pm"
}
```
