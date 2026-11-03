import time as pytime
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(page_title="2026 Election Dashboard", layout="wide", page_icon="🗳️")

st.title("🗳️ 2026 Election Tracker Dashboard")
st.markdown("Live updates from major forecasters, state election portals, wire service feeds, Bluesky analysts, and Reddit megathreads.")

# ---------------------------------------------------------
# Timezone & Auto-Refresh Controls (No External Component Needed)
# ---------------------------------------------------------
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])

with ctrl_col1:
    tz_label = st.selectbox(
        "Dashboard Timezone:",
        ["US/Eastern", "US/Central", "US/Mountain", "US/Pacific"],
        index=0
    )

current_tz = ZoneInfo(tz_label)
now = datetime.now(current_tz)
refresh_start_time = time(17, 0)  # 5:00 PM in selected timezone

with ctrl_col2:
    force_live = st.checkbox("Force Live 60s Auto-Refresh Now", value=False)

with ctrl_col3:
    if st.button("🔄 Refresh Now"):
        st.rerun()

is_live_mode = force_live or (now.time() >= refresh_start_time)

if is_live_mode:
    st.success(f"🔴 **Live Update Mode Active** — Refreshing automatically every 60 seconds (Current time: {now.strftime('%I:%M:%S %p %Z')})")
else:
    st.warning(f"⏳ *Waiting for 5:00 PM ({tz_label}) to start automatic 60-second updates. Current time: {now.strftime('%I:%M:%S %p %Z')} (Check the box above to start early).*")

# ---------------------------------------------------------
# 1. Forecasters Comparison Table
# ---------------------------------------------------------
st.subheader("📊 Major Forecaster Trackers (2026 Senate & House)")
forecasters = {
    "Decision Desk HQ": {
        "Senate Coverage": "Live Race Calls & Precinct Returns",
        "House Coverage": "All 435 Districts Tracked",
        "Update Feed": "Active via Bluesky & Live Desk"
    },
    "Cook Political Report": {
        "Senate Coverage": "Battleground Race Ratings",
        "House Coverage": "Competitive District Ratings",
        "Update Feed": "Active via Bluesky (@cookpolitical.com)"
    },
    "Sabato's Crystal Ball": {
        "Senate Coverage": " Crystal Ball Senate Ratings",
        "House Coverage": "Crystal Ball House Ratings",
        "Update Feed": "Active via Kyle Kondik (@kkondik.bsky.social)"
    },
    "Inside Elections": {
        "Senate Coverage": "Baseline & Toss-Up Ratings",
        "House Coverage": "District-by-District Handicapping",
        "Update Feed": "Active via Jacob Rubashkin (@rubashkin.bsky.social)"
    },
    "G. Elliott Morris (50+1)": {
        "Senate Coverage": "Probabilistic Senate Model",
        "House Coverage": "Seat Distribution & Generic Ballot",
        "Update Feed": "Active via Bluesky (@gelliottmorris.com)"
    },
    "Race to the WH": {
        "Senate Coverage": "Polling Averages & Win Probabilities",
        "House Coverage": "District Forecast Simulations",
        "Update Feed": "Election Night Model Updates"
    },
}
df_forecasters = pd.DataFrame.from_dict(forecasters, orient="index")
st.dataframe(df_forecasters, use_container_width=True)
st.caption(f"Last updated: {now.strftime('%I:%M:%S %p %Z')}")

st.divider()

# ---------------------------------------------------------
# 2. Live Wire Service & Election Headlines (Google News RSS)
# ---------------------------------------------------------
st.subheader("📰 Live Wire & Election Night Headlines")
st.caption("Pulled dynamically via Google News RSS search operators (AP, Reuters, NPR, PBS).")

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

# ---------------------------------------------------------
# 5. Live Bluesky Analyst Feeds (12 Tracked Prognosticators)
# ---------------------------------------------------------
st.subheader("🦋 Live Election Analysts & Handicappers (via Bluesky)")
st.caption("Latest breaking posts pulled live via Bluesky's free, unauthenticated AT Protocol public API.")

