import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image
import time
import random


st.set_page_config(page_title="AERIE Disaster Recovery", layout="wide", page_icon="🚁")


if 'stage' not in st.session_state:
    st.session_state.stage = 0
if 'detections' not in st.session_state:
    st.session_state.detections = []
if 'deployed_uavs' not in st.session_state:
    st.session_state.deployed_uavs = []


API_KEY = "irJ992MWV9T2FmE9pCWL"  
MODEL_ID = "disaster-4303w/1"

@st.cache_resource
def get_roboflow_client():
    return InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key=API_KEY
    )

def detect_disasters(image_path):
    """Run disaster detection using Roboflow model"""
    try:
        client = get_roboflow_client()
        result = client.infer(image_path, model_id=MODEL_ID)
        
        
        st.write("**Debug - API Response:**")
        st.json(result)
        
        return result
    except Exception as e:
        st.error(f"Detection error: {e}")
        return None

def process_detections(result):
    """Convert Roboflow results to our format"""
    if not result or 'predictions' not in result:
        return []
    
    detections = []
    for idx, pred in enumerate(result['predictions']):
        
        detection = {
            'id': idx + 1,
            'class': pred.get('class', pred.get('class_name', 'Unknown')),
            'confidence': pred.get('confidence', 0.0),
            'x': pred.get('x', pred.get('cx', 0)),
            'y': pred.get('y', pred.get('cy', 0)),
            'width': pred.get('width', pred.get('w', 0)),
            'height': pred.get('height', pred.get('h', 0)),
            'zone': ['North', 'Central', 'South'][idx % 3]
        }
        detections.append(detection)
    
    
    detections.sort(key=lambda x: x['confidence'], reverse=True)
    return detections


st.title("🚁 AERIE Swarm Intelligence System")
st.markdown("**Autonomous Emergency Reconnaissance & Resource Integration Ecosystem**")


