import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import mysql.connector as mysql
from mysql.connector import Error
import matplotlib.pyplot as plt
from obspy.imaging.beachball import beach

import warnings
warnings.filterwarnings("ignore")

# moment value
moment= 0

try:
    # connect database
    db = mysql.connect(
        host='localhost',
        user='root',
        database = 'thesis',
        passwd='',
    )

    if db.is_connected():
        cursor = db.cursor(buffered=True) #like a little robot that will do commands for you
        # for all the events after the last which exists in the database
        cursor.execute("SELECT id FROM events WHERE time >= '2023-08-21'")


        for event in cursor.fetchall():
            print("\n",event[0],"\n")
            id = event[0]

            # Define the URL you want to start with
            base_url = "https://bbnet.gein.noa.gr/gisola/realtime/2023/"+id+"/"  # Replace with your URL

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
                                    print(txtlink1,"\n")
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
                                        print(txtlink2,"\n")
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


except Error as e:
    print("Error while connecting to MySQL. \n", e)

db.close()


# Mrr:	1.279e+14		Mtt:	3.460e+15		Mpp:	-3.588e+15

# Mrt:	6.620e+15		Mrp:	3.464e+15		Mtp:	6.235e+15

# list = [-156631000000000.0, -1326852000000000.0, 1483483000000000.0, -90348000000000.0, -514661000000000.0, 55180000000000.0]
# norm = [-0.1040046480743692, -0.8810438247011952, 0.9850484727755644, -0.05999203187250996, -0.3417403718459495, 0.03664010624169987]

moment1 = 1.035e+16
data1 = [1.279e+14,3.460e+15,-3.588e+15,6.620e+15,3.464e+15,6.235e+15]
result1 = [x / moment1 for x in data1]
print(data1)
print(result1)
# moment1 = 1.035e+16
# data1 = [1.279e+14,3.460e+15,-3.588e+15,6.620e+15,3.464e+15,6.235e+15]
# result1 = [x / moment for x in data1]

# df = pd.DataFrame(result)
# print(df)
# df.mean()
# mesosmt = list(df.mean())
radius = 100
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(111)
nofill=True
focal1 = beach(result1, xy=(0.0,0.0), width=2*radius,axes=None,alpha=1, facecolor='r', zorder=1)
ax.add_collection(focal1)
ax.autoscale_view(tight=False, scalex=True, scaley=True)
# plot the axis
ax.axison=False
plt.axis('scaled')
ax.set_aspect(1)

# fig.savefig(filepath, transparent=True)
plt.show()