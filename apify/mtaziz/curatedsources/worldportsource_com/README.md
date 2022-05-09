# Background information
There are around 5746 ports across the world. So far, no API found and to parse the data, we had no choice except using manual method like `lxml`. 

This ( `http://www.worldportsource.com/countries.php` )  lists all the countries and port counts. 
The crawler, at first scrapes the country-based map URL such as for Albania, `http://www.worldportsource.com/ports/index/ALB.php`. 
`http://www.worldportsource.com/ports/index/ALB.php` if changed to `http://www.worldportsource.com/ports/ALB.php`, that returns the ports and harbors located in Albania on the map. From the page source, the crawler extracts the URL for each port and save it in a list. This is done for all other countries and that yields all the port-based page URLs. The crawler goes to each page_url and extract desired data. 



# `street_address`

Please note that if `street_address` is found to have `<MISSING>`, it is replaced with `location_name`. 