from io import BytesIO

def create_ui():
    try:
        import streamlit as st
    except Exception as e:
        raise ImportError('streamlit not available: ' + str(e))
    try:
        from reportlab.pdfgen import canvas
    except Exception as e:
        raise ImportError('reportlab not available: ' + str(e))
    st.title('Minimal Streamlit App')
    if st.button('Show sample data'):
        st.write({'hello': 'world'})
    if st.button('Generate PDF'):
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, 'Sample PDF from ReportLab')
        c.showPage(); c.save(); buffer.seek(0)
        st.download_button('Download PDF', buffer, file_name='sample.pdf', mime='application/pdf')

if __name__ == '__main__':
    create_ui()
