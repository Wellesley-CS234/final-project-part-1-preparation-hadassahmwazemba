import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Configuration
st.set_page_config(layout="wide", page_title="Analysis of Page Sizes by Language (2023-2025)")


st.title("Analysis of Page Sizes by Language (2023-2025)")
st.write("By Hadassah Mwazemba")



st.write(
    "This analysis examines the page sizes of WPPCC articles across the most-visited Wikipedia language editions. "
    "It replicates the framework presented in the Wikipedia Climate Analysis paper, "
    "using the DPDP dataset (Feb 2023–Oct 2025), which contains 20,764 articles across 25 languages."
)

st.caption("Meier, F. (2024, May). Using Wikipedia Pageview Data to Investigate Public Interest in Climate Change at a Global Scale. \
     In Proceedings of the 16th ACM Web Science Conference (pp. 365-375).")

#uploading the dataframeS
df = pd.read_csv("data/st01_data.csv")

st.divider()

st.header("Data Used for this Analysis")
st.write("This dataset was produced by identifying WPPCC articles on Wikidata and extracting their corresponding QIDs. \
    These QIDs were then queried through the Wikipedia API to obtain the page size of each article. \
        A preview of the dataset is provided below.")

is_toggle = st.toggle("View data snippet (first 50 rows) ")

if is_toggle:

    df = df.drop(columns=["Unnamed: 0", "Unnamed: 0.1"], errors="ignore")

    st.dataframe(df.head(50))


st.divider()


st.header("Complete Visual Analysis of the Collected Data")
st.write("The graph below shows the top 25 languages according to the size of the articles in the WPCC. \
    The English Wikipedia was used as a baseline and the rest of the languages are ranked in comparison to it. ")




#defining function to get the x-axis labels
def x_axislabels():
    counts = df['lan_full'].value_counts()

    order = counts.index.to_list()

    total = len(df)

    eng_count = int((df['lan_full'] == 'English').sum())

    xticklabels = [f"{lang}\n({(counts[lang] / eng_count * 100):.1f}%)"
        for lang in order
    ]

    return xticklabels

#creating the xlabels
xlabels = x_axislabels()
#st.write(xlabels)


#plotting the boxplot
trace1 = go.Box(
    x=df["lan_full"],
    y=df['pagesize'],
    marker=dict(
        color='navy', size=0.8
               ),
    fillcolor='rgba(0,0,0,0)',
    boxpoints=False, #removing the dots above the box plot
    showwhiskers=False, #removing the long lines
    boxmean=False,
    whiskerwidth=0,
    
)

#plotting the stripplot
trace2 = go.Box(
    x=df["lan_full"],
    y=df["pagesize"],
    boxpoints="all",
    pointpos = 0,
    yaxis= 'y2',
    marker=dict(
        color='navy', size=1
               )
)

#plotting the graphs together
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(trace1)
fig.add_trace(trace2,secondary_y=False)

fig['layout'].update(height = 600, width = 800, xaxis=dict(
      tickmode="array",
      ticktext=xlabels,
      tickvals= list(range(25)),
      tickangle=-45,
    ))

fig.update_layout(showlegend=False)
fig.update_xaxes(title_text="Language")
fig.update_yaxes(title_text="Page Size in Bytes", secondary_y=False)
fig.update_yaxes(range=[0, None])

st.plotly_chart(fig, use_container_width=True)

st.divider()

#analysis no 2
st.header("Analysis of Pagesizes per Language")
st.write("This visualization helps compare the distribution of Wikipedia article \
     page sizes across selected languages.")


#getting a list of the languages
language_df = df['lan_full'].value_counts().reset_index()
language_df.columns = ['lan_full', 'count']
languages = language_df['lan_full'].tolist()


#creating a multi-select box
selected_langs = st.multiselect(
    "Select language(s) to compare",
    options=languages,
    
)

if selected_langs:
    language_data = df[df['lan_full'].isin(selected_langs)].copy() #filtering to get the language

    #creating the box plot
    trace3 = go.Box(
        x=language_data['lan_full'],
        y=language_data['pagesize'],
        boxpoints="all",
        pointpos=0,
        marker=dict(color='blue', size=3)
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace3)

    fig.update_layout(
        height=900,
        width=800,
        xaxis_title="Language",
        yaxis_title="Page Size",
    )
    fig.update_xaxes(tickangle=-90)
    fig.update_xaxes(title_text="Language")
    fig.update_yaxes(title_text="Page Size in Bytes", secondary_y=False)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select at least one language to see the comparison.")    

st.divider()

#analysis 3
st.header("Top 10 Longest Articles per Language")
st.write("The analysis below examines each language individually and returns the top 10 largest articles (by page size in bytes), \
     along with direct links to each article.")

#creating a selectbox
language = st.selectbox("Choose a Language",
            languages)

if language:
    df_filtered = df[df["lan_full"] == language].copy()

    df_filtered = df_filtered.sort_values(by="pagesize", ascending=False)

    top10 = df_filtered.head(10)

    top10_result = top10[['title','pagesize', 'url']].reset_index(drop=True)

    #creating a dataframe that uses a clickable link
    clickable = st.dataframe(
    top10_result,
    column_config={
        "url": st.column_config.LinkColumn()
    }
    )


st.divider()

# analysis no 4
st.header("Article Counts per Language Within Selected Page Size Range")
st.write(
    "Use the slider below to select a page size range (in bytes). "
    "The table and bar chart show how many articles each language has "
    "within that range."
)

# Get overall min and max page sizes
min_pagesize = int(df["pagesize"].min())
max_pagesize = int(df["pagesize"].max())

# Range slider for page size
page_min, page_max = st.slider(
    "Select page size range (in bytes)",
    min_value=min_pagesize,
    max_value=max_pagesize,
    value=(min_pagesize, max_pagesize),
    step=500,
)

# Filtering articles within this range
filtered = df["pagesize"].between(page_min, page_max)
df_range = df[filtered].copy()


# Counting articles per language within the range
range_counts = (
    df_range["lan_full"]
    .value_counts()
    .reset_index()
)

range_counts.columns = ["lan_full", "article_count"]

#making sure all languages are present
all_langs = language_df[["lan_full"]].copy()
summary_counts = all_langs.merge(range_counts, on="lan_full", how="left")
summary_counts["article_count"] = summary_counts["article_count"].fillna(0).astype(int)

# plotting graph
fig_counts = px.bar(
    summary_counts,
    x="lan_full",
    y="article_count",
    color="lan_full",
    title="Number of Articles per Language within Selected Page Size Range",
    labels={
        "lan_full": "Language",
        "article_count": "Number of Articles",
    },
)

fig_counts.update_layout(xaxis_tickangle=-40)

st.plotly_chart(fig_counts, use_container_width=True)