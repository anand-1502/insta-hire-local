import streamlit as st
import json
from src.embeddings import EmbeddingIndex
from src.db import DB
from src.match import filter_and_rank
from src.settings import settings

st.title("Employer Search")
st.write("Describe the role and set your filters to find the best candidates.")

# Init services
db = DB()
index = EmbeddingIndex()

with st.form("search_form"):
    job_text = st.text_area(
        "Job requirement",
        placeholder="e.g., Waiter with 2+ years, POS experience, evenings and weekends"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.text_input("City", value="")
    with col2:
        state = st.text_input("State or region", value="")
    with col3:
        st.text_input("Distance filter (local version)", value="same city", disabled=True)

    st.markdown("**Required availability**")
    req_days = st.multiselect("Days needed", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    req_times = st.multiselect("Time windows", ["morning", "afternoon", "evening", "night"])

    col4, col5 = st.columns(2)
    with col4:
        pay_min = st.number_input("Pay min you can offer ($/hr)", min_value=0.0, value=15.0, step=1.0)
    with col5:
        pay_max = st.number_input("Pay max you can offer ($/hr)", min_value=0.0, value=30.0, step=1.0)

    top_k = st.slider("How many candidates to fetch from vector search before filtering", 10, 200, 50, step=10)
    submitted = st.form_submit_button("Find Candidates")

if submitted:
    if not job_text.strip():
        st.error("Please enter a job requirement.")
        st.stop()

    # Embed query and search Chroma
    ids, scores = index.search(job_text, k=top_k)   # ids are strings now
    if not ids:
        st.warning("No candidates found in the vector store yet. Upload some resumes first.")
        st.stop()

    # Fetch matched candidates by IDs from the DB
    records = db.get_candidates_by_ids([int(x) for x in ids])

    # Apply filters and ranking
    results = filter_and_rank(
        job_text=job_text,
        candidates=records,
        req_city=city,
        req_state=state,
        req_days=req_days,
        req_times=req_times,
        pay_min=float(pay_min),
        pay_max=float(pay_max),
        id_rank=ids,
        id_scores=scores
    )

    st.subheader(f"Top {min(10, len(results))} matches")
    if not results:
        st.info("No candidates matched the filters. Try loosening the pay or availability constraints.")
    else:
        for rank, row in enumerate(results[:10], start=1):
            with st.container(border=True):
                st.markdown(f"### {rank}. {row['name']}")
                st.write(f"Location: {row.get('city','')} {row.get('state','')}")
                st.write(f"Expected pay: ${row.get('pay_min',0):.0f} – ${row.get('pay_max',0):.0f}/hr")
                avail = json.loads(row["availability"]) if row.get("availability") else {"days": [], "times": []}
                st.write(
                    f"Availability: days {', '.join(avail.get('days', [])) or 'n/a'} "
                    f"| times {', '.join(avail.get('times', [])) or 'n/a'}"
                )
                if row.get("resume_excerpt"):
                    with st.expander("Resume preview"):
                        st.write(row["resume_excerpt"])
                if row.get("resume_path"):
                    with open(row["resume_path"], "rb") as f:
                        st.download_button(
                            "Download resume PDF",
                            data=f.read(),
                            file_name=row["resume_path"].split("/")[-1]
                        )
