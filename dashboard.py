import streamlit as st
import pandas as pd
from datetime import datetime, time
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# Page config must be the first Streamlit command
st.set_page_config(page_title="2026 Election Dashboard", layout="wide", page_icon="🗳️")

st.title("🗳️ 2026 Election Tracker Dashboard")
st.markdown("Live updates from major forecasters, Secretary of State links, and Twitter feeds.")

# Auto-refresh logic (starts at 5:00 PM tomorrow)
now = datetime.now()
refresh_start_time = time(17, 0) # 5:00 PM

if now.time() >= refresh_start_time:
    st.success("🔴 **Live Update Mode Active** (Data refreshing every 60 seconds)")
    # Run the autorefresh component (refreshes the whole page every 60000 milliseconds)
    st_autorefresh(interval=60000, key="data_refresh")
else:
    st.warning("⏳ *Live minute-by-minute updates will begin at 5:00 PM.*")

st.subheader("📊 Major Forecaster Projections")

# In a fully connected app, you would use requests.get() to hit APIs here.
forecasters = {
    "Decision Desk HQ": {"Senate Forecast": "Lean Dem (65% Prob)", "House Forecast": "Lean Dem (84% Prob)", "House Seats": 241},
    "G. Elliott Morris (50+1)": {"Senate Forecast": "Lean Rep (94% Prob)", "House Forecast": "Likely Dem (99% Prob)", "House Seats": 240},
    "Cook Political Report": {"Senate Forecast": "Awaiting Live API", "House Forecast": "Awaiting Live API", "House Seats": "-"},
    "Sabato's Crystal Ball": {"Senate Forecast": "Awaiting Live API", "House Forecast": "Awaiting Live API", "House Seats": "-"},
    "Inside Elections": {"Senate Forecast": "Awaiting Live API", "House Forecast": "Awaiting Live API", "House Seats": "-"},
    "Race to the WH": {"Senate Forecast": "Awaiting Live API", "House Forecast": "Awaiting Live API", "House Seats": "-"},
}

df_forecasters = pd.DataFrame.from_dict(forecasters, orient='index')
st.dataframe(df_forecasters, use_container_width=True)
st.caption(f"Last updated: {now.strftime('%I:%M:%S %p')}")

st.divider()

# Secretary of State Links
st.subheader("🏛️ Battleground Secretary of State Result Portals")
st.markdown("Direct links to election authority websites.")

sos_links = {
    "Pennsylvania": "https://www.electionreturns.pa.gov/",
    "Michigan": "https://miboecfr.nictusa.com/",
    "Wisconsin": "https://elections.wi.gov/",
    "Arizona": "https://results.arizona.vote/",
    "Nevada": "https://silverstateelection.nv.gov/",
    "Georgia": "https://results.enr.clarityelections.com/GA/",
    "North Carolina": "https://er.ncsbe.gov/",
    "Ohio": "https://liveresults.ohiosos.gov/",
    "Texas": "https://results.texas-election.com/",
    "Florida": "https://floridaelectionwatch.gov/"
}

cols = st.columns(5)
for i, (state, url) in enumerate(sos_links.items()):
    cols[i % 5].markdown(f"**[{state}]({url})**")

st.divider()

# Twitter / X Embeds via Tabs
st.subheader("🐦 Live Election Analysts & Forecasters")
st.markdown("Track breaking calls and analysis from major desks and independent prognosticators.")

# Create tabs for clean organization
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Decision Desk HQ", 
    "Cook Political Report", 
    "Dave Wasserman", 
    "Nate Silver", 
    "Adam Carlson", 
    "Simon Rosenberg"
])

def embed_twitter(handle, height=600):
    html = f'''
    <a class="twitter-timeline" data-height="{height}" data-theme="light" href="https://twitter.com/{handle}?ref_src=twsrc%5Etfw">Tweets by {handle}</a> 
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    '''
    components.html(html, height=height+20, scrolling=True)

with tab1:
    embed_twitter("DecisionDeskHQ")

with tab2:
    embed_twitter("CookPolitical")

with tab3:
    embed_twitter("Redistrict") # Dave Wasserman's handle

with tab4:
    embed_twitter("NateSilver538")

with tab5:
    embed_twitter("admcrlsn") # Adam Carlson's handle

with tab6:
    embed_twitter("SimonWDC") # Simon Rosenberg's handle
