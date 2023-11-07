##### `Car_Pool.py`
##### Car Pool
##### Open-Source, hosted on https://github.com/DrBenjamin/Car_Pool
##### Please reach out to ben@benbox.org for any questions
#### Loading needed Python libraries
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
import sys
sys.path.insert(1, "files/")
from functions import header
from functions import check_password
from functions import landing_page
from functions import read_sheet
from functions import write_sheet


## Streamlit initial setup
try:
    desc_file = open('DESCRIPTION', 'r')
    lines = desc_file.readlines()
    print(lines[3])
    st.set_page_config(
        page_title = "Car Pool Demo",
        page_icon = st.secrets["custom"]["sidebar_image"],
        layout = "centered",
        initial_sidebar_state = "expanded",
        menu_items = {
            'Get Help': 'https://www.benbox.org',
            'Report a bug': 'https://github.com/DrBenjamin/Car_Pool/issues',
            'About': '**Car Pool Demo** (' + lines[3] + ')\n\n The Car Pooling Demo. See the full version on Github (https://github.com/DrBenjamin/Car_Pool/).'
        }
    )
except Exception as e:
    print(e)


## Initialization of session states
if ('logout' not in st.session_state):
    st.session_state['logout'] = False
if ('header' not in st.session_state):
    st.session_state['header'] = True
if ('index' not in st.session_state):
    st.session_state['index'] = 1
if ('booking' not in st.session_state):
    st.session_state['booking'] = []




