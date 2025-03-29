import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import numpy as np

class QRCodeProcessor(VideoProcessorBase):
    def __init__(self):
        self.qr_detector = cv2.QRCodeDetector()

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        # Detecta e decodifica o QR code
        data, bbox, _ = self.qr_detector.detectAndDecode(img)
        if bbox is not None and data:
            # Desenha o contorno do QR code
            n_points = len(bbox)
            for j in range(n_points):
                pt1 = tuple(bbox[j][0].astype(int))
                pt2 = tuple(bbox[(j+1) % n_points][0].astype(int))
                cv2.line(img, pt1, pt2, color=(0, 255, 0), thickness=2)
            # Exibe os dados decodificados
            cv2.putText(img, data, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            st.session_state['qr_data'] = data

        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.title("Leitor de QR Code em Tempo Real")

webrtc_ctx = webrtc_streamer(
    key="qr-code-scanner",
    video_processor_factory=QRCodeProcessor,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

if 'qr_data' in st.session_state:
    st.write(f"Dados do QR Code: {st.session_state['qr_data']}")
