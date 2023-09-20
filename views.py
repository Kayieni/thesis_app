# template for flask in jinja
from datetime import datetime
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from obspy.imaging.beachball import beach
from flask import *
from flask_mysqldb import MySQL
import requests, json, os, csv
from obspy import read_events, Catalog, UTCDateTime
from obspy.core.event import read_events
# from app import app
import pandas as pd
from werkzeug.utils import secure_filename
from distutils.log import debug
from fileinput import filename
from collections import OrderedDict
from shapely.geometry import Polygon, Point, shape
import threading
import subprocess
# from obs import beachball

import warnings
warnings.filterwarnings("ignore")

views = Blueprint(__name__, "views")

ALLOWED_EXTENTIONS = {'csv'}

# Global variable to track the status of the script thread
script_thread_completed = False

def update_events():
    global script_thread_completed
    try:
        result = subprocess.run(['python', 'obs.py'], capture_output=True, text=True)
        # print("Output1: ", result.stdout)

    except subprocess.CalledProcessError as e:
        print("Error1: ", e)

# def update_areas_belong():
#     try:
#         result = subprocess.run(['python', 'of_which_area.py'], capture_output=True, text=True)
#         # Process the result or save it to a global variable if needed
#         print("Output2: ", result.stdout)
#     except subprocess.CalledProcessError as e:
#         print("Error2: ", e)

# run the script to update the new events, and for each one to assign it to the correct area
def run_scripts():
    global script_thread_completed
    update_events()
    # update_areas_belong()
    # Set the global variable to indicate that the script thread is completed
    script_thread_completed = True

@views.route('/')
def execute_update_events():
    global script_thread_completed
     # Only start the script thread if it's not already running
    if not script_thread_completed:
        # Create a new thread to run the other script
        script_thread = threading.Thread(target=run_scripts)
        script_thread.start()
        session.clear()

    # Render the loading template
    return render_template('loading.html')

@views.route('/check_process_status')
def check_process_status():
    global script_thread_completed
    return {"completed": script_thread_completed}

@views.route('/index')
def home():
    files_list = session.get('files_list', None)
    import obs
    # Render a different template as a response
    return render_template("map.html", file_name=files_list) 

# to get all tha available geojson files existing in the server
@views.route('/get_geojson_files')
def get_geojson_files():
    data_dir = 'static/data'
    file_list = []

    # Iterate through files in the data directory
    for filename in os.listdir(data_dir):
        if filename.endswith('.json') or filename.endswith('.geojson'):
            file_list.append(filename)
    
    session['files_list'] = file_list

    print(file_list)
    return redirect(url_for('views.home'))

