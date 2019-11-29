validate.py data.csv --ignore StreetAddressHasNumber --ignore StoreNumberColumnValidator

Both errors came due to record for Zen Massage Dilworth, NC. This franchise had another domain outside of the domain assigned, hence has <MISSING> in both street_adress and store_number field, which was causing the validtor to fail.