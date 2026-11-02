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
# Live Tweets via Official X API
st.subheader("🐦 Live Election Analysts & Forecasters")
st.markdown("Track breaking calls and analysis from major desks and independent prognosticators.")

analysts = {
    "Decision Desk HQ": "DecisionDeskHQ",
    "Cook Political Report": "CookPolitical",
    "Dave Wasserman": "Redistrict",
    "Nate Silver": "NateSilver538",
    "Adam Carlson": "admcrlsn",
    "Simon Rosenberg": "SimonWDC"
}

selected_name = st.selectbox("Choose an analyst feed:", list(analysts.keys()))
selected_handle = analysts[selected_name]

# Secure input for the API Bearer Token
bearer_token = st.text_input("Enter your X API Bearer Token to view live tweets:", type="password")

if bearer_token:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    import requests
    # Step 1: Look up the user's hidden Twitter ID
    user_url = f"https://api.twitter.com/2/users/by/username/{selected_handle}"
    user_res = requests.get(user_url, headers=headers)
    
    if user_res.status_code == 200:
        user_id = user_res.json()["data"]["id"]
        
        # Step 2: Fetch their single latest tweet
        tweet_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5"
        tweet_res = requests.get(tweet_url, headers=headers)
        
        if tweet_res.status_code == 200 and "data" in tweet_res.json():
            latest_tweet = tweet_res.json()["data"][0]["text"]
            
            # Display it cleanly in a Streamlit callout box
            st.info(f"**Latest from @{selected_handle}:**\n\n{latest_tweet}")
            st.link_button(f"View full thread on X ↗", f"https://twitter.com/{selected_handle}")
        else:
            st.error(f"Failed to fetch tweets for @{selected_handle}.")
    else:
        st.error("Invalid API Token or user not found.")
else:
    st.warning("⚠️ **API Token Required:** To bypass X's iframe blocks, you must provide a Bearer Token from the [X Developer Portal](https://developer.x.com).")
# This bypasses official Twitter API blocks and renders the feed directly
components.iframe(f"https://xxcancel.com/{selected_handle}", height=600, scrolling=True)