# not needed anymore: while creating the geojson file. It suppose to be uploaded as geojson
# create the geojson file for the polygons stored in the database (for now only the vamvakaris)
# for the vamvakaris phd areas that are stored in the database
@views.route('/geojson-vamv')
def get_geojson():
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT id,code,area_poly,WKT,name FROM areas''')
    areas = cursor.fetchall()
    # εδω μπορω να προσθεσω ένα WHERE from = "" όπου αυτό θα είναι η απάντηση απο το check box. πχ θα ειναι Βαμβακαρης ή csv που ανέβηκε ή 


    # gjson is the main dictionary
    gjson_dict={}
    gjson_dict["type"]= "FeatureCollection"
    feat_list = []
    
    # Loop through all the cursors, building a list entry which is itself a dictionary
    # Each of these dictionaries has nested within it a type dictionary, which contains a polygon dictionary and a properties dictionary 
    for area in areas:
        cursor.execute("SELECT ST_AsGeoJSON(ST_GeomFromText(%s)) ", (area[3],)) # area 3 is the WKT column of the fetched data
        jsons = cursor.fetchall()[0][0] 
        print(jsons)

        type_dict = {}
        prop_dict = {}
        
        type_dict["type"]= "Feature"
            
        # GEOJSON looks for long,lat so reverse order
        type_dict["geometry"]= json.loads(jsons)  # Load JSON string as a Python object
        
        prop_dict["id"]= area[0]
        prop_dict["name"]= area[4]
        prop_dict["code"] = area[1]
        type_dict["properties"]=prop_dict
        feat_list.append(type_dict)

    gjson_dict["features"] = feat_list
    print(gjson_dict)

    # Serialize JSON for writing to file
    with open("static/data/areas-vamv.json", "w") as outfile:
     json.dump(gjson_dict, outfile, sort_keys = True, indent = 4,
		ensure_ascii=False)

    mysql.connection.commit()

    #Closing the cursor
    cursor.close()

    # Return a response indicating success
    return f'okk!'

# when uploading a file (csv)
@views.route("/csv", methods=['GET','POST'])
def import_csv():
    if request.method == 'POST':
        # upload file flask
        f = request.files.get('file')

        # extracting uploaded file name
        data_filename = secure_filename(f.filename)

        f.save(os.path.join('static/uploads/',data_filename))

        session['uploaded_data_file_path'] = os.path.join('static/uploads/', data_filename)
        session['uploaded_data_file_name'] = data_filename

        return redirect (url_for('views.showData'))
    return render_template('map.html')

# to create csv file data in correct geojson format
@views.route('/show_data')
def showData():
    # upload file path
    data_file_path = session.get('uploaded_data_file_path', None)
    session_file_name = session.get('uploaded_data_file_name', None)
    data_file_name = session_file_name.split('.')[0]
    # read csv
    uploaded_df = pd.read_csv(data_file_path, encoding="unicode_escape")
    print(uploaded_df)
    # coverting to html table
    # uploaded_df_html = uploaded_df.to_html()
    uploaded_df_html = uploaded_df.to_html()

    li = []
    with open(data_file_path, 'r') as csvfile:
        # get the final line

        reader = csv.reader(csvfile, delimiter=',')

        # This skips the first row of the CSV file which is the header
        next(reader)

        coords = []
        first = []
        poly = []
        id_temp = ''
        code = "" 
        name = ""
        pap = ""
        moun = ""
        eq = ""
        mmax = ""

        for row in reader:
            print(row)
            coords = [float(row[4]), float(row[3])]
            
            if row[0] == id_temp:
                # anikei sto idio polygono me to teleftaio id
                poly.append(coords)
            elif row[0] == "":
                # anikei sto idio polygono me to teleftaio id
                poly.append(coords)
            else:
            # paei se neo polygono
                # exiting
                if len(poly) > 0 :
                    # otan bgainei apo to polygono
                    poly.append(first)
                    print(poly)
                    d = OrderedDict()
                    d['type'] = 'Feature'
                    d['geometry'] = {
                        'type': 'Polygon',
                        'coordinates': [poly]
                    }
                    d['properties'] = {
                        'id': id_temp,
                        'code': code,
                        'name': name,
                        'mmax_pap': pap,
                        'mmax_moun': moun,
                        'mmax_eq': eq,
                        'mmax': mmax

                    }
                    li.append(d)

                    poly = []

                # entering
                id_temp = int(row[0])
                code = row[1] 
                name = row[2]
                pap = row[5]
                moun = row[6]
                eq = row[7]
                mmax = row[8]
                first = coords
                poly.append(first)

    d = OrderedDict()
    d['type'] = 'FeatureCollection'
    d['features'] = li
    with open('static/data/' + data_file_name + '.json', 'w') as f:
        f.write(json.dumps(d, sort_keys=False, indent=4))

    return redirect(url_for('views.createGeojson'))

# to create the geojson from the csv uploaded, goes to the get_geojson_files to render the list in frontend modal
@views.route('/create_geojson')
def createGeojson():
    #upload file path
    data_file_path = session.get('uploaded_data_file_path', None)
    session_file_name = session.get('uploaded_data_file_name', None)

    # read csv
    uploaded_df = pd.read_csv(data_file_path, encoding="unicode_escape")
    uploaded_df_html = uploaded_df.to_json()
    return redirect(url_for('views.get_geojson_files'))

# to check which events contained in the drawn polygon every time
@views.route('/drawnshape', methods=['POST'])
def drawn_contain():

    drawn_polygon = request.get_json()
    print(drawn_polygon)
    drawn_polygon = shape(drawn_polygon)
    # Define the event coordinates
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM events''')

    columns = [column[0] for column in cursor.description]  # Get column names


    events_contained = []
    for row in cursor.fetchall():
        print("\n\n", row)
        point = Point(row[2],row[3])
        print(point)
        if drawn_polygon.contains(point):
            event_dict = dict(zip(columns, row))  # Create a dictionary for each row
            events_contained.append(event_dict)

        else:
            continue
    print("This polygon contains the following events:", events_contained)
    
    return jsonify(events_contained)


