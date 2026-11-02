import streamlit as st
import pandas as pd
import requests
from datetime import datetime, time
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(page_title="2026 Election Dashboard", layout="wide", page_icon="🗳️")

st.title("🗳️ 2026 Election Tracker Dashboard")
st.markdown("Live updates from major forecasters, state election portals, Bluesky analysts, and Reddit discussions.")

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

# 3. Live Bluesky Analyst Feeds (100% Free Public API, No Token Needed)
st.subheader("🦋 Live Bluesky Analyst Feeds")
st.caption("Direct from the Bluesky AT Protocol public endpoint — completely free and unauthenticated.")

bsky_analysts = {
    "Nate Silver": "natesilver.bsky.social",
    "Dave Wasserman": "redistrict.bsky.social",
    "Simon Rosenberg": "simonwdc.bsky.social",
    "Decision Desk HQ": "decisiondeskhq.bsky.social"
}

bsky_cols = st.columns(len(bsky_analysts))

for idx, (name, handle) in enumerate(bsky_analysts.items()):
    with bsky_cols[idx]:
        st.markdown(f"**{name}**")
        st.caption(f"@{handle}")
        try:
            # Public endpoint: no auth, no tokens
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
                st.warning("Feed currently unavailable.")
        except Exception as e:
            st.error("Error loading feed.")

st.divider()

# 4. Live Reddit Election Hubs (Public JSON, No Token Needed)
st.subheader("💬 Live Reddit Communities")
st.caption("Latest breaking submissions from top election discussion subreddits.")

subreddits = {
    "r/VoteDEM": "VoteDEM",
    "r/elections": "elections",
    "r/PoliticalDiscussion": "PoliticalDiscussion"
}

reddit_cols = st.columns(len(subreddits))

# Custom user-agent prevents Reddit 429 ratelimits on public JSON
headers = {"User-Agent": "ElectionDashboardBot/1.0 (by /u/ElectionObserver)"}

for idx, (sub_title, sub_name) in enumerate(subreddits.items()):
    with reddit_cols[idx]:
        st.markdown(f"**{sub_title}**")
        try:
            url = f"https://www.reddit.com/r/{sub_name}/new.json?limit=3"
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                posts = r.json().get("data", {}).get("children", [])
                for p in posts[:3]:
                    pdata = p.get("data", {})
                    title = pdata.get("title", "Untitled")
                    permalink = f"https://www.reddit.com{pdata.get('permalink', '')}"
                    score = pdata.get("score", 0)
                    comments = pdata.get("num_comments", 0)
                    st.markdown(f"• [{title}]({permalink})")
                    st.caption(f"▲ {score} upvotes | 💬 {comments} comments")
            else:
                st.warning("Subreddit temporarily rate-limited.")
        except Exception:
            st.error("Error loading subreddit.")
