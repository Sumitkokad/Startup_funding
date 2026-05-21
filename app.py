import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
df=pd.read_csv('startup_funding_clean.csv')
original=pd.read_csv('df_original.csv')
import plotly.express as px

# Some preprocessing  of investors ->

df['investors']=df['investors'].str.replace(r'\\n','',regex=True)
df['investors']=df['investors'].str.replace(r'\n','',regex=True)
df['investors']=df['investors'].str.replace(r'\\x[a-fA-F0-9]{2}','',regex=True)
df['investors']=df['investors'].str.replace(r'\\','',regex=True)



# Some processing of round for stags ->

df['round']=df['round'].str.replace('\\\\n','')
df['round']=df['round'].str.replace('/',',')
df['round']=df['round'].str.lower()

df['stage'] = df['round'].replace({

    # ---------------- Seed Stage ----------------

    'pre-series a':'Seed Stage',
    'pre series a':'Seed Stage',

    'seed round':'Seed Stage',
    'seed':'Seed Stage',
    'seed funding':'Seed Stage',
    'seed funding round':'Seed Stage',
    'seedfunding':'Seed Stage',

    'angel':'Seed Stage',
    'angel round':'Seed Stage',
    'angel funding':'Seed Stage',

    'seed, angel funding':'Seed Stage',
    'seed , angel funding':'Seed Stage',
    'seed,angel funding':'Seed Stage',
    'seed , angle funding':'Seed Stage',
    'angel , seed funding':'Seed Stage',

    'bridge round':'Seed Stage',
    'crowd funding':'Seed Stage',
    'maiden round':'Seed Stage',

    # ---------------- Early Growth ----------------

    'series a':'Early Growth Stage',
    'series b':'Early Growth Stage',
    'series b (extension)':'Early Growth Stage',

    # ---------------- Growth Stage ----------------

    'series c':'Growth Stage',
    'series d':'Growth Stage',

    # ---------------- Late Stage ----------------

    'series e':'Late Stage',
    'series f':'Late Stage',
    'series g':'Late Stage',
    'series h':'Late Stage',
    'series j':'Late Stage',

    'private equity':'Late Stage',
    'private equity round':'Late Stage',
    'privateequity':'Late Stage',
    'private':'Late Stage',
    'private funding':'Late Stage',

    # ---------------- Debt Stage ----------------

    'debt':'Debt Stage',
    'debt funding':'Debt Stage',
    'debt-funding':'Debt Stage',
    'debt and preference capital':'Debt Stage',
    'structured debt':'Debt Stage',
    'term loan':'Debt Stage',
    'mezzanine':'Debt Stage',

    # ---------------- Venture Stage ----------------

    'venture':'Venture Stage',
    'single venture':'Venture Stage',
    'venture round':'Venture Stage',
    'venture - series unknown':'Venture Stage',

    'corporate round':'Venture Stage',
    'funding round':'Venture Stage',
    'equity':'Venture Stage',
    'equity based funding':'Venture Stage',
    'inhouse funding':'Venture Stage',

    # ---------------- Other ----------------

    'undisclosed':'Other'

})




# Some processing of Startup -------------------------------------->
df['startup']=df['startup'].str.replace("BYJU's","Byju's")

















# Layout  --------->






st.sidebar.title('StartUp Funding Project')
st.set_page_config(layout='wide')


option = st.sidebar.selectbox('Select One',['Overall Analysis','Startup','Investor'])


