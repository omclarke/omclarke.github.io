from pathlib import Path  # Python Standard Library
import pandas as pd  # pip install pandas
import plotly.express as px
import streamlit as st

import openai_secret_manager 
from googleapitlcient.dicovery import build 

# Use the Google Drive API to authenticate and read the file
secrets = openai_secret_manager.get_secret("google")
service = build('drive', 'v3', credentials=secrets)
request = service.files().get_media(fileId='your_file_id')
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print("Download %d%%." % int(status.progress() * 100))
fh.seek(0)

# Read the CSV file
df = pd.read_csv(fh)

hide_st_style= """
        <style>
        #footer {visibility: hidden;}
        </style>
        """

# Set the page config and title
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Lariat Rental")
st.markdown(hide_st_style, unsafe_allow_html=True)

# Set up the sidebar with various filters
st.sidebar.header("Please filter here")

# Button to toggle airport locations
airport_ind = st.sidebar.selectbox("Include Airport Locations?", ["Include", "Exclude", "Both"])

# Filter for states
state_filter = st.sidebar.multiselect(
    "Select the State",
    options=sales_data["state"].unique(),
    default=sales_data["state"].unique()
)
# Function to generate list of cities based on selected states

def filter_cities():
    if airport_ind == "Include":
        cities = sales_data[(sales_data["state"].isin(state_filter)) & (sales_data["airport_ind"] == True)]["city"].unique()
    elif airport_ind == "Exclude":
        cities = sales_data[(sales_data["state"].isin(state_filter)) & (sales_data["airport_ind"] == False)]["city"].unique()
    else:
        cities = sales_data[sales_data["state"].isin(state_filter)]["city"].unique()
    return st.sidebar.multiselect( 
        'Select the City',
        options=cities,
        default=cities
    )

city_filter = filter_cities()

# Filter for vehicle make
make_filter = st.sidebar.multiselect(
    "Select the vehicle Make",
    options=sorted(sales_data["car_make"].unique()),
    default=sales_data["car_make"].unique()
)

# Filter for customer gender
customer_filter = st.sidebar.multiselect(
    "Select the customers Gender",
    options=sales_data["driver_gender"].unique(),
    default=sales_data["driver_gender"].unique()
)

# Add age slider to the sidebar
age_range = st.sidebar.slider("Select age range", 18, 80, (18, 80))

# Create a mask using boolean indexing to filter the data
if airport_ind == "Include":
    mask = (
        sales_data["city"].isin(city_filter) &
        sales_data["state"].isin(state_filter) &
        sales_data["car_make"].isin(make_filter) &
        sales_data["driver_gender"].isin(customer_filter) &
        (sales_data["airport_ind"] == True) &
        (sales_data["driver_age"] >= age_range[0]) &
        (sales_data["driver_age"] <= age_range[1])
    )
elif airport_ind == "Exclude":
    mask = (
        sales_data["city"].isin(city_filter) &
        sales_data["state"].isin(state_filter) &
        sales_data["car_make"].isin(make_filter) &
        sales_data["driver_gender"].isin(customer_filter) &
        (sales_data["airport_ind"] == False) &
        (sales_data["driver_age"] >= age_range[0]) &
        (sales_data["driver_age"] <= age_range[1])
    )
else:
    mask = (
        sales_data["city"].isin(city_filter) &
        sales_data["state"].isin(state_filter) &
        sales_data["car_make"].isin(make_filter) &
        sales_data["driver_gender"].isin(customer_filter) &
        (sales_data["driver_age"] >= age_range[0]) &
        (sales_data["driver_age"] <= age_range[1])
    )
filtered_data = sales_data[mask]

current_page = 1
if current_page == 1:
# Create a variable to keep track of whether the dataframe is visible
    dataframe_visible = True

show_data = st.checkbox("Show Filtered Data", value=True)

if show_data:
    st.dataframe(filtered_data)
else:
    st.empty()
#___ Main Page, Charts and data visualization ___

# KPI 
total_sales = int(filtered_data['total'].sum())
average_sales = round(filtered_data["total"].mean(), 2)
average_age = round(filtered_data["driver_age"].mean(),)
average_transaction= round(filtered_data['price_per_day'].mean(), 2)
average_rental_sales= round(filtered_data['total'].sum() /filtered_data['rented_length'].sum(), 2)
total_rentals =  int(filtered_data['rented_length'].sum())

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
    st.subheader("Annual Rentals:")
    st.subheader(f"{total_rentals:,}")
with middle_column:
    st.subheader("Average Transaction:")
    st.subheader(f" $ {average_sales}")
    st.subheader("Average Customer Age:")
    st.subheader(f"{average_age:,}")
with right_column:
    st.subheader("Average Rental Length:")
    st.subheader(f"{average_transaction}")
    st.subheader("Average Rental Sales:")
    st.subheader(f" $ {average_rental_sales}")

