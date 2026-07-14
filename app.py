import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px


def load_data():
    data = pd.read_excel("Super+Store+Data.xlsx")
    df = data.copy()
    print(df.columns.tolist())
    df = df.rename(columns={
         "Row ID": "Row_ID",
         "Order ID": "Order_ID",
         "Order Date": "Order_Date",
         "Ship Date": "Ship_Date",
         "Customer Name":"Customer_Name",
         "Sub-Category": "Sub_Category",
         "Product Name":"Product_Name",
         "Customer ID":"Customer_ID",
         "Product ID":"Product_ID",
         "Ship Mode":"Ship_Mode"
    })
# add Year column, Month, Quarter etc.
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.month_name()
    df["Quarter"] = df["Order_Date"].dt.quarter
    df["Month_No"] = df["Order_Date"].dt.month
    df["Shipping_Days"] = (
    df["Ship_Date"] - df["Order_Date"]
    ).dt.days
    df["Profit_Margin"] = (df["Profit"] / df["Sales"])
    df["Loss"] = df["Profit"] < 0
    return df


# display to the browser
try:
   df = load_data()
   st.title("SUPER STORE ANALYSIS")
   st.dataframe(df)

   #st.write(df.isnull()  -sum)) #check for null
#st.write(df.dtypes)

   filters = {
    "Year":df["Year"].unique(),
    "Month":df["Month"].unique(),
    "Ship_Mode":df["Ship_Mode"].unique(),
    "Segment":df["Segment"].unique(),
    "State":df["State"].unique(),
    "City":df["City"].unique(),
    "Category":df["Category"].unique()
    }
# store user selection
   selected_filters = {}

# generate multi-select widgets dynamically
   for key, options in filters.items():
        selected_filters[key] = st.sidebar.multiselect(key, options)

# selected data filtered
   filtered_df = df.copy()

# apply user selections to the data
   for key, selected_values in selected_filters.items():
       if selected_values:
            filtered_df = filtered_df[filtered_df[key]\
                                      .isin(selected_values)]

# view data
   st.dataframe(filtered_df)

# section 2: Calculations
   total_sales = filtered_df["Sales"].sum()
   total_profit = filtered_df["Profit"].sum()
   no_orders = len(filtered_df)
   no_customers = filtered_df["Customer_ID"].nunique()

   col1, col2, col3, col4 = st.columns(4)

   with col1:
       st.write(f"Total Sales: ${total_sales:,.2f}")

   with col2:
       st.write(f"Total Profit: ${total_profit:,.2f}")

   with col3:
       st.write(f"Orders: ${no_orders:,.2f}")

   with col4:
       st.write(f"Customers: ${no_customers:,.2f}")
       
   # Charts
   # chart data
   temp_df = (
       filtered_df.groupby("Year", as_index=False)
       .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
       .sort_values("Year")
   )
   
   st.header("yearly Trend - Sales & Profit")

   metric_choice = st.radio(
       "Trend Metric",
       ["Sales", "Profit"],
       horizontal=True, key="trend_metric",
   )

   trend = (
       alt.Chart(temp_df)
       .mark_line(point=True)
       .encode(
           x=alt.X("Year:T", title="Year"),
           y=alt.Y(f"{metric_choice}:Q", title=metric_choice),
           tooltip=[
               alt.Tooltip("Year:T", title="Year", format="%Y"),
               alt.Tooltip(f"{metric_choice}:Q", format="$,.2f")
               ],
           )
       .properties(height=360)
       .interactive()
       )
   st.altair_chart(trend, use_container_width=True)
   #chart
   
   st.header("Locations")
   
   geo_col, ship_col = st.columns([1.2, 1])
   
   #chart data
   state_df = (
       filtered_df.groupby(["State","Region"], as_index=False)
       .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
       .sort_values("Sales", ascending=False)
       .head(15)
   )
   
   with geo_col:
       fig_state = px.bar(
           state_df.sort_values("Profit"), X="Profit",y="State",
           orientation="h",color="Region",
           title="Top states by sales, ranked by profit",
           hover_data={"sales": ":,.2f"},
       )
       fig_state.add_vline(x=0, line_dash="dash")
       fig_state.update_layout(height=480,
                               margin=dict(l=10, r=10, t=50, b=10))
       st.ploty_chart(fig_state, use_container_width= True)
       
except Exception as e:
       st.exception(e)

    
    
    
    
    
    
    
        