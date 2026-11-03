import streamlit as st
import pandas as pd
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, time
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(page_title="2026 Election Dashboard", layout="wide", page_icon="🗳️")

st.title("🗳️ 2026 Election Tracker Dashboard")
st.markdown("Live updates from major forecasters, state election portals, wire service feeds, Bluesky analysts, and Reddit megathreads.")

# Auto-refresh logic (starts at 5:00 PM local time)
now = datetime.now()
refresh_start_time = time(17, 0)

if now.time() >= refresh_start_time:
    st.success("🔴 **Live Update Mode Active** (Auto-refreshing every 60 seconds)")
    st_autorefresh(interval=60000, key="data_refresh")
else:
    st.warning("⏳ *Live minute-by-minute auto-refresh will begin at 5:00 PM.*")

# ---------------------------------------------------------
# 1. Forecasters Table
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 2. Live Wire Service & Election Headlines (Google News RSS)
# ---------------------------------------------------------
st.subheader("📰 Live Wire & Election Night Headlines")
st.caption("Pulled dynamically via free Google News RSS search operators (AP, Reuters, NPR, PBS).")

wire_queries = {
    "Associated Press (AP)": 'site:apnews.com ("Senate" OR "House" OR "Election") when:1d',
    "Reuters Election Wire": 'site:reuters.com ("U.S. Senate" OR "U.S. House" OR "midterm" OR "election") when:1d',
    "NPR & PBS Politics": '(site:npr.org OR site:pbs.org) ("Senate" OR "House" OR "election results") when:1d'
}

wire_cols = st.columns(3)
rss_headers = {"User-Agent": "Mozilla/5.0 (compatible; ElectionDashboard/1.0)"}

for idx, (source_label, query_str) in enumerate(wire_queries.items()):
    with wire_cols[idx]:
        st.markdown(f"#### {source_label}")
        try:
            encoded_q = urllib.parse.quote_plus(query_str)
            rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-US&gl=US&ceid=US:en"
            resp = requests.get(rss_url, headers=rss_headers, timeout=6)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                items = root.findall(".//item")
                if items:
                    for item in items[:4]:
                        title = item.find("title").text if item.find("title") is not None else "Headline"
                        link = item.find("link").text if item.find("link") is not None else "#"
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                        st.markdown(f"• [{title}]({link})")
                        if pub_date:
                            st.caption(f"🕒 {pub_date[:22]}")
                else:
                    st.info("No new wire items in the last 24 hours.")
            else:
                st.warning(f"Wire feed returned HTTP {resp.status_code}")
        except Exception:
            st.error("Unable to parse RSS feed.")

st.divider()

# ---------------------------------------------------------
# 3. Live Wikipedia Election Page Edit Tracker
# ---------------------------------------------------------
st.subheader("📝 Live Wikipedia Race Table Updates")
st.caption("Tracks real-time editor updates to the 2026 U.S. Senate and House Wikipedia pages as calls are made.")

wiki_pages = {
    "2026 U.S. Senate Elections": "2026_United_States_Senate_elections",
    "2026 U.S. House Elections": "2026_United_States_House_of_Representatives_elections"
}

wiki_cols = st.columns(2)
wiki_headers = {"User-Agent": "StreamlitElectionTracker/1.0 (https://streamlit.io)"}

for idx, (label, page_title) in enumerate(wiki_pages.items()):
    with wiki_cols[idx]:
        st.markdown(f"#### {label}")
        try:
            wiki_api = (
                f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions"
                f"&titles={page_title}&rvlimit=3&rvprop=timestamp|comment|user&format=json"
            )
            w_res = requests.get(wiki_api, headers=wiki_headers, timeout=5)
            if w_res.status_code == 200:
                pages = w_res.json().get("query", {}).get("pages", {})
                for _, pdata in pages.items():
                    revs = pdata.get("revisions", [])
                    for rev in revs:
                        ts = rev.get("timestamp", "")[:16].replace("T", " ")
                        comment = rev.get("comment", "Table update") or "Updated section"
                        st.markdown(f"• **`{ts} UTC`** — {comment[:120]}")
            else:
                st.warning("Wikipedia API temporarily unavailable.")
        except Exception:
            st.error("Error fetching Wikipedia revisions.")

st.divider()

# ---------------------------------------------------------
# 4. Secretary of State Portals
# ---------------------------------------------------------
st.subheader("🏛️ Battleground Secretary of State Result Portals")
sos_links = {
    "Pennsylvania": "https://www.electionreturns.pa.gov/",
    "Michigan": "https://miboecfr.nictusa.com/",
    "Wisconsin": "https://elections.wi.gov/",
    "Arizona": "https://results.arizona.vote/",
    "Nevada": "https://silverstateelection.nv.gov/",
    "Georgia": "
