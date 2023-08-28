# template for flask in jinja
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

views = Blueprint(__name__, "views")

ALLOWED_EXTENTIONS = {'csv'}

# Global variable to track the status of the script thread
script_thread_completed = False

def update_events():
    global script_thread_completed
    try:
        result = subprocess.run(['python', 'obs.py'], capture_output=True, text=True)
        print("Output1: ", result.stdout)

    except subprocess.CalledProcessError as e:
        print("Error1: ", e)

def update_areas_belong():
    try:
        result = subprocess.run(['python', 'of_which_area.py'], capture_output=True, text=True)
        # Process the result or save it to a global variable if needed
        print("Output2: ", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error2: ", e)

# run the script to update the new events, and for each one to assign it to the correct area
def run_scripts():
    global script_thread_completed
    update_events()
    update_areas_belong()
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

    # Render a different template as a response
    return render_template("map.html", file_name=files_list) 

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
        # return render_template('map.html', file_name=data_filename)
    return render_template('map.html')

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
    # return render_template('import_show.html',data_var=uploaded_df_html)
    # return render_template('map.html', file_name=data_file_name)

@views.route('/create_geojson')
def createGeojson():
    #upload file path
    data_file_path = session.get('uploaded_data_file_path', None)
    session_file_name = session.get('uploaded_data_file_name', None)

    # read csv
    uploaded_df = pd.read_csv(data_file_path, encoding="unicode_escape")
    uploaded_df_html = uploaded_df.to_json()
    # return render_template('import_show.html',data_var=uploaded_df_html)
    # return render_template('map.html', file_name=session_file_name)
    return redirect(url_for('views.get_geojson_files'))

# to check which events contained in the drawn polygon every time
@views.route('/drawnshape', methods=['POST'])
def drawn_contain():
    # if request.method == "POST":
    #     drawn_polygon = request.json['data']
    #     print(drawn_polygon)
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
    
    # point_coords = (25,37)
    # point = Point(point_coords)
    # events_contained = []
    # # Iterate over the features in the GeoJSON file
    # for feature in data['features']:
    #     polygon = shape(feature['geometry'])
    #     if polygon.contains(point):
    #         event_dict = dict(row)  # Create a dictionary for each row
    #         events_contained.append(event_dict)
    #         print("The point is contained within the polygon:", feature['properties']['name'], " with code: ", feature['properties']['code'])
    #     else:
    #         continue
    # return redirect("/")

# when an area is selected, this route calls the database and fetches the events included in this area
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