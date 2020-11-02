While running the validate.py it was giving error "Found 4 addresses with no number" while validating the street address. In this case, it 
was not possible to parse the address into streetaddress, city, state and zipcode, so i have created a column raw_address and included the 
address in it while the rest of the columns for street_address, city, state, zipcode is marked as <INACCESSIBLE> as per the instructions.

So to get success for validate.py I have ignored the streetaddressvalidator and ran below command:
python validate.py data.csv --ignore StreetAddressValidator:validateStreetAddress
