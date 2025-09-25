import streamlit as st
import pandas as pd
import json
from src.db import DB

st.title("Candidate Dashboard")
st.write("View all candidates stored in the system, including availability details.")

db = DB()
records = db.get_all_candidates()

if not records:
    st.info("No candidates have been uploaded yet.")
else:
    # Parse availability JSON into human-readable strings
    for r in records:
        try:
            avail = json.loads(r.get("availability") or "{}")
            days = ", ".join(avail.get("days", [])) if avail.get("days") else "n/a"
            times = ", ".join(avail.get("times", [])) if avail.get("times") else "n/a"
            r["availability_days"] = days
            r["availability_times"] = times
        except Exception:
            r["availability_days"] = "n/a"
            r["availability_times"] = "n/a"

    # Build a DataFrame for display
    df = pd.DataFrame(records)[
        ["id", "name", "email", "phone", "city", "state",
         "pay_min", "pay_max", "availability_days", "availability_times"]
    ]

    st.dataframe(df, use_container_width=True)

    st.markdown("### Candidate Resumes")
    for r in records:
        with st.expander(f"{r['name']} ({r['city']}, {r['state']})"):
            st.write(f"**Email:** {r['email']} | **Phone:** {r['phone']}")
            st.write(f"**Expected Pay:** ${r['pay_min']:.0f} – ${r['pay_max']:.0f}/hr")
            st.write(f"**Availability:** {r['availability_days']} | {r['availability_times']}")
            if r.get("resume_excerpt"):
                st.markdown("**Resume Preview:**")
                st.write(r["resume_excerpt"][:800] + "...")
            if r.get("resume_path"):
                with open(r["resume_path"], "rb") as f:
                    st.download_button(
                        "Download Resume PDF",
                        data=f.read(),
                        file_name=r["resume_path"].split("/")[-1]
                    )
