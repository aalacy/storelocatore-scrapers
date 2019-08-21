New validator is flagging two locations:

Found 2 addresses with no number. Examples:
    locator_domain location_name  ... hours_of_operation _detectedCC
10  citymarket.com      Shiprock  ...  Su-Sa 06:00-22:00          US
19  citymarket.com       Durango  ...  Su-Sa 06:00-23:00          US

The reason appears to be that the site lists a highway / intersection as the addresses.

It passes a previous test, and the error is from the way they are sending the address on the site, so it has been skipped.