import sys
import os
import json
import time
import traceback

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
    get_cache_statistics,
    cache_health_check
)

from app.utils.config import (
    AI_REQUEST_COOLDOWN,
    MAX_CHAT_HISTORY,
    APP_TITLE,
    COMPANY_NAME,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    get_total_available_keys
)


st.set_page_config(
    page_title=APP_TITLE,
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
        font-size: 30px;
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


@st.cache_resource
def initialize_runtime_resources():

    return {
        "initialized": True
    }


initialize_session()

initialize_runtime_resources()


def safe_dataframe(data):

    try:

        if data is None:

            return pd.DataFrame()

        dataframe = pd.DataFrame(data)

        if dataframe.empty:

            return pd.DataFrame()

        return dataframe

    except Exception:

        return pd.DataFrame()


def safe_numeric_conversion(
    dataframe,
    columns
):

    try:

        for column in columns:

            if column in dataframe.columns:

                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="coerce"
                ).fillna(0)

        return dataframe

    except Exception:

        return dataframe


def safe_plotly_chart(figure):

    try:

        st.plotly_chart(
            figure,
            width="stretch"
        )

    except Exception as error:

        st.warning(
            f"Visualization unavailable: {str(error)}"
        )


def sanitize_ai_response(response):

    if not response:

        return (
            "AI response unavailable."
        )

    response = str(response).strip()

    blocked_patterns = [

        "resource_exhausted",

        "quota",

        "429",

        "503",

        "404",

        "model not found",

        "rate limit"
    ]

    for pattern in blocked_patterns:

        if pattern in response.lower():

            return (
                "AI service temporarily unavailable. Please retry shortly."
            )

    return response


def load_fallback_data():

    try:

        with open(
            "app/data/sample_data.json",
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


@st.cache_data(ttl=1800)
def load_channel_data(channel_name):

    try:

        handle = CHANNELS.get(
            channel_name
        )

        if not handle:

            return [], pd.DataFrame()

        channel_id = get_channel_id(
            handle
        )

        if not channel_id:

            fallback = load_fallback_data()

            enriched = enrich_video_metrics(
                fallback
            )

            return (
                enriched,
                safe_dataframe(enriched)
            )

        videos = get_latest_videos(
            channel_id
        )

        if not videos:

            videos = load_fallback_data()

        enriched_videos = enrich_video_metrics(
            videos
        )

        dataframe = safe_dataframe(
            enriched_videos
        )

        return (
            enriched_videos,
            dataframe
        )

    except Exception:

        fallback = load_fallback_data()

        enriched = enrich_video_metrics(
            fallback
        )

        return (
            enriched,
            safe_dataframe(enriched)
        )


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

    try:

        benchmark = (
            get_competitor_channels_data()
        )

        return build_competitive_summary(
            benchmark
        )

    except Exception:

        return []


st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
    width=90
)

st.sidebar.title(
    COMPANY_NAME
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

cache_health = cache_health_check()

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### Runtime Intelligence"
)

st.sidebar.metric(
    "Cache Entries",
    cache_stats.get(
        "active_entries",
        0
    )
)

st.sidebar.metric(
    "Tracked Channels",
    len(CHANNELS)
)

st.sidebar.metric(
    "Competitors",
    len(COMPETITOR_CHANNELS)
)

st.sidebar.metric(
    "Gemini API Keys",
    get_total_available_keys()
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### AI Runtime Health"
)

st.sidebar.info(
    f"Primary Model: {PRIMARY_MODEL}"
)

st.sidebar.info(
    f"Fallback Model: {FALLBACK_MODEL}"
)

st.sidebar.info(
    "Multi-Key Rotation Active"
)

st.sidebar.info(
    "Autonomous Retry Engine Active"
)

