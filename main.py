# This file is reading the url and is creating a file named list.html which includes
# all the info provided by the list view of the gisola software

import requests
from bs4 import BeautifulSoup

# Send a GET request to the website
url = 'http://orfeus.gein.noa.gr/gisola/realtime/all/list.html'
# url = 'http://bbnet.gein.noa.gr/HL/seismicity/mts'
# url = 'https://bbnet.gein.noa.gr/gisola/realtime/'
response = requests.get(url)
print('ok')

# Parse the HTML content of the website using Beautiful Soup
# Accessing the content of the response of the get request
soup = BeautifulSoup(response.content, 'html.parser')
# print("html content: \n", soup.prettify())

# Find the data elements in the HTML of the website
# the u-row-container class of div tag contains every row that exists in the imported gisola software
# 0. title: "National Observatory of Athens Instuture of Geodynamics"
# 1. title: "moment tensor solutions"
# 2. map + select year
# 3. start of rows with moment tensors info



# Find the data elements in the HTML of the website
map_data = soup.find_all('div', {'class': 'u-row-container'})

mts_rows = []

# Find the selected option of the select tag with id='years'
selected_option = soup.select_one('select#years option[selected]')
if selected_option is not None:
    mts_rows.append(selected_option.text)
else:
    mts_rows.append("--no year is selected--")


# Loop through each row element in map_data and find all the p tags within it
for data in map_data:
    p_tags = data.find_all('p')
    # img_tag = data.find_all('img')
    for p in p_tags:
        # Check for the presence of a tags inside each p tag
        a_tags = p.find_all('a')
        if len(a_tags) > 0:
            # If a tags are found, grab the link and append it with the a string to the mts_rows list
            for a in a_tags:
                link = a['href']
                mts_rows.append(str(a.string) + '\n' + ' (' + url.rsplit('/', 2)[0] + '/' + selected_option.text + '/' + link + ')')
        else:
            # If no a tags are found, only append the p string (without the p tags) to the mts_rows list
            mts_rows.append(str(p.string))
    # for i in img_tag:
    #     img_src = i.get('src')
    #     mts_rows.append(str(img_src))


# Save the data to a file in HTML format

with open('templates/list.html', 'w', encoding='utf-8') as f:
    # join all the elements of the array into one list with newlines
    f.write('\n'.join(mts_rows))