# when an area is selected, this route calls the database and fetches the events included in this area then, pass to frontend
@views.route("/<areacode>")
def area_selected(areacode):
    code = format(areacode)
    print(code)
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM events WHERE of_area=%s''', (code,))
    
    columns = [column[0] for column in cursor.description]  # Get column names
    
    areas = []
    for row in cursor.fetchall():
        area_dict = dict(zip(columns, row))  # Create a dictionary for each row
        areas.append(area_dict)
    
    return jsonify(areas)

# to fetch all events from db and show their beachballs on the map
@views.route("/allevents", methods=['GET'])
def all_events():
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM events''')
    
    columns = [column[0] for column in cursor.description]  # Get column names
    
    areas = []
    for row in cursor.fetchall():
        area_dict = dict(zip(columns, row))  # Create a dictionary for each row
        areas.append(area_dict)
    
    return jsonify(areas)

# to see in which area each event is contained based in the selected geojson
# given that the file is in the correct form
@views.route("/geojson_selected",methods=['POST'])
def geojson_selected():
    # if request.method == "POST":
    selected_file = request.values.get("file")
    print(selected_file)
    import geojson
    with open("./static/data/"+str(selected_file)) as f:
        json_selected = geojson.load(f)

    from app import mysql
    cursor = mysql.connection.cursor()
    try:
        cursor.execute('''SELECT longitude,latitude,id,of_area FROM events''')
        coordinates = cursor.fetchall()
        
        area_belong = ""
        for row in coordinates:
            if row[3] == "TBA" or row[3] == "None":
                point = Point(row[0],row[1])
                # print(point)
                for feature in json_selected['features']:
                    polygon = shape(feature['geometry'])
                    # print(polygon)
                    if polygon.contains(point):
                        area_belong = feature['properties']['code']
                        print(area_belong)
                        cursor.execute("UPDATE events SET of_area = %s WHERE id = %s", (str(area_belong),row[2]))
                        print("The event ("+ row[2] +") belongs to the :", area_belong)
                        # mysql.connection.commit()
                    # else:
                    #     cursor.execute("UPDATE events SET of_area = %s WHERE id = %s", ("None",row[2]))
                        # continue
        mysql.connection.commit()
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return jsonify(str(selected_file))

# to filter out only the data needed
@views.route("/filter_events",methods=["GET", "POST"])
def filter_events():
        
    if request.method == "POST":

        # filter_values = request.form.get("filter")
        # print(filter_values)
        starttime = request.form.get("starttime")
        endtime = request.form.get("endtime")
        magnitude = request.form.get("magnitude")
        depth = request.form.get("depth")
        rake = request.form.get("rake")

        query= "SELECT * FROM events "


        if starttime and endtime:
            query+="WHERE time between '"+ starttime +"' and '"+ endtime +"'"
        elif starttime:
            query+="WHERE time >= '" + starttime + "'"
        elif endtime:
            query+="WHERE time <= '" + endtime + "'"

        if magnitude:
            if starttime or endtime:
                query+=" AND Mw <= " + magnitude
            else:
                query+="WHERE Mw <= " + magnitude
                
        
        if depth:
            if starttime or endtime or magnitude:
                query+=" AND depth <= " + depth
            else:
                query+="WHERE depth <= " + depth

        if rake:
            if starttime or endtime or magnitude or depth:
                query+=" AND rake <= " + rake
            else:
                query+="WHERE rake <= " + rake

        from app import mysql

        cursor = mysql.connection.cursor()

        cursor.execute(query)
        events = cursor.fetchall()

        print(query)

           
        columns = [column[0] for column in cursor.description]  # Get column names
        
        events_filt = []
        for row in events:
            event_dict = dict(zip(columns, row))  # Create a dictionary for each row
            events_filt.append(event_dict)


        # for row in events:
            
    return jsonify(events_filt)

