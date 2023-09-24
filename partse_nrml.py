# Program to convert an xml
# file to GeoJSON file
import json
import xmltodict

# Open the input XML file and read data in the form of a Python dictionary using xmltodict module
with open("asm_ver12e_winGT_fs017_hi_abgrs_maxmag_low.xml") as xml_file:
    data_dict = xmltodict.parse(xml_file.read())

    # Manipulate the data if needed
    area_sources = data_dict["nrml"]["sourceModel"]["areaSource"]

    # Filter the objects based on "@id" that includes "GRAS"
    # filtered_sources = [source for source in area_sources if "GRAS" in source["@id"]]

    # Create a new dictionary with the filtered data
    filtered_area_source_data = {"Sources": area_sources}

    # Initialize the GeoJSON structure
    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    # Iterate through the "Sources" array and convert each object to a GeoJSON feature
    counter = 0
    for source in filtered_area_source_data["Sources"]:
        counter+=1
        # Extract relevant information from the source object
        feature = {
            "type": "Feature",
            "properties": {
                "id": counter,
                "code": str(source["@id"])[-7:],
                "name": source["@name"],
                "tectonicRegion": source["@tectonicRegion"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[]]  # Initialize an empty list for coordinates
            }
        }

        # Extract and add coordinates to the "coordinates" property
        pos_list = source["areaGeometry"]["gml:Polygon"]["gml:exterior"]["gml:LinearRing"]["gml:posList"]
        coordinates = list(map(float, pos_list.split()))
        coordinates = [coordinates[i:i + 2] for i in range(0, len(coordinates), 2)]  # Split coordinates into pairs
        feature["geometry"]["coordinates"][0] = coordinates  # Set the coordinates list

        # Add the feature to the GeoJSON features list
        geojson_data["features"].append(feature)

    # Convert the GeoJSON data to a JSON string
    geojson_string = json.dumps(geojson_data, indent=4)

    # Write the GeoJSON data to the output file
    with open("output.json", "w") as geojson_file:
        geojson_file.write(geojson_string)
