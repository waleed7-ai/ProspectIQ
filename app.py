import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from agent import run_agent
from storage import save, all_prospects, get_prospect, update_status

load_dotenv()
st.set_page_config(page_title='ProspectIQ | AI Research', page_icon='🔎', layout='wide')
st.title('🔎 ProspectIQ')
st.caption('Agentic business research • Evidence-based qualification • Human-reviewed outreach')
with st.sidebar:
    st.header('Settings')
    api_key = st.text_input('Gemini API key', type='password')
    model = st.text_input('Model', value=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'))
    st.info('No messages are sent automatically. Research is limited to a URL you approve.')
research, leads = st.tabs(['Research agent', 'Prospect dashboard'])
with research:
    url = st.text_input('Public company website', placeholder='https://example.com')
    if st.button('Run AI research', type='primary'):
        if not api_key:
            st.error('Add your Gemini API key in Settings.')
        elif not url:
            st.error('Enter a website URL.')
        else:
            try:
                with st.spinner('Agent is researching the website...'):
                    report, log = run_agent(url.strip(), api_key, model)
                st.session_state['report'] = report
                st.session_state['log'] = log
                st.session_state['url'] = url.strip()
            except Exception as exc:
                st.error(f'Research failed: {exc}')
    if 'report' in st.session_state:
        r = st.session_state['report']
        c1, c2, c3 = st.columns(3)
        c1.metric('Company', r['company'])
        c2.metric('Sector', r['sector'])
        c3.metric('Lead score', f"{r['score']}/100")
        st.subheader('Company summary')
        st.write(r['summary'])
        st.subheader('Evidence')
        for item in r['evidence']:
            st.write('•', item)
        st.subheader('Potential opportunities')
        
        for i, opportunity in enumerate(r['opportunities'], start=1):
            with st.expander(
                f"Opportunity {i}: {opportunity.get('proposed_solution', 'Untitled')}",
                expanded=True
            ):
                st.markdown("**Business challenge**")
                st.write(opportunity.get('problem', 'Not specified'))

                st.markdown("**Proposed solution**")
                st.write(opportunity.get('proposed_solution', 'Not specified'))

                st.markdown("**Confidence**")
                st.write(opportunity.get('confidence', 'Unknown'))

                st.markdown("**Supporting rationale**")
                st.write(opportunity.get('rationale', 'Not provided'))

        st.caption('Score rationale: ' + str(r['score_reason']))
        st.subheader('Outreach draft — not sent')
        st.text_input('Subject', value=r['subject'])
        st.text_area('Email', value=r['outreach_email'], height=180)
        st.subheader('Limitations')
        st.write(r['limitations'])
        with st.expander('Agent tool activity'):
            st.json(st.session_state['log'])
        if st.button('Approve and save prospect'):
            save(st.session_state['url'], r)
            st.success('Saved locally for review. No email was sent.')
with leads:
    rows = all_prospects()
    if rows:
        df = pd.DataFrame(rows, columns=['Company', 'Website', 'Sector', 'Score', 'Status', 'Created'])
        
        st.subheader("Prospect overview")

        m1, m2, m3 = st.columns(3)

        m1.metric("Total prospects", len(df))
        m2.metric("Average lead score", f"{df['Score'].mean():.0f}/100")
        m3.metric("Needs review", (df['Status'] == 'Needs review').sum())

        st.divider()

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button('Export CSV', df.to_csv(index=False), file_name='prospects.csv', mime='text/csv')

        st.divider()
        st.subheader("Review saved prospect")

        selected_url = st.selectbox(
            "Select a prospect",
            options=df["Website"].tolist(),
            format_func=lambda u: (
                f"{df.loc[df['Website'] == u, 'Company'].iloc[0]} — {u}"
            )
        )

        prospect = get_prospect(selected_url)

        if prospect:
            report = prospect["report"]

            st.markdown(f"### {prospect['company']}")
            st.write(report.get("summary", ""))

            st.markdown("**Research evidence**")
            for evidence in report.get("evidence", []):
                st.write("•", evidence)

            st.markdown("**Outreach draft**")
            st.write(report.get("outreach_email", ""))

            statuses = ["Needs review", "Qualified", "Not qualified"]

            selected_status = st.selectbox(
                "Review status",
                options=statuses,
                index=(
                    statuses.index(prospect["status"])
                    if prospect["status"] in statuses else 0
                )
            )

            if st.button("Save review status"):
                update_status(selected_url, selected_status)
                st.success("Review status updated.")
                st.rerun()

    else:
        st.info('No prospects saved yet. Run a research report first.')
