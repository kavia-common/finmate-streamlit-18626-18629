from io import BytesIO

# PUBLIC_INTERFACE
def create_ui():
    """Render the minimal Streamlit UI with sample data display and PDF generation.

    This is the main entry function invoked by Streamlit. It verifies required
    dependencies are available, renders a simple header, and provides buttons to:
      - show sample data
      - generate and download a PDF using ReportLab
    """
    try:
        import streamlit as st
    except Exception as e:
        # Provide clear feedback when Streamlit is missing
        raise ImportError('streamlit not available: ' + str(e))
    try:
        from reportlab.pdfgen import canvas
    except Exception as e:
        # Provide clear feedback when ReportLab is missing
        raise ImportError('reportlab not available: ' + str(e))

    st.set_page_config(page_title="FinMate Minimal", page_icon="💸")
    st.title('Minimal Streamlit App')

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Show sample data'):
            st.write({'hello': 'world'})
    with col2:
        if st.button('Generate PDF'):
            buffer = BytesIO()
            c = canvas.Canvas(buffer)
            c.drawString(100, 750, 'Sample PDF from ReportLab')
            c.showPage()
            c.save()
            buffer.seek(0)
            st.download_button('Download PDF', buffer, file_name='sample.pdf', mime='application/pdf')

if __name__ == '__main__':
    # Running directly (useful for local dev): streamlit will still handle this file
    create_ui()