st.markdown("""---""")

#sales by product line bar chart 

sales_by_make = (
    filtered_data.groupby(by=["car_make"]).sum()[["total"]].sort_values(by="total")
)

fig_product_sales = px.bar(
    sales_by_make,
    y='total',
    x= sales_by_make.index, 
    orientation="v",
    title ="<b>Sales by Make</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_make),
    template = "plotly_white", 
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

sales_by_state = (
    filtered_data.groupby(by=["state"]).sum()[["total"]].sort_values(by="total")
)

fig_product_state = px.bar(
    sales_by_state,
    y='total',
    x= sales_by_state.index, 
    orientation="v",
    title ="<b>Sales by State </b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_state),
    template = "plotly_white", 
)
fig_product_state.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_product_sales, use_containter_width=True)
right_column.plotly_chart(fig_product_state, use_containter_width=True)

hide_st_style= """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visbility: hidden;}
        </style>
        """

# Create a variable to keep track of which tab is currently being displayed
current_tab = "Filters"

# Add a button to switch to the Strategies tab
if st.button("Go to Strategies Page"):
        current_page = 2
#elif current_page == 2:

# Display the appropriate content for the current tab
elif current_tab == "Filters":
    st.sidebar.header("Filters")
    # Add filters code here
elif current_tab == "Strategies":
    st.sidebar.header("Strategies")
    # Add strategy implementation code here

    # Add filter options (city, state, car make, etc)
    city_filter = st.multiselect("Select city", sales_data["city"].unique())
    state_filter = st.multiselect("Select state", sales_data["state"].unique())
    make_filter = st.multiselect("Select car make", sales_data["car_make"].unique())
    customer_filter = st.multiselect("Select customer gender", sales_data["driver_gender"].unique())
    airport_ind = st.selectbox("Include or exclude airport rentals?", ["Include", "Exclude", "All"])
    
    # Create a mask using boolean indexing to filter the data
    if airport_ind == "Include":
        mask = (
            sales_data["city"].isin(city_filter) &
            sales_data["state"].isin(state_filter) &
            sales_data["car_make"].isin(make_filter) &
            sales_data["driver_gender"].isin(customer_filter) &
            (sales_data["airport_ind"] == True)
        )
    elif airport_ind == "Exclude":
        mask = (
            sales_data["city"].isin(city_filter) &
            sales_data["state"].isin(state_filter) &
            sales_data["car_make"].isin(make_filter) &
            sales_data["driver_gender"].isin(customer_filter) &
            (sales_data["airport_ind"] == False)
        )
    else:
        mask = (
            sales_data["city"].isin(city_filter) &
            sales_data["state"].isin(state_filter) &
            sales_data["car_make"].isin(make_filter) &
            sales_data["driver_gender"].isin(customer_filter)
        )
    filtered_data = sales_data[mask]
# Create a variable to keep track of the current page
current_page = 1

if current_page == 1:
    # Add content for the first page
    st.write("This is the first page.")
    # Add a button to navigate to the second page
    if st.button("Go to second page"):
        current_page = 2
elif current_page == 2:
    # Add content for the second page
    st.write("This is the second page.")
    # Add a button to navigate back to the first page
    if st.button("Go back to first page"):
        current_page = 1
#Add a second page to view strategies     
st.write("Page 2", page_break=True)
    # Display the filtered data
st.dataframe(filtered_data)

# Add content to the second page
if current_tabs == "Strategies":
    # Add sliders for strategy implementation
    price_increase = st.slider("Price increase (%)", 1, 100, 25)
    total_rentals = st.slider("Total rentals increase (%)", 1, 100, 25)
    airport_increase = st.slider("Airport locations increase (%)", 1, 100, 25)

    # Add button to implement strategies
    if st.button("Implement Strategies"):
        # Apply strategies to the data
        filtered_data["price"] = filtered_data["price"] * (1 + (price_increase / 100))
        filtered_data["total_rentals"] = filtered_data["total_rentals"] * (1 + (total_rentals / 100))
        filtered_data.loc[filtered_data["airport_ind"] == True, "total_rentals"] = filtered_data.loc[filtered_data["airport_ind"] == False, "total_rentals"]* (1+ (airport_increase / 100))


elif tabs == "Dashboard":
# Create a chart of average price by city
    st.line_chart(filtered_data.groupby("city").mean()["price"])
# Create a chart of average rentals by city
    st.line_chart(filtered_data.groupby("city").mean()["total_rentals"])
# Create a chart of average price by car type
    st.line_chart(filtered_data.groupby("car_type").mean()["price"])
# Create a chart of average rentals by car type
    st.line_chart(filtered_data.groupby("car_type").mean()["total_rentals"])
# Create a histogram of price
    st.hist(filtered_data["price"], bins=20)
# Create a histogram of total rentals
    st.hist(filtered_data["total_rentals"], bins=20)