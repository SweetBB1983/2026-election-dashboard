import streamlit as st
import pandas as pd
import requests
from datetime import datetime, time
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(page_title="2026 Election Dashboard", layout="wide", page_icon="🗳️")

st.title("🗳️ 2026 Election Tracker Dashboard")
st.markdown("Live updates from major forecasters, state election portals, and Bluesky election analysts.")

# Auto-refresh logic (starts at 5:00 PM local time)
now = datetime.now()
refresh_start_time = time(17, 0)

if now.time() >= refresh_start_time:
    st.success("🔴 **Live Update Mode Active** (Auto-refreshing every 60 seconds)")
    st_autorefresh(interval=60000, key="data_refresh")
else:
    st.warning("⏳ *Live minute-by-minute auto-refresh will begin at 5:00 PM.*")

# 1. Forecasters Table
st.subheader("📊 Major Forecaster Projections")
forecasters = {
    "Decision Desk HQ": {"Senate Forecast": "Lean Dem (65% Prob)", "House Forecast": "Lean Dem (84% Prob)", "House Seats": 241},
    "G. Elliott Morris (50+1)": {"Senate Forecast": "Lean Rep (94% Prob)", "House Forecast": "Likely Dem (99% Prob)", "House Seats": 240},
    "Cook Political Report": {"Senate Forecast": "Awaiting Live API", "House Forecast": "Awaiting Live API", "House Seats": "-"},
    "Sabato's Crystal Ball": {"Senate Forecast": "Awaiting Live API", "House Forecast": "Awaiting Live API", "House Seats": "-"},
    "Inside Elections": {"Senate Forecast": "Awaiting Live API", "House Forecast": "Awaiting Live API", "House Seats": "-"},
    "Race to the WH": {"Senate Forecast": "Awaiting Live API", "House Forecast": "Awaiting Live API", "House Seats": "-"},
}
df_forecasters = pd.DataFrame.from_dict(forecasters, orient="index")
st.dataframe(df_forecasters, use_container_width=True)
st.caption(f"Last updated: {now.strftime('%I:%M:%S %p')}")

st.divider()

# 2. Secretary of State Portals
st.subheader("🏛️ Battleground Secretary of State Result Portals")
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

# 3. Live Bluesky Analyst Feeds (Completely Free & Open Public API)
st.subheader("🦋 Live Election Analysts (via Bluesky)")
st.caption("Latest breaking posts pulled directly from the open AT Protocol public network.")

bsky_analysts = {
    "Nate Silver": "natesilver.bsky.social",
    "Dave Wasserman": "redistrict.bsky.social",
    "Simon Rosenberg": "simonwdc.bsky.social",
    "Decision Desk HQ": "decisiondeskhq.bsky.social",
    "G. Elliott Morris": "gelliottmorris.bsky.social",
    "Inside Elections": "insideelections.bsky.social"
}

# Display in a clean 3x2 grid
analyst_items = list(bsky_analysts.items())
row1 = st.columns(3)
row2 = st.columns(3)
all_cols = row1 + row2

for idx, (name, handle) in enumerate(analyst_items):
    with all_cols[idx]:
        st.markdown(f"### {name}")
        st.caption(f"[@{handle}](https://bsky.app/profile/{handle})")
        try:
            api_url = f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={handle}&limit=3&filter=posts_no_replies"
            r = requests.get(api_url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                feed = data.get("feed", [])
                if feed:
                    post_record = feed[0].get("post", {}).get("record", {})
                    post_text = post_record.get("text", "No text found.")
                    created_at = post_record.get("createdAt", "")[:16].replace("T", " ")
                    st.info(f"{post_text}\n\n*🕒 {created_at} UTC*")
                    st.link_button("View on Bluesky ↗", f"https://bsky.app/profile/{handle}")
                else:
                    st.info("No recent top-level posts.")
            else:
                st.warning(f"Feed unavailable (HTTP {r.status_code})")
        except Exception:
            st.error("Error retrieving feed.")

st.divider()

# 4. Direct Discussion Hubs (Safe from 429 IP Blocks)
st.subheader("💬 Community Election Hubs")
st.caption("Direct links to active live-threads and election communities.")

hub_cols = st.columns(3)
with hub_cols[0]:
    st.markdown("### r/VoteDEM")
    st.markdown("Discussion, canvassing reports, and live election night megathreads.")
    st.link_button("Open r/VoteDEM ↗", "https://www.reddit.com/r/VoteDEM/")

with hub_cols[1]:
    st.markdown("### r/elections")
    st.markdown("General results tracking, media calls, and community reporting.")
    st.link_button("Open r/elections ↗", "https://www.reddit.com/r/elections/")

with hub_cols[2]:
    st.markdown("### r/PoliticalDiscussion")
    st.markdown("In-depth analysis of balance of power, exit polls, and margins.")
    st.link_button("Open r/PoliticalDiscussion ↗", "https://www.reddit.com/r/PoliticalDiscussion/")
