import cdflib

def print_cdf_headers(cdf_path):
    # Load the CDF file
    cdf_file = cdflib.CDF(cdf_path)

    # Print global attributes
    print("\n--- Global Attributes ---")
    global_attrs = cdf_file.globalattsget()
    for key, value in global_attrs.items():
        print(f"{key}: {value}")

    # Get CDF info object (use attributes, not keys)
    cdf_info = cdf_file.cdf_info()
    rvars = cdf_info.rVariables if cdf_info.rVariables else []
    zvars = cdf_info.zVariables if cdf_info.zVariables else []
    variables = rvars + zvars

    print("\n--- Variables ---")
    for var in variables:
        print(f"\nVariable: {var}")
        
        # Variable-specific attributes
        try:
            attrs = cdf_file.varattsget(var)
            for attr_key, attr_val in attrs.items():
                print(f"  {attr_key}: {attr_val}")
        except Exception as e:
            print(f"  (No attributes found or error reading: {e})")

if __name__ == "__main__":
    cdf_path = "/Users/clevenger/Projects/paper01/sop23_data/202302/27/SW_EXPT_EFIA_TCT02_20230227T042051_20230227T164506_0302.cdf"
    print_cdf_headers(cdf_path)