#### Two versions of the page -> Landing page vs. Car Pool
### Logged in state (Car Fleet Management System)
if check_password():
    # Header
    header(title = 'Car Pool', data_desc = 'car pooling', expanded = st.session_state['header'])
    st.title('Car Pool')
    st.write('The Car Pool App gives staff the opportunity to find, propose and book business trips to share resources such as a vehicle, fuel and drivers to reduce costs, eco-system impact and to increase the opportunities to reach a destination. Now feel free to:')
    st.write('- enter a trip (🚗 **Driving**), if you can offer at least one seat;')
    st.write('- or search for a trip (👍🏿 **Hitchhiking**) for your purpose;')
    st.write('- or book a matching trip (📅 **Booking**) you found.')

    # Get trips data, (NO CACHING!)
    databank = read_sheet()
    databank["ID"] = databank.index + 1
    databank = databank.set_index('ID')

    # Get cities data (cached)
    databank_cities = read_sheet(sheet = 2)
    databank_cities["ID"] = databank_cities.index + 1
    databank_cities = databank_cities.set_index('ID')
    
    # Get distances data (cached)
    databank_distances = read_sheet(sheet = 3)
    databank_distances["ID"] = databank_distances.index + 1
    databank_distances = databank_distances.set_index('ID')

    # Get routes data (cached)
    databank_routes = read_sheet(sheet = 4)
    databank_routes["ID"] = databank_routes.index + 1
    databank_routes = databank_routes.set_index('ID')

    # Get points (gamification)
    databank_points = read_sheet(sheet = 1)
    databank_points["ID"] = databank_points.index + 1
    databank_points = databank_points.set_index('ID')
    st.sidebar.subheader('Highscore 🏆')
    databank_points = databank_points.sort_values('POINTS', ascending = False)
    st.sidebar.dataframe(databank_points[['NAME', 'POINTS']], column_config = {
        "NAME": st.column_config.TextColumn("Name"),
        "POINTS": st.column_config.NumberColumn("Points")}, hide_index = True)
    
    # Menu
    font_css = """<style>button[data-baseweb = "tab"] > div[data-testid="stMarkdownContainer"] > p {font-size: 18px;}</style>"""
    st.write(font_css, unsafe_allow_html = True)
    tab1, tab2, tab3 = st.tabs(["🚗 **Driving** :gray[(*enter a trip*)]", "👍🏿 **Hitchhiking** :gray[(*see future trips*)]", "📅 **Booking** :gray[(*book a trip*)]"])

    # tab `Driving`
    with tab1:
        with st.form("Driving", clear_on_submit = True):
            st.write("")
            st.title('Driving')
            st.subheader('Enter a trip')
            st.write('Please enter all data precisely, for a trip, you can offer at least one seat in your car.')
            name = st.text_input('Name', key = "name_driving")
            sex = st.selectbox('Sex', options = ['female', 'male'], index = 0, key = "sex_driving")
            if sex == 'female':
                female = 1
            else:
                female = 0
            phone = st.text_input('Phone', key = "phone_driving")
            mail = st.text_input('Mail', key = "mail_driving")
            dep_list = np.array([])
            # sorting city list
            dep_list = np.insert(databank_cities['CITY'].values, 0, 'All departures')
            dep_list = np.sort(dep_list)
            dep = st.selectbox('Departure', options = dep_list, index = 11, key = "dep_driving")
            des_list = np.array([])
            des_list = np.insert(databank_cities['CITY'].values, 0, 'All destinations')
            des_list = np.sort(des_list)
            des = st.selectbox('Destination', options = des_list, index = 2, key = "des_driving")
            date_t = st.date_input('Date', key = "date_driving")
            # Add time to date
            date_t = datetime.combine(date_t, time(0, 0)) # Convert date to datetime
            time_start = st.time_input('Start time', value = time(11, 30), key = "stime_driving")
            time_start = datetime.combine(date_t, time_start) # Convert time to datetime
            time_end = st.time_input('Approx. arrival time', value = time(12, 45), key = "etime_driving")
            time_end = datetime.combine(date_t, time_end) # Convert time to datetime
            seats = st.number_input('Seats', min_value = 1, max_value = 6, value = 1, key = "num_driving")
            guests = st.selectbox('Guests', options = ['all sexes', 'only female!'], index = 0, key = "guest_driving")
            if female == 1:
                if guests == 'only female!':
                    female_guests = 1
                else:
                    female_guests = 0
            else:
                female_guests = 0

            # Submit button
            submitted = st.form_submit_button('Submit', help = "Write your trip to the database.")
            if submitted:
                try:
                    # Updating `trips` table
                    data = read_sheet()
                    data['PHONE'] = "'" + data['PHONE'].astype(str)
                    data = np.array(data)
                    newrow = np.array([name, "'" + phone, mail, dep, des, str(date_t), str(time_start), str(time_end), seats, 0, female, female_guests])
                    data = np.vstack((data, newrow))
                    data = data.tolist()
                    write_sheet(data = data, sheet = 0)
                    st.session_state['google'] = True
                    print('Updated Google Sheet, sheet `trips`')

                    # Updating `gamification` table
                    if name in databank_points['NAME'].values:
                        data = read_sheet(sheet = 1)
                        data.loc[data['NAME'] == name, 'POINTS'] = int(databank_points.loc[databank_points['NAME'] == name]['POINTS'].values[0]) + 10
                        data = np.array(data)
                        data = data.tolist()
                        write_sheet(data = data, sheet = 1)
                        print('Updated Google Sheet, sheet `gamification`')
                    else:
                        data = read_sheet(sheet = 1)
                        data = np.array(data)
                        newrow = np.array([name, 10])
                        data = np.vstack((data, newrow))
                        data = data.tolist()
                        write_sheet(data = data, sheet = 1)
                        print('Updated Google Sheet, sheet `gamification`)')
                except Exception as e:
                    print('No Update to Google Sheet', e)

    # tab `Hitchhiking`
    with tab2:
        with st.expander('', expanded = True):
            st.title('Hitchhiking')
            st.subheader('Look for trips')
            st.write('Choose the range of dates in between you want to travel to find a matching trip (*booking will be done by these results*).')

            # Set range of dates
            range_date = []
            date_start = st.date_input('Range start', key = "rstart")
            range_date.append(date_start)
            date_end = st.date_input('Range end', value = date.today() + timedelta(days = 60), key = "rend")
            range_date.append(date_end)
            st.info('Choose the same date twice if you are looking just for a single day.', icon = "ℹ️")
            
            # Set the Departure and Destination
            st.write('Choose the departure and destination of your travel.')

            # Add option all at the start of the list
            dep_list = np.array([])
            dep_list = np.insert(databank_cities['CITY'].values, 0, 'All departures')
            dep_list = np.sort(des_list)
            dep = st.selectbox('Departure', options = dep_list, index = 11, key = "dep_hitchhiking")
            des_list = np.array([])
            des_list = np.insert(databank_cities['CITY'].values, 2, 'All destinations')
            des_list = np.sort(des_list)
            des = st.selectbox('Destination', options = des_list, index = 2, key = "des_hitchhiking")

            # Distance calculation
            if dep != 'All departures' and des != 'All destinations':
                distance = databank_distances.loc[databank_distances['CITY'] == dep][des].values[0]
                st.write('Distance of this trip is about ', str(distance), 'km.')

            # Female only trips
            fem = st.checkbox('Female driver?', key = "fem_hitchhiking")
            if fem:
                fem_g = st.checkbox('Only female guests?', key = "fem_g_hitchhiking")
            else:
                fem_g = False


            ## Search for matching trips in the future
            actual_data = []
            # Get directions on the route in the right order
            try:
                direction = databank_routes.loc[databank_routes['CITY'] == dep][des].values[0].replace(" ", "").split(',')
            except:
                direction = []
                direction.append("")
            # Add `Departure` to direction
            if direction[0] == "":
                direction[0] = dep
            else:
                direction.insert(0, dep)
            # Add `Destination` to direction 
            direction.append(des)
            index_dep = direction.index(dep)
            index_des = direction.index(des)
            direction_direction = index_dep - index_des
            # Find the matching trips
            for idx, row in databank.iterrows():
                # Get cities on the route in the right order
                cities = databank_routes.loc[databank_routes['CITY'] == row['DEPARTURE']][row['DESTINATION']].values[0].replace(" ", "").split(',')
                # Add `Departure` to cities
                if cities[0] == "":
                    cities[0] = row['DEPARTURE']
                else:
                    cities.insert(0, row['DEPARTURE'])
                # Add `Destination` to cities
                cities.append(row['DESTINATION'])
                # Calculate order
                try:
                    index1 = cities.index(dep)
                    index2 = cities.index(des)
                    direction_cities = index1 - index2
                except:
                    direction_cities = 0
                # Add trips to the list if matching
                row['DATE'] = datetime.strptime(row['DATE'], '%Y-%m-%d %H:%M:%S')
                if (datetime.date(row['DATE']) >= range_date[0] and datetime.date(row['DATE']) <= range_date[1]) and int(row['SEATS'] - row['REQUEST']) >= 1:
                    if dep == 'All departures' or dep in cities:
                        if des == 'All destinations' or des in cities:
                            # Check if the array `cities` is in the same direction of array `direction`
                            if (direction_cities < 0 and direction_direction < 0) or (direction_cities > 0 and direction_direction > 0) or des == 'All destinations':
                                if len(dep) > 0:    
                                    if fem:
                                        if row['FEMALE'] == 1:
                                            if fem_g:
                                                if row['FEMALE_GUESTS'] == 1:
                                                    actual_data.append(row)
                                            else:
                                                actual_data.append(row)
                                    else:
                                        actual_data.append(row)

            # Show data
            try:
                actual_data = pd.DataFrame(actual_data)
                st.subheader('List view of trips')
                st.write('For your selection, there are ' + str(len(actual_data.index)) + ' trips in the database.')
                try:
                    if len(actual_data) > 0:
                        if len(actual_data) == 1:
                            st.info('Go to **Booking** page to book this trip!', icon = "‼")
                        else:
                            st.info('Go to **Booking** page to book one of these trips!', icon = "‼")
                except:
                    print('No data.')
                st.dataframe(actual_data[['DEPARTURE', 'DESTINATION', 'DATE', 'START', 'ARRIVAL', 'SEATS', 'REQUEST']], column_config = {
                    "DEPARTURE": st.column_config.TextColumn("From (Departure)"),
                    "DESTINATION": st.column_config.TextColumn("To (Destination)"),
                    "DATE": st.column_config.DatetimeColumn("Date", format = "D MMM YYYY"),
                    "START": st.column_config.DatetimeColumn("Departure", format = "HH:mm"),
                    "ARRIVAL": st.column_config.DatetimeColumn("Arrival", format = "HH:mm"),
                    "SEATS": st.column_config.NumberColumn("Seats"),
                    "REQUEST": st.column_config.NumberColumn("Already requested")}, hide_index = True)
                i = 0
                for trip in actual_data[['FEMALE', 'FEMALE_GUESTS']].values:
                    i += 1
                    if not fem:
                        if trip[0] == 1:
                            st.info('Trip ' + str(i) + ' is offered by a female driver.', icon = "🧍🏾‍♀️")
                    if not fem_g:
                        if trip[1] == 1:
                            st.info('Trip ' + str(i) + ' is for female guests only!', icon = "👭")
                st.session_state['booking'] = actual_data
            # No data available  
            except:
                st.warning(body = 'No Trips in this range!', icon = "🚨")
                st.info('Choose other selections if possible.', icon = "ℹ️")
        
    # tab `Booking`
    with tab3:
        with st.expander('', expanded = True):
            st.title('Booking')
            st.subheader('Book a trip')
            st.write('Here you book a trip (*you need to contact the driver afterwards*).')
            name = ""
            name = st.text_input('Name (*needed to add your points to the Highscore* 🏆)', key = "name_booking")
            try:
                st.dataframe(st.session_state['booking'][['DEPARTURE', 'DESTINATION', 'DATE', 'START', 'ARRIVAL', 'SEATS', 'REQUEST']], column_config = {
                        "DEPARTURE": st.column_config.TextColumn("From (Departure)"),
                        "DESTINATION": st.column_config.TextColumn("To (Destination)"),
                        "DATE": st.column_config.DatetimeColumn("Date", format = "D MMM YYYY"),
                        "START": st.column_config.DatetimeColumn("Departure", format = "HH:mm"),
                        "ARRIVAL": st.column_config.DatetimeColumn("Arrival", format = "HH:mm"),
                        "SEATS": st.column_config.NumberColumn("Seats"),
                        "REQUEST": st.column_config.NumberColumn("Already requested")}, hide_index = True)

                # Book trip
                seats = st.number_input('Seats', min_value = 1, max_value = 6, value = 1, key = "num_booking")
            
                # Show available trips
                i = 0
                st.session_state['booking']["ID"] = st.session_state['booking'].index
                st.session_state['booking'] = st.session_state['booking'].set_index('ID')
                for idx, row in st.session_state['booking'].iterrows():
                    if seats <= int(row["SEATS"] - row["REQUEST"]):
                        i += 1
                        if st.button('Book trip ' + str(i) + ' (' + str(row["DATE"].strftime('%d-%m-%Y' + ')')), key = "book" + str(i), help = 'Book the trip '):
                            try:
                                databank['PHONE'] = "'" + databank['PHONE'].astype(str)
                                databank["ID"] = databank.index
                                databank.at[idx, 'REQUEST'] = int(databank.loc[databank['ID'] == idx]['REQUEST'].values[0]) + seats
                                data = databank.drop(columns = ['ID'])
                                data = np.array(data)
                                data = data.tolist()
                                write_sheet(data = data, sheet = 0)
                                print('Updated Google Sheet, sheet `trips`')
                                st.toast("Please contact the driver!", icon = '💬')
                                st.session_state['booking'] = []
                                if name != "":
                                    if name in databank_points['NAME'].values:
                                        data = read_sheet(sheet = 1)
                                        data.loc[data['NAME'] == name, 'POINTS'] = int(databank_points.loc[databank_points['NAME'] == name]['POINTS'].values[0]) + 10
                                        data = np.array(data)
                                        data = data.tolist()
                                        write_sheet(data = data, sheet = 1)
                                        print('Updated Google Sheet, sheet `gamification`')
                                    else:
                                        data = read_sheet(sheet = 1)
                                        data = np.array(data)
                                        newrow = np.array([name, 10])
                                        data = np.vstack((data, newrow))
                                        data = data.tolist()
                                        write_sheet(data = data, sheet = 1)
                                        print('Updated Google Sheet, sheet `gamification`)')
                                st.write('**Driver:** ' + row['DRIVER'] + ' (' + row['PHONE'] + ')')
                                st.write('**Mail:** ' + row['MAIL'])
                                st.info('Please contact the driver!', icon = "💬")
                            except Exception as e:
                                print('No Update ', e)
                if i == 0:
                    st.info('Lower the amount of seats you are requesting.', icon = "ℹ️")
  
                # Map
                st.subheader('Map view of trips')
                places = np.concatenate((st.session_state['booking']['DEPARTURE'].unique(), st.session_state['booking']['DESTINATION'].unique()), axis = 0)
                df = pd.DataFrame([], columns = ['lat', 'lon'])
                for place in places:
                    for cordinate in databank_cities['CITY']:
                        if place == cordinate:
                            lat = str(databank_cities.loc[databank_cities['CITY'] == cordinate]['lat.'].values)[1:-1]
                            lon = str(databank_cities.loc[databank_cities['CITY'] == cordinate]['lon.'].values)[1:-1]
                            df.loc[len(df.index)] = [float(lat.replace("'", "")), float(lon.replace("'", ""))]
                # Show map
                st.map(df, size = 20, use_container_width = False)

            except:
                st.warning(body = 'No trips selected!', icon = "🚨")
                st.info('Go to `Hitchhiking` to find a fitting trip.', icon = "ℹ️")   


## Not Logged in state (Landing page)
else:
    landing_page('Car Pool')