bsky_analysts = {
    "Cook Political Report": "cookpolitical.com",
    "Decision Desk HQ": "decisiondeskhq.bsky.social",
    "Dave Wasserman": "redistrict.bsky.social",
    "Kyle Kondik (Sabato's Crystal Ball)": "kkondik.bsky.social",
    "Geoffrey Skelley (DDHQ)": "geoffreyskelley.com",
    "Jacob Rubashkin (Inside Elections)": "rubashkin.bsky.social",
    "G. Elliott Morris (50+1)": "gelliottmorris.com",
    "Nate Silver": "natesilver.bsky.social",
    "Taniel (Bolts Mag)": "taniel.bsky.social",
    "Adam Carlson": "admcrlsn.bsky.social",
    "Kyle Griffin": "kylegriffin1.bsky.social",
    "Simon Rosenberg": "simonwdc.bsky.social"
}

analyst_items = list(bsky_analysts.items())
cols = st.columns(3)

for idx, (name, handle) in enumerate(analyst_items):
    col = cols[idx % 3]
    with col:
        st.markdown(f"#### {name}")
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
                    st.info("No recent posts found.")
            else:
                st.warning(f"Feed unavailable (HTTP {r.status_code})")
        except Exception:
            st.error("Error retrieving feed.")
        st.write("")

st.divider()

# ---------------------------------------------------------
# 6. Reddit Election Communities & Live Megathreads
# ---------------------------------------------------------
st.subheader("💬 Reddit Election Communities & Live Megathreads")
st.caption("Live thread feeds (via RSS-to-JSON proxy) and direct one-click links to active election hubs.")

reddit_hubs = [
    {
        "title": "r/VoteDEM",
        "sub": "VoteDEM",
        "desc": "Volunteer updates, county reporting, and live Election Day discussion.",
        "sub_url": "https://www.reddit.com/r/VoteDEM/",
        "megathread_label": "Open r/VoteDEM Megathreads ↗",
        "megathread_url": "https://www.reddit.com/r/VoteDEM/hot/"
    },
    {
        "title": "r/fivethirtyeight",
        "sub": "fivethirtyeight",
        "desc": "Polling averages, early vote modeling, and data-driven race calls.",
        "sub_url": "https://www.reddit.com/r/fivethirtyeight/",
        "megathread_label": "Open r/fivethirtyeight Hot Threads ↗",
        "megathread_url": "https://www.reddit.com/r/fivethirtyeight/hot/"
    },
    {
        "title": "r/elections",
        "sub": "elections",
        "desc": "General results tracking, media race calls, and community reporting.",
        "sub_url": "https://www.reddit.com/r/elections/",
        "megathread_label": None,
        "megathread_url": None
    },
    {
        "title": "r/PoliticalDiscussion",
        "sub": "PoliticalDiscussion",
        "desc": "In-depth analysis of national swing, exit polls, and legislative control.",
        "sub_url": "https://www.reddit.com/r/PoliticalDiscussion/",
        "megathread_label": None,
        "megathread_url": None
    }
]

hub_cols = st.columns(4)

for idx, hub in enumerate(reddit_hubs):
    with hub_cols[idx]:
        st.markdown(f"### {hub['title']}")
        st.caption(hub["desc"])

        try:
            rss_target = urllib.parse.quote_plus(f"https://www.reddit.com/r/{hub['sub']}/new.rss")
            proxy_url = f"https://api.rss2json.com/v1/api.json?rss_url={rss_target}"
            r_resp = requests.get(proxy_url, timeout=5)
            if r_resp.status_code == 200 and r_resp.json().get("status") == "ok":
                items = r_resp.json().get("items", [])
                for item in items[:3]:
                    t_title = item.get("title", "Thread")
                    t_link = item.get("link", hub["sub_url"])
                    st.markdown(f"• [{t_title}]({t_link})")
        except Exception:
            pass

        if hub["megathread_url"]:
            st.link_button(hub["megathread_label"], hub["megathread_url"])
        st.link_button(f"Open {hub['title']} ↗", hub["sub_url"])

# ---------------------------------------------------------
# 7. Pure-Python Auto-Refresh Trigger (Runs After Page Renders)
# ---------------------------------------------------------
if is_live_mode:
    pytime.sleep(60)
    st.rerun()