if option=='Overall Analysis':

    st.title('Overall Analysis')
    col1,col2,col3,col4=st.columns(4)
    with col1:

       with st.container(border=True):
           st.header('Total Funding')
           st.subheader(f'Cr {round(original['amount'].sum(0),4)}')


    with col2:

        with st.container(border=True):
            st.header('Peak Funding')
            st.subheader(f'Cr {original['amount'].max()}')



    with col3:
        mean_amount=df['amount']

        with st.container(border=True):
            st.header('Average Funding')
            st.subheader(f'Cr {round(original['amount'].mean(),3)}')

    with col4:
        with st.container(border=True):
            st.header('Total StartUp')
            unique_startup=df['startup'].unique()
            st.subheader(f' {(unique_startup.shape[0])}')

    df['date'] = pd.to_datetime(df['date'])

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # MOM Chart ------------------------------------------------------------------------->

    st.subheader('Month On Month Funding Count')

    temp = df.groupby(['year', 'month'])['startup'].count().reset_index()

    temp['x'] = temp['month'].astype(str) + '-' + temp['year'].astype(str)

    fig = px.line(
        temp,
        x='x',
        y='startup',
        markers=True,

    )

    st.plotly_chart(fig, use_container_width=True)

    # Funding Type ----------------------------------------------------------------------->

    st.subheader('Funding Type')

    funding_type = df['round'].value_counts()

    fig = px.bar(
        x=funding_type.index,
        y=funding_type.values
    )

    st.plotly_chart(fig, use_container_width=True)










    # City Wise Funding ------------------------------------------------------------------>

    st.subheader('City Wise Funding')

    city = (
        df.groupby('city')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig = px.bar(
        x=city.index,
        y=city.values
    )

    st.plotly_chart(fig)



    # Top Startups ---------------------------------------------------------------------------->

    st.subheader('Top Startups')

    top_startups = (
        df.groupby('startup')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.dataframe(top_startups)



    # Top Investors ----------------------------------------------------------------------->

    st.subheader('Top Investors')

    top_investors = (
        df.groupby('investors')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.dataframe(top_investors)

    st.subheader('Funding Heatmap')

    heatmap = df.pivot_table(
        index='city',
        columns='year',
        values='amount',
        aggfunc='sum'
    )

    fig = px.imshow(
        heatmap,
        text_auto=True,
        aspect='auto',
        title='City vs Year Funding Heatmap'
    )

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='City'
    )

    st.plotly_chart(fig, use_container_width=True)



    # Pivot table ----------------------------------------------------------------------------->
    st.subheader('Funding Pivot Table')

    heatmap = df.pivot_table(
        index='city',
        columns='year',
        values='amount',
        aggfunc='sum'
    )

    st.dataframe(heatmap)





    # YOY Chart -------------------------------------------------------------------------->
    df['date'] = pd.to_datetime(df['date'])
    st.subheader('Year Wise Startup Funding Trend')
    temp = df.groupby(df['date'].dt.year)['Sr No'].count().reset_index()

    temp.columns = ['year', 'count']

    fig = px.line(
        temp,
        x='year',
        y='count',
        markers=True,

    )


    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Number of Fundings'
    )

    st.plotly_chart(fig, use_container_width=True)


# StartUp code/logic ------------------------------------------------------------------------>











if option=='Startup':
    startup = st.sidebar.selectbox('Select Startup', sorted(df['startup'].unique().tolist()))
    btn1=st.sidebar.button('Find StartUp Details')
    st.title('Start up')

    if btn1:
        st.title(startup.upper())

        startup_df = df[df['startup'] == startup]

        # ---------------- Basic Details ----------------

        st.subheader("Startup Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            with st.container(border=True):
                st.metric(
                    'Industry',
                    startup_df['vertical'].iloc[0]
                )

        with col2:
            with st.container(border=True):
                st.metric(
                    'Subindustry',
                    startup_df['subvertical'].iloc[0]
                )

        with col3:
            with st.container(border=True):
                st.metric(
                    'Location',
                    startup_df['city'].iloc[0]
                )

        with col4:
            with st.container(border=True):
                st.metric(
                    'Total Funding',
                    f"{round(startup_df['amount'].sum(), 2)} Cr"
                )

        st.write('')

        # ---------------- Funding Timeline ----------------

        st.subheader('Funding Timeline')

        timeline = startup_df.copy()

        timeline['date'] = pd.to_datetime(timeline['date'])

        timeline = timeline.sort_values('date')

        fig = px.line(
            timeline,
            x='date',
            y='amount',
            markers=True,
            title='Funding Growth Over Time'
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------------- Funding Round Distribution ----------------

        st.subheader('Funding Round Distribution')

        round_data = (
            startup_df['round']
            .value_counts()
            .reset_index()
        )

        round_data.columns = ['round', 'count']

        fig = px.pie(
            round_data,
            names='round',
            values='count',
            title='Funding Round Share'
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------------- Investors ----------------

        st.subheader('Investors')

        investor_data = (
            startup_df['investors']
            .value_counts()
            .reset_index()
        )

        investor_data.columns = ['investor', 'count']

        fig = px.bar(
            investor_data,
            x='investor',
            y='count',
            text_auto=True,
            title='Investor Participation'
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------------- Funding Details Table ----------------

        st.subheader('Funding Details')

        st.dataframe(
            startup_df[
                ['date', 'round', 'investors', 'amount']
            ].sort_values('date', ascending=False),
            use_container_width=True,
            hide_index=True
        )










# Logic function only for investors---------------------------------------------------------------->


def investor_funding(x):
    investment=df[df['investors'].str.contains(x)][['date', 'startup', 'vertical','city', 'investors','round', 'amount']]
    st.dataframe(investment,hide_index=True)



# City Wise Pie chart ----------------------------------------------------------------->


def pie_chart(x):

    chart = df[
        df['investors'].str.contains(x, na=False, regex=False)
    ]['city'].value_counts().head(8).reset_index()

    chart.columns = ['city', 'count']

    fig = px.pie(
        chart,
        names='city',
        values='count',
        title='City Wise Investment'
    )

    st.plotly_chart(fig, use_container_width=True)


# Year to Year investment graph ------------------------------------------------------->


def yoy_investment_graph(inv):

    x = df[
        df['investors'].str.contains(inv, na=False, regex=False)
        & (df['amount'] > 0)
    ].copy()

    x['date'] = pd.to_datetime(x['date'], errors='coerce')

    x = x.dropna(subset=['date'])

    x['year'] = x['date'].dt.year

    yearly = (
        x.groupby('year')['amount']
        .sum()
        .reset_index()
    )

    fig = px.line(
        yearly,
        x='year',
        y='amount',
        markers=True,
        title='Year Wise Investment Trend'
    )

    st.plotly_chart(fig, use_container_width=True)


# General investment found in round ----------------------------------------------------->

def generally_invested_in(inv):
    x = df[df['investors'] == inv]
    result=x['round'].value_counts().head(1).index[0]
    st.write(result)



# Biggest Investment -------------------------------------------------------------------------->


def biggest_investment(inv):
    x=df[df['investors']==inv]
    result=x.sort_values('amount',ascending=False).head(1)
    if (x['amount']>0).any():
        st.dataframe(result)
    else:
        st.write("Amount of Investment is Zero")




def sector_pie(x):

    chart = df[
        df['investors'].str.contains(x, na=False, regex=False)
    ]['vertical'].value_counts().head(8).reset_index()

    chart.columns = ['sector', 'count']

    fig = px.pie(
        chart,
        names='sector',
        values='count',
        title='Sector Wise Investment'
    )

    st.plotly_chart(fig, use_container_width=True)




def stage_pie(x):

    chart = df[
        df['investors'].str.contains(x, na=False, regex=False)
    ]['stage'].value_counts().reset_index()

    chart.columns = ['stage', 'count']

    fig = px.pie(
        chart,
        names='stage',
        values='count',
        title='Stage Wise Investment'
    )

    st.plotly_chart(fig, use_container_width=True)


def bar_biggest(x):

    investor_df = df[
        (df['investors'].str.contains(x, na=False, regex=False)) &
        (df['amount'] > 0)
    ]

    big_series = (
        investor_df
        .groupby('startup')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    fig = px.bar(
        big_series,
        x='startup',
        y='amount',
        title='Top 5 Biggest Investments',
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)


def similar_investor(x):
    inv=df[df['investors'].str.contains(x, na=False, regex=False)]['vertical']
    result=df[df['vertical'].isin(inv)]
    st.dataframe(result)


if option=='Investor':
    investor = st.sidebar.selectbox('Select Investor', sorted(df['investors'].dropna().unique().tolist()))









    st.title(f'Selected Investor : {investor}')
    btn2 = st.sidebar.button('Find StartUp Details')


    # Creating the logic of investors ------->

    if btn2:
        st.header(f'{investor} Analysis Dashboard')

        # ---------------- Metrics ----------------

        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):

                st.subheader('Preferred Round')
                generally_invested_in(investor)
                st.write('')
                st.write('')
                st.write('')



        with col2:
            with st.container(border=True):
                st.subheader('Total Investments')
                total = df[df['investors'].str.contains(investor, na=False)].shape[0]
                st.metric('Count', total)



        with col3:
            with st.container(border=True):
                st.subheader('Total Funding')
                total_amount = df[df['investors'].str.contains(investor, na=False)]['amount'].sum()
                st.metric('Amount', f'{round(total_amount, 2)} Cr')


        # ---------------- Table ----------------

        with st.container(border=True):
            st.subheader('Most Recent Investments')

            investor_funding(investor)


        with st.container(border=True):
            st.subheader('Biggest Investment')
            biggest_investment(investor)







        # ---------------- Charts Row 1 ----------------

        col4, col5 = st.columns(2)

        with col4:
            with st.container(border=True):
                st.subheader('City Wise Investment')

                pie_chart(investor)

        with col5:
            with st.container(border=True):
                st.subheader('Sector Wise Investment')
                sector_pie(investor)

        # ---------------- Charts Row 2 ----------------

        col6, col7 = st.columns(2)

        with col6:
         with st.container(border=True):
                st.subheader('Biggest Investments')
                bar_biggest(investor)

        with col7:
            with st.container(border=True):
                st.subheader('Stage Wise Pie Chart')
                stage_pie(investor)



        with st.container(border=True):
            st.subheader('YoY Investment Trend')

            yoy_investment_graph(investor)


        with st.container(border=True):
            st.subheader('Similar Investor on the basis of Tech ')
            similar_investor(investor)
