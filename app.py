import streamlit as st
import conva_ai as ca
import asyncio
import json
import pandas as pd

# Initialize the Conva AI client
client = ca.AsyncConvaAI(
    #use ur credentials here
    assistant_id="", 
    assistant_version="28.0.0", 
    api_key="",
)

# Asynchronous function to retrieve patient details using Conva AI
async def get_patient_details(patient_name):
    try:
        response = await client.invoke_capability(
            f"retrieve patient details for patient name {patient_name}",
            capability_group="PatientInfoGroup"
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

async def get_doctor_details(doctor_name):
    try:
        response = await client.invoke_capability(
            f"retrieve doctor details for doctor name {doctor_name}",
            capability_group="Doctorpatientdet"
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Asynchronous function to retrieve upcoming appointments using Conva AI
async def upcoming_appointments(patient_name):
    try:
        response = await client.invoke_capability(
            f"show all the upcoming appointments for patient with name {patient_name}",
            capability_group="appointment tracker"
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
    
async def upcoming_appointments_doctors(doctor_name):
    try:
        response = await client.invoke_capability(
            f"show all the upcoming appointments for doctor with name {doctor_name}",
            capability_group="appointment tracker"
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

async def past_appointments(patient_name):
    try:
        response = await client.invoke_capability(
            f"show all the past appointments for patient with name {patient_name}",
            capability_group="pastAppointments"
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

async def tests_taken(patient_name):
    try:
        response = await client.invoke_capability(
            f"show tests taken for patient with name {patient_name}",
            capability_group="test information"
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

async def doctor_availability(department_name):
    try:
        response = await client.invoke_capability(
            f"show me the available doctors in the department of {department_name}",
            capability_group="DoctorAvailability"
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Streamlit app structure with enhanced UI
st.set_page_config(page_title="Hospital Management System", layout="wide")

# Sidebar for user selection
st.sidebar.title("Options")
user_type = st.sidebar.selectbox("Are you a Patient or Doctor?", ("Select", "Patient", "Doctor", "Check Availability"))

# Main layout
st.title("🏥 Hospital Management System")

if user_type == "Patient":
    st.header("Patient Portal")
    with st.form(key="patient_form"):
        patient_name = st.text_input("Enter Patient Name")
        submit = st.form_submit_button("Get Patient Information")
    
    if submit and patient_name:
        with st.spinner("Retrieving patient details..."):
            patient_details_response = asyncio.run(get_patient_details(patient_name))
            if patient_details_response:
                patient_info = json.loads(patient_details_response.parameters['patient_information_summary'])
                df = pd.DataFrame(list(patient_info.items()), columns=["Field", "Value"])
                st.subheader("Patient Personal Details and Medical History")
                st.table(df)

        with st.spinner("Retrieving upcoming appointments..."):
            upcoming_appointments_response = asyncio.run(upcoming_appointments(patient_name))
            if upcoming_appointments_response:
                upcoming_appointments_data = json.loads(upcoming_appointments_response.parameters['appointment_summary'])
                upcoming_appointments_df = pd.DataFrame(upcoming_appointments_data)
                st.subheader("Upcoming Appointments")
                st.table(upcoming_appointments_df)

        with st.spinner("Retrieving past appointments..."):
            past_appointments_response = asyncio.run(past_appointments(patient_name))
            if past_appointments_response:
                past_appointments_data = past_appointments_response.parameters['past_appointment_summary_info']
                past_appointments_df = pd.DataFrame(past_appointments_data)
                st.subheader("Past Appointments")
                st.table(past_appointments_df)

        with st.spinner("Retrieving tests taken..."):
            tests_taken_response = asyncio.run(tests_taken(patient_name))
            if tests_taken_response:
                tests_taken_data = json.loads(tests_taken_response.parameters['patient_test_info_summary'])
                tests_taken_df = pd.DataFrame(tests_taken_data)
                st.subheader("Tests Taken")
                st.table(tests_taken_df)

elif user_type == "Doctor":
    st.header("Doctor Portal")
    with st.form(key="doctor_form"):
        doctor_name = st.text_input("Enter Doctor Name")
        submit = st.form_submit_button("Get Doctor Information")
    
    if submit and doctor_name:
        with st.spinner("Retrieving doctor details..."):
            doctor_details_response = asyncio.run(get_doctor_details(doctor_name))
            if doctor_details_response:
                doctor_info = json.loads(doctor_details_response.parameters['doctor_information_summary'])
                df = pd.DataFrame(list(doctor_info.items()), columns=["Field", "Value"])
                st.subheader("Doctor Details")
                st.table(df)

        with st.spinner("Retrieving upcoming appointments..."):
            upcoming_appointments_response = asyncio.run(upcoming_appointments_doctors(doctor_name))
            if upcoming_appointments_response:
                upcoming_appointments_data = json.loads(upcoming_appointments_response.parameters['appointment_summary'])
                upcoming_appointments_df = pd.DataFrame(upcoming_appointments_data)
                st.subheader("Upcoming Appointments")
                st.table(upcoming_appointments_df)

elif user_type == "Check Availability":
    st.header("Check Doctor Availability")
    with st.form(key="availability_form"):
        department_name = st.text_input("Enter Department Name")
        submit = st.form_submit_button("Check Availability")
    
    if submit and department_name:
        with st.spinner("Retrieving doctor availability..."):
            doctor_availability_response = asyncio.run(doctor_availability(department_name))
            if doctor_availability_response and 'availability_info_summary' in doctor_availability_response.parameters:
                availability_info = doctor_availability_response.parameters['availability_info_summary']
                availability_list = [item.strip() for item in availability_info.split(';')]
                availability_data = [item.split(': ') for item in availability_list]
                doctor_availability_df = pd.DataFrame(availability_data, columns=["Doctor Name", "Available Days"])
                st.subheader(f"Doctor Availability for {department_name} Department")
                st.table(doctor_availability_df)
            else:
                st.error("Failed to retrieve doctor availability or missing 'availability_info_summary'.")

# Add a footer for branding
st.markdown("""
    <style>
        footer {visibility: hidden;}
        .footer {visibility: visible; position: fixed; bottom: 0; width: 100%; text-align: center; color: grey;}
    </style>
    <div class="footer">Built with Conva.AI by SlangLabs 🤖</div>
""", unsafe_allow_html=True)
