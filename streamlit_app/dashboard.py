import sys
import os
import json
import time

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px

from app.services.youtube_service import (
    CHANNELS,
    COMPETITOR_CHANNELS,
    get_channel_id,
    get_latest_videos,
    get_competitor_channels_data,
    build_competitive_summary
)

from app.analytics.metrics_engine import (
    enrich_video_metrics,
    calculate_channel_health_score,
    classify_channel_health,
    generate_channel_summary
)

from app.agents.report_generator import (
    generate_channel_report
)

from app.agents.agent_router import (
    route_user_query
)

from app.utils.report_exporter import (
    export_to_docx,
    export_to_pdf
)

from app.utils.cache_manager import (
    get_cache_statistics
)

from app.utils.config import (
    AI_REQUEST_COOLDOWN,
    MAX_CHAT_HISTORY
)


st.set_page_config(
    page_title="MoveUp Media AI Ops Platform",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>

    .main {
        background-color: #0E1117;
    }

    .stMetric {
        background-color: #1A1D24;
        padding: 15px;
        border-radius: 14px;
        border: 1px solid #262730;
    }

    .custom-card {
        background-color: #1A1D24;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #262730;
        margin-bottom: 15px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .small-text {
        color: #B0B3B8;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


def initialize_session():

    defaults = {
        "chat_history": [],
        "generated_reports": {},
        "last_ai_request": 0,
        "benchmark_loaded": False
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


initialize_session()


def load_fallback_data():

    try:

        with open(
            "data/sample_data.json",
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data

    except Exception:

        return []


@st.cache_data(ttl=1800)
def load_channel_data(channel_name):

    try:

        handle = CHANNELS[channel_name]

        channel_id = get_channel_id(
            handle
        )

        videos = get_latest_videos(
            channel_id
        )

        if not videos:

            videos = load_fallback_data()

        enriched_videos = enrich_video_metrics(
            videos
        )

        df = pd.DataFrame(
            enriched_videos
        )

        return enriched_videos, df

    except Exception:

        fallback = load_fallback_data()

        enriched_videos = enrich_video_metrics(
            fallback
        )

        df = pd.DataFrame(
            enriched_videos
        )

        return enriched_videos, df


@st.cache_data(ttl=1800)
def load_all_channels():

    all_channel_data = {}

    for channel_name in CHANNELS.keys():

        videos, _ = load_channel_data(
            channel_name
        )

        all_channel_data[
            channel_name
        ] = videos

    return all_channel_data


@st.cache_data(ttl=3600)
def load_benchmark_data():

    benchmark = get_competitor_channels_data()

    return build_competitive_summary(
        benchmark
    )


st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
    width=80
)

st.sidebar.title(
    "MoveUp Media"
)

st.sidebar.caption(
    "AI Content Operations Platform"
)

st.sidebar.markdown("---")

selected_channel = st.sidebar.selectbox(
    "Select Channel",
    list(CHANNELS.keys())
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### Platform Status"
)

st.sidebar.success(
    "YouTube API Connected"
)

st.sidebar.success(
    "Autonomous AI Agent Active"
)

st.sidebar.success(
    "Analytics Engine Running"
)

st.sidebar.success(
    "Export System Ready"
)

cache_stats = get_cache_statistics()

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### Runtime Intelligence"
)

st.sidebar.metric(
    "Cache Entries",
    cache_stats["active_entries"]
)

st.sidebar.metric(
    "Tracked Channels",
    len(CHANNELS)
)

st.sidebar.metric(
    "Competitors",
    len(COMPETITOR_CHANNELS)
)

all_channel_data = load_all_channels()

enriched_videos, df = load_channel_data(
    selected_channel
)

if df.empty:

    st.error(
        "No analytics data available."
    )

    st.stop()

numeric_columns = [
    "views",
    "likes",
    "comments",
    "engagement_rate",
    "performance_score",
    "views_per_day"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column]
        )

channel_health_score = (
    calculate_channel_health_score(
        enriched_videos
    )
)

channel_health = (
    classify_channel_health(
        channel_health_score
    )
)

channel_summary = (
    generate_channel_summary(
        enriched_videos
    )
)

top_video = df.sort_values(
    by="performance_score",
    ascending=False
).iloc[0]

worst_video = df.sort_values(
    by="performance_score"
).iloc[0]

col_logo, col_title = st.columns(
    [1, 8]
)

with col_logo:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
        width=70
    )

with col_title:

    st.markdown(
        """
        <div class="section-title">
        MoveUp Media AI Operations Intelligence Platform
        </div>

        <div class="small-text">
        Enterprise-grade autonomous YouTube analytics, operational intelligence, and AI-driven media optimization platform.
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

metric1, metric2, metric3, metric4, metric5 = st.columns(5)

metric1.metric(
    "Channel Health",
    channel_health
)

metric2.metric(
    "Health Score",
    round(channel_health_score, 2)
)

metric3.metric(
    "Total Views",
    f"{int(df['views'].sum()):,}"
)

metric4.metric(
    "Avg Engagement",
    f"{round(df['engagement_rate'].mean(), 2)}%"
)

metric5.metric(
    "Strong Videos",
    len(
        df[
            df["classification"] == "Strong"
        ]
    )
)

st.markdown("---")

alert1, alert2 = st.columns(2)

with alert1:

    st.markdown(
        f"""
        <div class="custom-card">

        <h3>Operational Opportunity</h3>

        <p><strong>Top Video:</strong> {top_video['title']}</p>

        <p><strong>Performance Score:</strong> {top_video['performance_score']}</p>

        <p><strong>Momentum:</strong> {top_video['momentum_classification']}</p>

        </div>
        """,
        unsafe_allow_html=True
    )

with alert2:

    st.markdown(
        f"""
        <div class="custom-card">

        <h3>Operational Risk</h3>

        <p><strong>Weakest Video:</strong> {worst_video['title']}</p>

        <p><strong>Performance Score:</strong> {worst_video['performance_score']}</p>

        <p><strong>Retention Signal:</strong> {worst_video['estimated_retention_signal']}</p>

        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

tabs = st.tabs([
    "Executive Overview",
    "Analytics Intelligence",
    "AI Report",
    "Competitive Benchmark",
    "Autonomous AI Assistant"
])

overview_tab = tabs[0]
analytics_tab = tabs[1]
report_tab = tabs[2]
benchmark_tab = tabs[3]
assistant_tab = tabs[4]

with overview_tab:

    st.subheader(
        "Executive Performance Overview"
    )

    summary_df = pd.DataFrame(
        [channel_summary]
    )

    st.dataframe(
        summary_df,
        width="stretch"
    )

    st.markdown("---")

    st.subheader(
        "Latest Uploads"
    )

    thumbnail_cols = st.columns(3)

    for index, video in enumerate(
        enriched_videos[:3]
    ):

        with thumbnail_cols[index]:

            st.image(
                video["thumbnail"],
                width="stretch"
            )

            st.markdown(
                f"**{video['title']}**"
            )

            st.caption(
                f"Views: {video['views']:,}"
            )

    st.markdown("---")

    st.subheader(
        "Top Performing Videos"
    )

    top_videos = df.sort_values(
        by="performance_score",
        ascending=False
    ).head(5)

    st.dataframe(
        top_videos[
            [
                "title",
                "views",
                "engagement_rate",
                "performance_score",
                "classification"
            ]
        ],
        width="stretch"
    )

    st.markdown("---")

    st.subheader(
        "Complete Analytics Dataset"
    )

    st.dataframe(
        df,
        width="stretch"
    )

with analytics_tab:

    st.subheader(
        "Performance Score Analysis"
    )

    fig1 = px.bar(
        df,
        x="title",
        y="performance_score",
        color="classification",
        height=650
    )

    st.plotly_chart(
        fig1,
        width="stretch"
    )

    st.subheader(
        "Engagement Intelligence"
    )

    fig2 = px.line(
        df,
        x="title",
        y="engagement_rate",
        markers=True,
        height=650
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

    st.subheader(
        "Content Classification"
    )

    pie_data = (
        df["classification"]
        .value_counts()
        .reset_index()
    )

    pie_data.columns = [
        "classification",
        "count"
    ]

    fig3 = px.pie(
        pie_data,
        names="classification",
        values="count",
        hole=0.45
    )

    st.plotly_chart(
        fig3,
        width="stretch"
    )

    st.subheader(
        "Views vs Engagement"
    )

    fig4 = px.scatter(
        df,
        x="views",
        y="engagement_rate",
        size="performance_score",
        color="classification",
        hover_data=["title"],
        height=700
    )

    st.plotly_chart(
        fig4,
        width="stretch"
    )

with report_tab:

    st.subheader(
        "AI Operational Intelligence Report"
    )

    report_key = (
        f"report_{selected_channel}"
    )

    report = st.session_state.generated_reports.get(
        report_key
    )

    if not report:

        st.info(
            "AI report not generated yet."
        )

        st.markdown(
            """
Click the button below to generate an enterprise AI operational intelligence report.
"""
        )

        if st.button(
            "Generate AI Report",
            width="stretch"
        ):

            try:

                with st.spinner(
                    "AI operational intelligence engine generating strategic report..."
                ):

                    generated_report = (
                        generate_channel_report(
                            selected_channel,
                            enriched_videos
                        )
                    )

                    if (
                        not generated_report
                        or
                        generated_report.startswith(
                            "Report Generation Error"
                        )
                        or
                        generated_report.startswith(
                            "AI report"
                        )
                    ):

                        st.warning(
                            generated_report
                        )

                    else:

                        st.session_state.generated_reports[
                            report_key
                        ] = generated_report

                        st.success(
                            "AI operational intelligence report generated successfully."
                        )

                        st.rerun()

            except Exception as error:

                st.error(
                    f"AI Report Generation Error: {str(error)}"
                )

    else:

        st.success(
            "AI report loaded successfully."
        )

        st.markdown(
            report
        )

        st.markdown("---")

        export_col1, export_col2 = st.columns(2)

        with export_col1:

            if st.button(
                "Generate PDF Report",
                width="stretch"
            ):

                try:

                    with st.spinner(
                        "Generating enterprise PDF report..."
                    ):

                        timestamp = datetime.now().strftime(
                            "%Y%m%d_%H%M%S"
                        )

                        pdf_file = (
                            f"reports/{selected_channel}_{timestamp}.pdf"
                        )

                        export_to_pdf(
                            report,
                            pdf_file,
                            selected_channel
                        )

                    st.success(
                        "PDF report generated successfully."
                    )

                    with open(
                        pdf_file,
                        "rb"
                    ) as pdf:

                        st.download_button(
                            label="Download PDF",
                            data=pdf,
                            file_name=os.path.basename(
                                pdf_file
                            ),
                            mime="application/pdf",
                            width="stretch"
                        )

                except Exception as error:

                    st.error(
                        f"PDF Export Error: {str(error)}"
                    )

        with export_col2:

            if st.button(
                "Generate DOCX Report",
                width="stretch"
            ):

                try:

                    with st.spinner(
                        "Generating enterprise DOCX report..."
                    ):

                        timestamp = datetime.now().strftime(
                            "%Y%m%d_%H%M%S"
                        )

                        docx_file = (
                            f"reports/{selected_channel}_{timestamp}.docx"
                        )

                        export_to_docx(
                            report,
                            docx_file,
                            selected_channel
                        )

                    st.success(
                        "DOCX report generated successfully."
                    )

                    with open(
                        docx_file,
                        "rb"
                    ) as docx:

                        st.download_button(
                            label="Download DOCX",
                            data=docx,
                            file_name=os.path.basename(
                                docx_file
                            ),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            width="stretch"
                        )

                except Exception as error:

                    st.error(
                        f"DOCX Export Error: {str(error)}"
                    )

        st.markdown("---")

        if st.button(
            "Regenerate AI Report",
            width="stretch"
        ):

            try:

                if (
                    report_key
                    in
                    st.session_state.generated_reports
                ):

                    del st.session_state.generated_reports[
                        report_key
                    ]

                st.success(
                    "AI report cache cleared successfully."
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"AI Regeneration Error: {str(error)}"
                )

with benchmark_tab:

    st.subheader(
        "Competitive Benchmark Intelligence"
    )

    try:

        benchmark_data = load_benchmark_data()

        if not benchmark_data:

            st.warning(
                "Competitive benchmark data is currently unavailable."
            )

        else:

            benchmark_df = pd.DataFrame(
                benchmark_data
            )

            if benchmark_df.empty:

                st.warning(
                    "Competitive benchmark dataframe is empty."
                )

            else:

                st.dataframe(
                    benchmark_df,
                    width="stretch"
                )

                required_columns = [
                    "channel_name",
                    "subscribers"
                ]

                missing_columns = [
                    column
                    for column in required_columns
                    if column not in benchmark_df.columns
                ]

                if missing_columns:

                    st.warning(
                        f"Missing benchmark columns: {missing_columns}"
                    )

                else:

                    benchmark_df[
                        "subscribers"
                    ] = pd.to_numeric(
                        benchmark_df[
                            "subscribers"
                        ],
                        errors="coerce"
                    )

                    benchmark_df = benchmark_df.dropna(
                        subset=["subscribers"]
                    )

                    if benchmark_df.empty:

                        st.warning(
                            "No valid benchmark subscriber data available."
                        )

                    else:

                        benchmark_chart = px.bar(
                            benchmark_df,
                            x="channel_name",
                            y="subscribers",
                            color="channel_name",
                            text_auto=True,
                            height=600,
                            title="Competitive Subscriber Benchmark"
                        )

                        benchmark_chart.update_layout(
                            template="plotly_dark",
                            xaxis_title="Channel",
                            yaxis_title="Subscribers"
                        )

                        st.plotly_chart(
                            benchmark_chart,
                            width="stretch"
                        )

    except Exception as error:

        st.error(
            f"Benchmark Intelligence Error: {str(error)}"
        )

with assistant_tab:

    st.subheader(
        "Autonomous AI Media Strategist"
    )

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    user_question = st.chat_input(
        "Ask strategic operational questions..."
    )

    if user_question:

        user_question = user_question.strip()

    if not user_question:

        st.stop()

    current_time = time.time()

    if (
        current_time
        -
        st.session_state.last_ai_request
    ) < AI_REQUEST_COOLDOWN:

        st.warning(
            "AI request cooldown active. Please wait a few seconds before sending another request."
        )

        st.stop()

        st.session_state.last_ai_request = (
            current_time
        )

        st.session_state.chat_history.append(
            
            {
                "role": "user",
                "content": user_question,
                "timestamp": str(datetime.now())
            }
        )
        
        if len(st.session_state.chat_history) > MAX_CHAT_HISTORY:

            st.session_state.chat_history = (
                st.session_state.chat_history[
                    -MAX_CHAT_HISTORY:
                ]
            )

        with st.chat_message("user"):

            st.markdown(
                user_question
            )

        with st.chat_message("assistant"):

            with st.spinner(
                "Autonomous AI strategist analyzing operational intelligence..."
            ):

                try:

                    result = route_user_query(
                        question=user_question,
                        selected_channel=selected_channel,
                        selected_channel_data=enriched_videos,
                        all_channel_data=all_channel_data
                    )

                    response = result["response"]

                    detected_intent = result["intent"]

                    st.caption(
                        f"Detected Intent: {detected_intent}"
                    )

                    st.markdown(
                        response
                    )

                except Exception as error:

                    response = (
                        f"AI Agent Error: {str(error)}"
                    )

                    st.error(response)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": response,
                "timestamp": str(datetime.now())
            }
        )

    if st.session_state.chat_history:

        if st.button(
            "Clear Conversation",
            width="stretch"
        ):

            st.session_state.chat_history = []

            st.rerun()

st.markdown("---")

st.caption(
    "Built by Ishan Kaushik | Autonomous AI Media Intelligence Platform"
)