# to calculate the average MT
@views.route("/averageMT",methods=["GET", "POST"])
def averageMT():

    # function to find the moment(Nm) from gisola
    def gisolaNm(id,year):
        print(id)
        moment= 0
        # Define the URL you want to start with
        base_url = "https://bbnet.gein.noa.gr/gisola/realtime/"+year+"/"+id+"/"  # Replace with your URL

        # Send an HTTP GET request and get the content
        response = requests.get(base_url, verify=False)  # Disable SSL certificate verification

        # Check if the request was successful
        if response.status_code == 200:
            # print(response.status_code)
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the table that contains the links
            table = soup.find('table')

            # Check if a table was found
            if table:
                
                # Iterate through each row in the table
                for row in table.find_all('tr'):
                    # Find the link in the row
                    link = row.find('a')


                    # Check if a link was found
                    if link:
                        # Get the href attribute of the link
                        href = link.get('href')

                        # Join the href with the base URL to create an absolute URL
                        absolute_url = urljoin(base_url, href)
                        # Check if the link is a directory or a file
                        if href.endswith('/'):
                            txtlink1 = urljoin(absolute_url,"output/mt.revise.txt")
                            txtlink2 = urljoin(absolute_url,"output/mt.txt")
                            if(requests.get(txtlink1, verify=False).status_code == 200):
                                # print(txtlink1,"\n")
                                response = requests.get(txtlink1, verify=False).text

                                # Use regular expressions to find the value between ":Moment: " and " Nm"
                                pattern = r"Moment: (\S+ Nm)"

                                # Search for the pattern in the text
                                match = re.search(pattern, response)

                                if match:
                                    moment_value = match.group(1)
                                    moment = float(moment_value.split(" ")[0])
                                    # print(moment,"\n-------------------------------------------------------------")
                                else:
                                    print("Moment value not found in the text.")

                            # You can recursively follow the directory link and repeat the process
                            else:
                                if(requests.get(txtlink2, verify=False).status_code == 200):
                                    # print(txtlink2,"\n")
                                    response = requests.get(txtlink2, verify=False).text

                                    # Use regular expressions to find the value between ":Moment: " and " Nm"
                                    pattern = r"Moment: (\S+ Nm)"

                                    # Search for the pattern in the text
                                    match = re.search(pattern, response)

                                    if match:
                                        moment_value = match.group(1)
                                        moment = float(moment_value.split(" ")[0])
                                        # print(moment,"\n-------------------------------------------------------------")

                                    else:
                                        print("Moment value not found in the text.")


                print(moment,"\n-------------------------------------------------------------")

            else:
                print("No table found in the HTML content.")
                
        else:
            print(f"Failed to retrieve the HTML content. Status code: {response.status_code}")

        if moment!=0:
            return moment
        else:
            return "Error"



    if request.method == "POST":

        print("post ok ")
        data = request.get_json()

        # Print the updated data
        print(data["data"])

        # if filtered hasn't been applied (only in areas selection)
        if "filter" in data:
            print(data["filter"])

            filter_vals = data["filter"]

            # initiate filename 
            filename = str(filter_vals["starttime"])+"_"+str(filter_vals["endtime"])+"_"+str(filter_vals["magnitude"])+"_"+str(filter_vals["depth"])+"_"+str(filter_vals["rake"])
            filepath=os.path.join("./static/beachballs/", (str(filename) +'.png'))
        elif "code" in data:
            filename = str(data["code"])
            filepath=os.path.join("./static/beachballs/", (str(filename) +'.png'))

        from app import mysql


        events_filt = []
        year = 0
        for id in data["data"]:
            # get selected filted events from database
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * from events WHERE id=%s",(id,))
            events = cursor.fetchall()

           
            columns = [column[0] for column in cursor.description]  # Get column names
            
            for row in events:
                event_dict = dict(zip(columns, row))  # Create a dictionary for each row
                events_filt.append(event_dict)
            
            mysql.connection.commit()


        # print(events_filt)


        # Convert elements to float in each sub-list
        # data["data"] = [[float(x) for x in lst] for lst in data["data"]]
        np = []
        tens6 = []

        for eventlist in events_filt:
            # get year of event
            print(eventlist["time"])
            # Assuming eventlist["time"] is a datetime.datetime object
            event_time = eventlist["time"]
            formatted_time = event_time.strftime("%Y-%m-%d %H:%M:%S.%f")
            year = int(formatted_time.split("-")[0])
            print(year)

            # get moment Nm from 
            momentNm = gisolaNm(eventlist["id"],str(year))
            if momentNm == "Error":
                # continue 
                momentNm = 1
            # convert strings to floats and create list of lists for all to calculate average (mean)
            np_temp = [float(x) for x in [eventlist["strike"],eventlist["dip"],eventlist["rake"]]]
            mtlist = eventlist["mtlist"].split("/")
            
            # print(mtlist)
            tens6_temp = [float(x) for x in mtlist]
            # print(tens6_temp)
            tens6_norm = [x / float(momentNm) for x in tens6_temp]
            # print(tens6_norm)
            np.append(np_temp)
            tens6.append(tens6_norm)
            # tens6.append(tens6_temp)

        # Define the header lines
        header_lines = [
            "% West Bohemia mechanisms",
            "%  strike          dip             rake",
        ]

        # Nodal planes (strike, dip, rake) list will be the data for each column
        # Specify the file path where you want to save the content
        stressinv_input_file = "./Stressinverse/Data/Input.dat"

        # Open the file in write mode and write the header lines and data
        with open(stressinv_input_file, "w") as file:
            for line in header_lines:
                file.write(line + "\n")
            
            for row in np:
                file.write("   " + "   ".join(f"{x:.7e}" for x in row) + "\n")

        print(f"File '{stressinv_input_file}' has been created.")

            




        # print(np)
        # print(tens6)

        # for average nodal planes
        df_np = pd.DataFrame(np)
        # for average 6 tensor components
        df_t6 = pd.DataFrame(tens6)
        df_np.mean()
        df_t6.mean()
        mesos_np = list(df_np.mean())
        mesos_t6 = list(df_t6.mean())
        radius = 100
        fig = plt.figure(figsize=(5,5))
        ax = fig.add_subplot(111)
        # Moment Tensor 6 Components
        try:
            nofill=True
            focal1 = beach(mesos_t6, xy=(0.0,0.0), width=2*radius,axes=None,alpha=1, facecolor='red', zorder=1)
            ax.add_collection(focal1)
        except:
            nofill=False

        # Planes
        # focal2 = beach(mesos_np, nofill=nofill, facecolor="red", xy=(0.0,0.0),axes=None,width=2*radius,zorder=2)

        # ax.add_collection(focal2)
        
        ax.autoscale_view(tight=False, scalex=True, scaley=True)
        # # plot the axis
        ax.axison=False
        plt.axis('scaled')
        ax.set_aspect(1)


        # plt.show()

        
        fig.savefig(filepath, transparent=True)





    # return filepath.lstrip('./')
    return redirect(url_for('views.stressinverse'))
    