if not cache_health.get(
    "healthy",
    True
):

    st.sidebar.warning(
        "Cache utilization is high."
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

df = safe_numeric_conversion(
    df,
    numeric_columns
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

top_video = {}

worst_video = {}

try:

    if not df.empty:

        sorted_df = df.sort_values(
            by="performance_score",
            ascending=False
        )

        if len(sorted_df) > 0:

            top_video = (
                sorted_df.iloc[0]
                .to_dict()
            )

            worst_video = (
                sorted_df.iloc[-1]
                .to_dict()
            )

except Exception:

    pass


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
        f"""
        <div class="section-title">
        {APP_TITLE}
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

        <p><strong>Top Video:</strong> {top_video.get('title', 'Unavailable')}</p>

        <p><strong>Performance Score:</strong> {top_video.get('performance_score', 0)}</p>

        <p><strong>Momentum:</strong> {top_video.get('momentum_classification', 'Unavailable')}</p>

        </div>
        """,
        unsafe_allow_html=True
    )

with alert2:

    st.markdown(
        f"""
        <div class="custom-card">

        <h3>Operational Risk</h3>

        <p><strong>Weakest Video:</strong> {worst_video.get('title', 'Unavailable')}</p>

        <p><strong>Performance Score:</strong> {worst_video.get('performance_score', 0)}</p>

        <p><strong>Retention Signal:</strong> {worst_video.get('estimated_retention_signal', 'Unavailable')}</p>

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

    st.dataframe(
        safe_dataframe(
            [channel_summary]
        ),
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

            thumbnail = video.get(
                "thumbnail",
                ""
            )

            if thumbnail:

                st.image(
                    thumbnail,
                    width="stretch"
                )

            st.markdown(
                f"**{video.get('title', 'Unknown')}**"
            )

            st.caption(
                f"Views: {video.get('views', 0):,}"
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

    safe_plotly_chart(fig1)

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

    safe_plotly_chart(fig2)

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

    safe_plotly_chart(fig3)

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

    safe_plotly_chart(fig4)


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

        if st.button(
            "Generate AI Report",
            width="stretch"
        ):

            with st.spinner(
                "Generating AI operational intelligence report..."
            ):

                try:

                    generated_report = (
                        generate_channel_report(
                            selected_channel,
                            enriched_videos
                        )
                    )

                    generated_report = (
                        sanitize_ai_response(
                            generated_report
                        )
                    )

                    st.session_state.generated_reports[
                        report_key
                    ] = generated_report

                    st.success(
                        "AI report generated successfully."
                    )

                    time.sleep(1)

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"AI Report Error: {str(error)}"
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

                    timestamp = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                    pdf_file = (
                        f"{selected_channel}_{timestamp}.pdf"
                    )

                    final_pdf = export_to_pdf(
                        report,
                        pdf_file,
                        selected_channel
                    )

                    st.success(
                        "PDF generated successfully."
                    )

                    with open(
                        final_pdf,
                        "rb"
                    ) as pdf:

                        st.download_button(
                            label="Download PDF",
                            data=pdf,
                            file_name=os.path.basename(
                                final_pdf
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

                    timestamp = datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )

                    docx_file = (
                        f"{selected_channel}_{timestamp}.docx"
                    )

                    final_docx = export_to_docx(
                        report,
                        docx_file,
                        selected_channel
                    )

                    st.success(
                        "DOCX generated successfully."
                    )

                    with open(
                        final_docx,
                        "rb"
                    ) as docx:

                        st.download_button(
                            label="Download DOCX",
                            data=docx,
                            file_name=os.path.basename(
                                final_docx
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

            if (
                report_key
                in
                st.session_state.generated_reports
            ):

                del st.session_state.generated_reports[
                    report_key
                ]

            st.success(
                "AI report cache cleared."
            )

            time.sleep(1)

            st.rerun()


with benchmark_tab:

    st.subheader(
        "Competitive Benchmark Intelligence"
    )

    try:

        benchmark_data = (
            load_benchmark_data()
        )

        benchmark_df = safe_dataframe(
            benchmark_data
        )

        if benchmark_df.empty:

            st.warning(
                "Competitive benchmark data unavailable."
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

                benchmark_df = safe_numeric_conversion(
                    benchmark_df,
                    ["subscribers"]
                )

                benchmark_df = benchmark_df.dropna(
                    subset=["subscribers"]
                )

                if benchmark_df.empty:

                    st.warning(
                        "No valid benchmark subscriber data."
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
                        template="plotly_dark"
                    )

                    safe_plotly_chart(
                        benchmark_chart
                    )

    except Exception as error:

        st.error(
            f"Benchmark Intelligence Error: {str(error)}"
        )


with assistant_tab:

    st.subheader(
        "Autonomous AI Media Strategist"
    )

    st.caption(
        "AI-powered operational intelligence assistant for strategic YouTube analytics."
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

        current_time = time.time()

        cooldown_remaining = (

            AI_REQUEST_COOLDOWN
            -
            (
                current_time
                -
                st.session_state.last_ai_request
            )
        )

        if cooldown_remaining > 0:

            st.warning(
                f"AI cooldown active. Please wait {int(cooldown_remaining)} seconds."
            )

            st.stop()

        st.session_state.last_ai_request = (
            current_time
        )

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_question,
                "timestamp": str(
                    datetime.now()
                )
            }
        )

        st.session_state.chat_history = (
            st.session_state.chat_history[
                -min(
                    MAX_CHAT_HISTORY,
                    10
                ):
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

                    ai_response = result.get(
                        "response",
                        "No AI response generated."
                    )

                    ai_response = sanitize_ai_response(
                        ai_response
                    )

                    detected_intent = result.get(
                        "intent",
                        "general_analysis"
                    )

                    st.caption(
                        f"Detected Intent: {detected_intent}"
                    )

                    st.markdown(
                        ai_response
                    )

                except Exception as error:

                    ai_response = (
                        f"AI Agent Error: {str(error)}"
                    )

                    st.error(
                        ai_response
                    )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": ai_response,
                "timestamp": str(
                    datetime.now()
                )
            }
        )

    if st.session_state.chat_history:

        if st.button(
            "Clear Conversation",
            width="stretch"
        ):

            st.session_state.chat_history = []

            time.sleep(1)

            st.rerun()


st.markdown("---")

st.caption(
    "Built by Ishan Kaushik | Autonomous AI Media Intelligence Platform"
)