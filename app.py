# =============================== IMPORT LIBRARY ===============================
import mysql.connector
import streamlit as st 
from streamlit_option_menu import option_menu
import pandas as pd 
import plotly.express as px 
import plotly.graph_objects as go

# =============================== CONNECTING TO SQL ===============================
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1000Shaik#1',
    database='phone_pe_project_latest'
)
mycursor = mydb.cursor()
print("Connection Established")

# =============================== PAGE CONFIGURATION ===============================
st.set_page_config(
    page_title="Phonepe Pulse Data Visualization | By Rahemath",                   
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================== SIDEBAR MENU ===============================
with st.sidebar:
    selected = option_menu("Menu", ["Data Overview", "Top Metrics", "Insights"], 
                           icons=["table", "bar-chart", "lightbulb"],
                           menu_icon="menu-button-wide",
                           default_index=0,
                           styles={
                               "nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#6F36AD"},
                               "nav-link-selected": {"background-color": "#6F36AD"}
                           })

# =============================== HELPER FUNCTIONS ===============================
def plot_choropleth(df, color_column, color_scale, title):
    fig = px.choropleth(
        df,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color=color_column,
        color_continuous_scale=color_scale,
        hover_name='State'
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(coloraxis_colorbar=dict(
        title=title,
        tickvals=[df[color_column].min(), df[color_column].max()],
        ticktext=["Low", "High"]
    ))
    return fig

def plot_line_trend(df, y_column, y_title):
    fig = px.line(df, x='Year-Quarter', y=y_column, markers=True)
    fig.update_layout(
        xaxis_title="Year-Quarter",
        yaxis_title=y_title,
        xaxis=dict(tickmode='linear', tickangle=-45),  
    )
    return fig

def fetch_data(query):
    mycursor.execute(query)
    return pd.DataFrame(mycursor.fetchall())

# =============================== DATA OVERVIEW PAGE ===============================
if selected == "Data Overview":
    col1, col2 = st.columns([1,9])
    with col1:        
        st.image("ICN.png")
    with col2:
        st.markdown("<h1 style='text-align: center; color: violet;'>Phonepe Pulse Data Visualization (2018 Q1 - 2024 Q2)</h1>", unsafe_allow_html=True)
        
    st.write("")  # Adding extra space    
    
    col1, col2, col3 = st.columns(3)
    with col1:
        Year = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022', '2023', '2024'), key='Year')
    with col2:
        Quarter = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='Quarter')
    with col3:
        Type = st.selectbox("**Select Type**", ("Transactions", "Users"))      

    if Type == "Transactions":
        transaction_type = st.radio("TRANSACTION METRIC", options=["Transaction Count", "Transaction Amount"], index=0)

        if transaction_type == "Transaction Amount":
            st.markdown("### :violet[Overall State Data - Transaction Amount]")
            
            try:
                query = f""" 
                    select State, sum(Count) as Total_Transactions, sum(Amount) as Total_amount
                    from map_transactions
                    where year = {Year} and quarter = {Quarter}
                    group by State 
                    order by State
                """
                df1 = fetch_data(query)
                if not df1.empty:
                    df1.columns = ['State', 'Total_Transactions', 'Total_amount']
                    df2 = pd.read_csv('Statenames.csv')
                    df1.State = df2
                    st.plotly_chart(plot_choropleth(df1, 'Total_amount', 'Viridis', 'Transaction Amount'), use_container_width=True)
                
                else:
                    st.warning("No data available for the selected year and quarter.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            
            # --------------------------------------------------------------------------------
                
            st.markdown("### :violet[Transaction Amount Trend Over Time]")
            
            try:
                df4 = fetch_data("Select * From aggregate_Transactions")
                if not df4.empty:
                    df4.columns = ['State', 'Year', 'Quarter', 'Transaction_type', 'Transaction_count', 'Transaction_amount']
                    df4['Year-Quarter'] = df4['Year'].astype(str) + ' Q' + df4['Quarter'].astype(str)
                    df_grouped = df4.groupby('Year-Quarter', as_index=False)['Transaction_amount'].sum()
                    st.plotly_chart(plot_line_trend(df_grouped, 'Transaction_amount', 'Transaction Amount'), use_container_width=True)
                else:
                    st.warning("No data available for the selected year and quarter.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                
            #------------------------------------------------------------------------------------
            
            st.markdown("### :violet[Explore State Wise Data - Transaction Amount]")
            selected_state = st.selectbox("",
                                          ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                                           'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana',
                                           'himachal-pradesh', 'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
                                           'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
                                           'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                                           'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'), index=30)
            
            query = f"""select State, District, year, quarter, sum(Count) as Total_Transactions, sum(Amount) as Total_amount
                        from map_transactions
                        where year = {Year} and quarter = {Quarter} and State = '{selected_state}'
                        group by State, District, year, quarter order by State, District"""
                        
            try:
                df1 = fetch_data(query)
                if not df1.empty:
                    df1.columns = ['State', 'District', 'Year', 'Quarter', 'Total_Transactions', 'Total_amount']
                    fig = px.bar(df1, title=selected_state, x="District", y="Total_amount", orientation='v')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for the selected year and quarter.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        
        # ==========================================================================================
        
        elif transaction_type == "Transaction Count":
            st.markdown("### :violet[Overall State Data - Transaction Count]")

            query = f""" 
                select State, sum(Count) as Total_Transactions, sum(Amount) as Total_amount 
                from map_transactions
                where year = {Year} and quarter = {Quarter}
                group by State 
                order by State
            """
            try: 
                df1 = fetch_data(query)
                if not df1.empty:
                    df1.columns = ['State', 'Total_Transactions', 'Total_amount']
                    df2 = pd.read_csv('Statenames.csv')
                    df1.Total_Transactions = df1.Total_Transactions.astype(int)
                    df1.State = df2

                    st.plotly_chart(plot_choropleth(df1, 'Total_Transactions', 'sunset', 'Transaction Count'), use_container_width=True)
                else:
                    st.warning("No data available for the selected year and quarter.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                
            # -----------------------------------------------------------------------------------
                
            st.markdown("### :violet[Transaction Count Trend Over Time]")
            
            try:
                df4 = fetch_data("Select * From aggregate_Transactions")
                if not df4.empty:
                    df4.columns = ['State', 'Year', 'Quarter', 'Transaction_type', 'Transaction_count', 'Transaction_amount']
                    df4['Year-Quarter'] = df4['Year'].astype(str) + ' Q' + df4['Quarter'].astype(str)
                    df_grouped = df4.groupby('Year-Quarter', as_index=False)['Transaction_count'].sum()

                    st.plotly_chart(plot_line_trend(df_grouped, 'Transaction_count', 'Transaction Count'), use_container_width=True)
                else:
                    st.warning("No data available for the selected year and quarter.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                
            # -----------------------------------------------------------------------------------
                           
            st.markdown("###  :violet[Explore State Wise Data - Transaction Count]")
            selected_state = st.selectbox("",
                                        ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                                        'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana',
                                        'himachal-pradesh', 'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
                                        'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
                                        'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                                        'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'), index=30)
            
            query = f"""select State, District, year, quarter, sum(Count) as Total_Transactions, sum(Amount) as Total_amount
                        from map_transactions
                        where year = {Year} and quarter = {Quarter} and State = '{selected_state}'
                        group by State, District, year, quarter order by State, District"""
            
            try:
                df1 = fetch_data(query)
                if not df1.empty:
                    df1.columns = ['State', 'District', 'Year', 'Quarter', 'Total_Transactions', 'Total_amount']
                    fig = px.bar(df1, title=selected_state, x="District", y="Total_Transactions", orientation='v')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for the selected year and quarter.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # ============================================================================================

    if Type == 'Users':
        st.write("")
        st.markdown("### :violet[Overall State Data - Registered Users]")
        query = f"""select State, sum(RegisteredUser) as Total_Users, sum(AppOpens) as Total_Appopens
                    from map_users
                    where year = {Year} and quarter = {Quarter}
                    group by State order by State"""
        
        try:
            df1 = fetch_data(query)
            if not df1.empty:
                df1.columns = ['State', 'Total_Users', 'Total_Appopens']
                df2 = pd.read_csv('Statenames.csv')
                df1.Total_Users = df1.Total_Users.astype(float)
                df1.Total_Appopens = df1.Total_Appopens.astype(float)
                df1.State = df2
        
                st.plotly_chart(plot_choropleth(df1, 'Total_Users', 'cividis', 'Registered Users'), use_container_width=True)
                st.markdown("### :violet[Overall State Data - App Opens]")
                st.plotly_chart(plot_choropleth(df1, 'Total_Appopens', 'Blues', 'App Opens'), use_container_width=True)           
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        # ----------------------------------------------------------------------------------------                  
                
        st.markdown("## :violet[Select any State to explore more]")
        selected_state = st.selectbox("",
                             ('andaman-&-nicobar-islands','andhra-pradesh','arunachal-pradesh','assam','bihar',
                              'chandigarh','chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu','delhi','goa','gujarat','haryana',
                              'himachal-pradesh','jammu-&-kashmir','jharkhand','karnataka','kerala','ladakh','lakshadweep',
                              'madhya-pradesh','maharashtra','manipur','meghalaya','mizoram',
                              'nagaland','odisha','puducherry','punjab','rajasthan','sikkim',
                              'tamil-nadu','telangana','tripura','uttar-pradesh','uttarakhand','west-bengal'), index=30)
        
        query = f"""select State, year, quarter, District, sum(RegisteredUser) as Total_Users, sum(AppOpens) as Total_Appopens
                    from map_users
                    where year = {Year} and quarter = {Quarter} and state = '{selected_state}'
                    group by State, District, year, quarter order by State, District"""
                    
        try:
            df = fetch_data(query)
            if not df.empty:
                df.columns = ['State', 'year', 'quarter', 'District', 'Total_Users', 'Total_Appopens']
                df.Total_Users = df.Total_Users.astype(int)
        
                fig = px.bar(df,
                        title=selected_state,
                        x="District",
                        y="Total_Users",
                        orientation='v',
                        color='Total_Users',
                        color_continuous_scale=px.colors.sequential.Agsunset)
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# =============================== TOP CHARTS PAGE ===============================

elif selected == "Top Charts":
    st.markdown("""<h1 style='text-align: center; color: violet;'>TOP METRICS</h1>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        Year = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022', '2023', '2024'), key='Year')
    with col2:
        Quarter = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='Quarter')
    tab1, tab2 = st.tabs(['Transaction', 'User'])  
    
    with tab1:
        st.markdown("### :violet[Top 10 States - Transaction Amount]")
        query = f"""select State, sum(Transaction_count) as Total_Transactions_Count,
                    sum(Transaction_amount) as Total from aggregate_transactions
                    where year = {Year} and quarter = {Quarter}
                    group by State order by Total desc limit 10"""
                    
        try:
            df = fetch_data(query)
            if not df.empty:
                df.columns = ['State', 'Transactions_Count', 'Total_Amount']
                fig = px.pie(df, values='Total_Amount', names='State', color_discrete_sequence=px.colors.sequential.Agsunset,
                     hover_data=['Transactions_Count'])
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        # -------------------------------------------------------------------------------------
        
        st.markdown("### :violet[Top 10 Districts with Highest Transactions Amount]")
        query = f"""select State, District, sum(Count) as Total_Count, sum(Amount) as Total
                    from map_transactions
                    where year = {Year} and quarter = {Quarter}
                    group by State, District order by Total desc limit 10"""
        try:
            df = fetch_data(query)
            if not df.empty:                
                df.columns = ['State', 'District', 'Transactions_Count', 'Total_Amount']        
                fig2 = px.sunburst(df, path=['State', 'District'], values='Total_Amount', color='State', color_continuous_scale='RdBu')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        # --------------------------------------------------------------------------------------
        
        st.markdown("### :violet[Top 10 Pincodes with Highest Transaction Amount]")
        query = f"""select State, Pincode, sum(Transaction_count) as Total_Transactions_Count, sum(Transaction_amount) as Total
                    from top_transactions_pincode
                    where year = {Year} and quarter = {Quarter}
                    group by State, Pincode order by Total desc limit 10"""
        try:
            df = fetch_data(query)
            if not df.empty:
                df.columns = ['State', 'Pincode', 'Transactions_Count', 'Total_Amount']
        
                fig3 = px.treemap(df, path=[px.Constant('India'), 'State', 'Pincode'], values='Total_Amount', color='State', color_continuous_scale='RdBu')
                st.plotly_chart(fig3, use_container_width=True)
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
        # -------------------------------------------------------------------------------------------
        
        st.markdown("## :violet[Top Payment Type]")
        query = f"""select Transaction_type, sum(Transaction_count) as Total_Transactions, sum(Transaction_amount) as Total_amount
                    from aggregate_transactions
                    where year= {Year} and quarter = {Quarter}
                    group by Transaction_type order by Transaction_type"""
        try:
            df = fetch_data(query)
            if not df.empty:
                df.columns = ['Transaction_type', 'Total_Transactions', 'Total_amount']

                fig = px.bar(df, title='Transaction Types vs Total_Transactions', x="Transaction_type", y="Total_Transactions", orientation='v',
                     color='Total_amount', color_continuous_scale=px.colors.sequential.Agsunset)
                st.plotly_chart(fig, use_container_width=False)
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
    # ------------------------------------------------------------------------------------------
        
    with tab2:
        st.markdown("### :violet[Top 10 Brands]")
        if (Year, Quarter) in [(2022, 2), (2022, 3), (2022, 4), (2023, 1), (2023, 2), (2023, 3), (2023, 4), (2024, 1), (2024, 2)]:
            st.warning("No data available for the selected year and quarter.")
        else:
            query = f"""select Brands, sum(Count) as Total_Count, round(avg(Percentage),0) as Avg_Percentage
                        from aggregate_users where year = {Year} and quarter = {Quarter}
                        group by Brands order by Total_Count desc limit 10"""
            df = fetch_data(query)

            if df.empty:
                st.markdown("#### No data available for the selected year and quarter.")
            else:
                df.columns = ['Brand', 'Total_Users', 'Avg_Percentage']
                fig = px.bar(df, x="Total_Users", y="Brand", orientation='h', color='Avg_Percentage', color_continuous_scale=px.colors.sequential.Agsunset)
                st.plotly_chart(fig, use_container_width=True)
        
        # ---------------------------------------------------------------------------------------
        
        st.markdown("### :violet[Top 10 District - Registered Users]")
        query = f"""select District, sum(RegisteredUser) as Total_Users, sum(AppOpens) as Total_AppOpens
                    from map_users
                    where year = {Year} and quarter = {Quarter}
                    group by District order by Total_Users desc limit 10"""
        try:
            df = fetch_data(query)
            if not df.empty:
                df.columns = ['District', 'Total_Users', 'Total_AppOpens']
                fig = px.bar(df, x="Total_Users", y="District", orientation='h', color='Total_Users', color_continuous_scale=px.colors.sequential.Agsunset)
                st.plotly_chart(fig, use_container_width=True)
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
        # ---------------------------------------------------------------------------------------       
        
        st.markdown("### :violet[Top 10 Pincodes - Registered Users]")
        query = f"""select Pincode, sum(RegisteredUsers) as Total_Users
                    from top_users_pincode
                    where year = {Year} and quarter = {Quarter}
                    group by Pincode
                    order by Total_Users desc
                    limit 10"""
        try:
            df = fetch_data(query)
            if not df.empty:
                df.columns = ['Pincode', 'Total_Users']
                fig = px.pie(df, values='Total_Users', names='Pincode', color_discrete_sequence=px.colors.sequential.Agsunset)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        # --------------------------------------------------------------------------------------
        
        st.markdown("### :violet[Top 10 States - Registered Users]")
        query = f"""select State, sum(RegisteredUser) as Total_Users, sum(AppOpens) as Total_AppOpens
                    from map_users
                    where year = {Year} and quarter = {Quarter}
                    group by State
                    order by Total_Users desc
                    limit 10"""
        try:
            df = fetch_data(query)
            if not df.empty:
                df.columns = ['State', 'Total_Users', 'Total_Appopens']
                fig = px.pie(df, values='Total_Users', names='State', color_discrete_sequence=px.colors.sequential.Agsunset,
                     hover_data=['Total_Appopens'])
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                    st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# =============================== INSIGHTS PAGE ===============================
elif selected == "Insights":
    st.markdown("""<h1 style='text-align: center; color: violet;'>INSIGHTS</h1>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        Year = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022', '2023', '2024'), key='Year')
    with col2:
        Quarter = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='Quarter')
    with col3:
        selected_state = st.selectbox("Select State",
                                      ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                                       'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana',
                                       'himachal-pradesh', 'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
                                       'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
                                       'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                                       'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'), index=30)
            
    Insight = st.selectbox("Select Insights", ("Change in Payment Trends", "Inter State Disparity", "Intra State Disparity"))

    if Insight == "Change in Payment Trends":
        df3 = fetch_data("select * from aggregate_transactions")
        df3.columns = ['State', 'Year', 'Quarter', 'Transaction_type', 'Transaction_count', 'Transaction_amount']
        df3['year_quarter'] = df3['Year'].astype(str) + ' Q' + df3['Quarter'].astype(str)
        fig = px.scatter(df3, x='Transaction_count', y='Transaction_amount', animation_frame='year_quarter',
                         color='Transaction_type', range_x=[0, 2.5e9], range_y=[0, 3e12])

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
            **Key Insights**:
            
            🏦 **Shift Towards a Cashless Economy**:
            - **Increase in smaller transactions**: People are making more transactions with smaller amounts, indicating a move towards a more cashless society.

            💳 **Growing Confidence in UPI**:
            - There is a **rise in larger payments** via UPI, with a daily transaction limit of **1 lakh**. This shows growing trust in UPI for big transactions.

            ⚡ **Recharge & Bill Payments: Room for Growth**:
            - **Limited coverage** in the recharge and bill payment sector presents **significant opportunities** for growth.
            - **Why?**:
                - 📱 Rise of **dedicated apps**.
                - ⏳ **Delays in payment reflections**, especially in sectors like **electricity bills**, causing frustration among users.
        """)
                
    elif Insight == "Inter State Disparity":
        query = f"""select State, sum(Transaction_count) as Total_Transactions_Count, sum(Transaction_amount) as Total
                    from aggregate_transactions
                    where Year = {Year} and Quarter = {Quarter}
                    group by State order by State"""
        df = fetch_data(query)
        df.columns = ['State', 'Transaction_amount', 'Transaction_count']
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['State'], y=df['Transaction_amount'], name='Transaction Amount'))
        fig.add_trace(go.Scatter(x=df['State'], y=df['Transaction_count'], mode='lines+markers', name='Transaction Count', yaxis='y2'))
        fig.update_layout(
            title="Correlation between Transaction count and Transaction Amount",
            xaxis=dict(title='States', tickangle=45),
            yaxis=dict(title="Transaction Amount", showgrid=False),
            yaxis2=dict(title="Transaction Count", overlaying='y', side='right'),
            template='plotly',
            legend=dict(x=1.05, y=1, xanchor='left', yanchor='top'),
            margin=dict(r=100, t=50, b=100, l=50)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
            **Key Insights**:

            🌍 **Lower Transaction Activity** (North Eastern States, Himalayan States, and Union Territories):
            
                - **Challenges**:  
                    - Lower population, connectivity issues.
            
                - **Solutions**:  
                    - Enhance **digital payment literacy**.
                    - Improve **user interfaces** and **security**.
                    - Collaborate with **government initiatives**.

            🌊 **Higher Transaction Activity** (Coastal and Hinterland India):

                - **Current Success**:  
                    - Strong adoption of **digital payments**.

                - **Opportunities for Growth**:  
                    - **Tailored financial products** and **services**.
                    - Expand **merchant acceptance** and **local business partnerships**.
                    - Leverage **regional success stories**.
        """)

    elif Insight == "Intra State Disparity":
        query = f"""select State, District, year, quarter, sum(Count) as Total_Transactions, sum(Amount) as Total_amount
                    from map_transactions
                    where year = {Year} and quarter = {Quarter} and State = '{selected_state}'
                    group by State, District, year, quarter order by State, District"""
        
        try:
            df1 = fetch_data(query)
            if not df1.empty:
                df1.columns = ['State', 'District', 'Year', 'Quarter', 'Total_Transactions', 'Total_amount']
                fig2 = px.sunburst(df1, path=['State', 'District'], values='Total_Transactions', color='State', color_continuous_scale='Viridis')
                fig2.update_traces(textinfo='label+percent entry', hovertemplate='<b>%{label}</b><br>Transactions: %{value}<br>Percent: %{percent:.2%}<extra></extra>')
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown("""
                ## **Key Insights**:
            
                ### 📍 **Karnataka - Digital Payment Adoption**:
            
                **Challenges:**
                - **Unequal digital payment adoption** across the state.
                - **Bengaluru Urban District** accounts for nearly **69%** of total transactions in Karnataka, highlighting a regional disparity.
            
                **Ways to Reduce Disparity**:
                - 💡 **Promote digital literacy** to bridge the knowledge gap.
                - 🏗️ **Develop infrastructure** in underserved areas to improve connectivity.
                - 🎁 **Offer incentives** for users adopting digital payments.
                - 📢 **Run awareness campaigns** to educate citizens on the benefits of digital payments.
            """)
            else:
                st.warning("No data available for the selected year and quarter.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