# to get stress inversion from Stressinverse 
@views.route("/stressinverse",methods=["GET", "POST"])
def stressinverse():
    if request.method == "GET":
        with open("./Stressinverse/Programs_PYTHON/StressInverse.py") as infile:
            print("---exec file now")
            exec(infile.read())
            
    return redirect(url_for('views.str_beachball'))


# to get stress inversion from Stressinverse and create its beachball 
@views.route("/str_beachball",methods=["GET", "POST"])
def str_beachball():
    if request.method == "GET":
        print("in")
        # Initialize empty lists to store the values from each row
        out1 = []
        out2 = []
        data = []
        
        # Open the .dat file for reading
        with open("./Stressinverse/Output/principal_mechanisms.dat", "r") as file:
            # Read the entire content of the file as a single string
            content = file.read()
            
            # Split the content into individual values based on whitespace
            elements = content.split()
            
            # Convert the values to floats and add them to the list
            for element in elements:
                data.append(float(element))

            print(data)

            def beachball(out,color):
                # radius of the ball
                radius = 100

                fig = plt.figure(figsize=(5,5))
                ax = fig.add_subplot(111)

                # Moment Tensor
                try:
                    nofill=True
                    focal = beach(data, xy=(0.0,0.0), width=2*radius,axes=None,alpha=1, facecolor=color, zorder=1)
                    ax.add_collection(focal)
                    ax.autoscale_view(tight=False, scalex=True, scaley=True)

                except:
                    # fall back to dc only with color
                    nofill=False

                # plot the axis
                ax.axison=False
                plt.axis('scaled')
                ax.set_aspect(1)

                fig.savefig("./static/Figures/"+color+".png", transparent=True)
                print("created")
                plt.show()

            beachball(data,"red")
            
            # beachball(out2,"blue")

            
        
    return r'./static/Figures/P_T_axes.png'