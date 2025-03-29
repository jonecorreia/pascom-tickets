import streamlit as st
import cv2
import numpy as np
import os
import json
from datetime import datetime
from PIL import Image
from camera_input_live import camera_input_live
from app_config import CREDITO, STATUS_CORES

st.set_page_config(page_title="📱 Vendas Mobile", page_icon="📱", layout="centered")

# Configuração inicial
data_path = "data/tickets_control.json"


st.caption(CREDITO)