with st.sidebar:
    st.header("🎮 Mission Control")
    
    
    stages = [
        "Mission Start",
        "VTOL Deployment",
        "AI Detection",
        "GCS Analysis",
        "UAV Assignment",
        "Relief Delivery",
        "Mission Complete"
    ]
    
    st.subheader("Mission Stage")
    progress = st.session_state.stage / (len(stages) - 1)
    st.progress(progress)
    st.info(f"**Stage {st.session_state.stage + 1}:** {stages[st.session_state.stage]}")
    
    st.divider()
    
    
    st.subheader("📊 Swarm Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("VTOLs Active", "3" if st.session_state.stage >= 1 else "0")
    with col2:
        st.metric("UAVs Deployed", len(st.session_state.deployed_uavs))
    
    st.metric("Total Detections", len(st.session_state.detections))
    
    st.divider()
    
    
    st.subheader("⚙️ System Info")
    st.caption("**Flight Controller:** Pixhawk 2.4.8")
    st.caption("**GPS:** Neo M8N")
    st.caption("**AI Model:** Roboflow Custom")
    st.caption("**Data Link:** 915MHz Telemetry")
    
    st.divider()
    
    if st.button("🔄 Reset Mission", use_container_width=True):
        st.session_state.stage = 0
        st.session_state.detections = []
        st.session_state.deployed_uavs = []
        st.rerun()


tab1, tab2, tab3 = st.tabs(["📷 Image Upload & Detection", "🗺️ Mission View", "📊 Analytics"])

with tab1:
    st.header("Image Upload & AI Detection")
    
    if st.session_state.stage == 0:
        st.info("👆 Upload a disaster image to begin reconnaissance mission")
        
        uploaded_file = st.file_uploader(
            "Upload Disaster Zone Image",
            type=['jpg', 'jpeg', 'png'],
            help="Upload an aerial image of a disaster zone"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Disaster Zone", use_container_width=True)
            
            with col2:
                st.subheader("Ready to Deploy")
                st.write("✅ Image loaded")
                st.write("✅ VTOL swarm ready")
                st.write("✅ AI model initialized")
                
                if st.button("🚀 Deploy VTOL Swarm", use_container_width=True, type="primary"):
                    st.session_state.stage = 1
                    
                   
                    with open("temp_disaster_image.jpg", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.rerun()
    
    elif st.session_state.stage == 1:
        st.success("✈️ VTOL drones deployed and scanning zones...")
        
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
            status_text.text(f"Scanning zone... {i+1}% complete")
        
        st.success("✅ Reconnaissance complete! Processing imagery...")
        
        if st.button("🤖 Run AI Detection", type="primary", use_container_width=True):
            st.session_state.stage = 2
            st.rerun()
    
    elif st.session_state.stage == 2:
        st.info("🔍 Running AI disaster detection model...")
        
        with st.spinner("Analyzing imagery with Roboflow model..."):
            
            result = detect_disasters("temp_disaster_image.jpg")
            
            if result:
                st.write("**Raw predictions received:**", len(result.get('predictions', [])))
                
                
                if result.get('predictions'):
                    st.write("**Sample prediction structure:**")
                    st.json(result['predictions'][0])
                
                st.session_state.detections = process_detections(result)
                time.sleep(1)  
                st.success(f"✅ Detected {len(st.session_state.detections)} objects!")
                st.session_state.stage = 3
                st.rerun()
            else:
                st.error("❌ Detection failed. Please check your API key and try again.")
    
    elif st.session_state.stage >= 3:
        
        image = Image.open("temp_disaster_image.jpg")
        st.image(image, caption="Analyzed Disaster Zone", use_container_width=True)
        
        st.success(f"✅ Detection Complete: {len(st.session_state.detections)} objects identified")

with tab2:
    st.header("Mission Coordination View")
    
    if st.session_state.stage >= 3 and st.session_state.detections:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🗺️ Detection Map")
            
            
            image = Image.open("temp_disaster_image.jpg")
            st.image(image, use_container_width=True)
            
            st.caption("Detections overlaid on disaster zone imagery")
        
        with col2:
            st.subheader("🎯 Detected Objects")
            
            for det in st.session_state.detections:
                confidence_color = "🟢" if det['confidence'] > 0.9 else "🟡" if det['confidence'] > 0.8 else "🟠"
                
                with st.expander(f"{confidence_color} {det['class']} - {det['confidence']*100:.1f}%"):
                    st.write(f"**ID:** {det['id']}")
                    st.write(f"**Zone:** {det['zone']}")
                    st.write(f"**Confidence:** {det['confidence']*100:.1f}%")
                    st.write(f"**Position:** ({det['x']:.0f}, {det['y']:.0f})")
        
        
        if st.session_state.stage == 3:
            st.divider()
            if st.button("📡 Analyze at GCS", type="primary", use_container_width=True):
                st.session_state.stage = 4
                st.rerun()
        
        elif st.session_state.stage == 4:
            st.divider()
            st.info("🤖 AI is prioritizing targets by confidence...")
            
            
            all_classes = list(set([d['class'] for d in st.session_state.detections]))
            st.write(f"**Detected classes:** {', '.join(all_classes)}")
            
           
            top_targets = st.session_state.detections[:3]  
            
            if top_targets:
                st.subheader("Priority Targets (Highest Confidence)")
                for i, target in enumerate(top_targets, 1):
                    st.success(f"**UAV-{i}** → {target['class']} ({target['confidence']*100:.1f}%)")
                
                if st.button("🚁 Deploy UAV Swarm", type="primary", use_container_width=True):
                    st.session_state.deployed_uavs = top_targets
                    st.session_state.stage = 5
                    st.rerun()
            else:
                st.warning("⚠️ No targets detected. Please try a different image.")
                if st.button("← Go Back", use_container_width=True):
                    st.session_state.stage = 0
                    st.rerun()
        
        elif st.session_state.stage == 5:
            st.divider()
            st.success("✈️ UAVs en route to priority targets...")
            
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)
                progress_bar.progress(i + 1)
            
            st.success("✅ All relief packages delivered!")
            
            if st.button("✓ Complete Mission", type="primary", use_container_width=True):
                st.session_state.stage = 6
                st.rerun()
        
        elif st.session_state.stage == 6:
            st.balloons()
            st.success("🎉 **MISSION COMPLETE!**")
            st.info(f"**Deliveries:** {len(st.session_state.deployed_uavs)} relief packages")
            st.info(f"**Success Rate:** 100%")

with tab3:
    st.header("Mission Analytics")
    
    if st.session_state.detections:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Detections", len(st.session_state.detections))
        with col2:
            avg_conf = sum(d['confidence'] for d in st.session_state.detections) / len(st.session_state.detections)
            st.metric("Avg Confidence", f"{avg_conf*100:.1f}%")
        with col3:
            st.metric("UAVs Deployed", len(st.session_state.deployed_uavs))
        
        st.divider()
        
        
        st.subheader("Detection Breakdown by Class")
        
        class_counts = {}
        for det in st.session_state.detections:
            class_name = det['class']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        for class_name, count in class_counts.items():
            st.write(f"**{class_name}:** {count}")
        
        st.divider()
        
        
        st.subheader("🎯 Top 3 Highest Confidence Detections")
        top_3 = st.session_state.detections[:3]
        for i, det in enumerate(top_3, 1):
            conf_emoji = "🟢" if det['confidence'] > 0.9 else "🟡" if det['confidence'] > 0.8 else "🟠"
            st.info(f"**#{i}** {conf_emoji} {det['class']} - {det['confidence']*100:.1f}% confidence (Zone: {det['zone']})")
        
        st.divider()
        
        
        st.subheader("Detailed Detections (Sorted by Confidence)")
        
        import pandas as pd
        df = pd.DataFrame(st.session_state.detections)
        df['confidence'] = df['confidence'].apply(lambda x: f"{x*100:.1f}%")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No detections yet. Upload an image to begin.")


st.divider()
st.caption("AERIE Disaster Recovery System | Powered by Roboflow AI | 915MHz Mesh Network")