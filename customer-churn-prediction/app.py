# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import joblib
import os
import mysql.connector
import streamlit_authenticator as stauth

# Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='mysql',
        database='streamlit_app'
    )

# Fetch user credentials from MySQL
def fetch_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, username, password FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

# Add new user to MySQL
def add_user(name, username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, username, password) VALUES (%s, %s, %s)", (name, username, password))
    conn.commit()
    cursor.close()
    conn.close()

# Get user credentials
users = fetch_users()
names = [user['name'] for user in users]
usernames = [user['username'] for user in users]
passwords = [user['password'] for user in users]

# Hash passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Initialize authenticator
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, 'some_cookie_name', 'some_signature_key', cookie_expiry_days=30)

# Define main application
def main():
    st.title('Telco Customer Churn Prediction App')

    # Get the directory of the current script
    current_dir = os.path.dirname(__file__)
    image_path = os.path.join(current_dir, 'App.jpg')

    # Check if the file exists before loading
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption='App Image')
    else:
        st.error(f"Image file not found at {image_path}")

    # Load the model
    model_path = os.path.join(current_dir, 'notebook', 'model.sav')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        st.write("Model loaded successfully!")
    else:
        st.error(f"Model file not found at {model_path}")

    # Setting Application title
    st.title('Telco Customer Churn Prediction App')

    # Setting Application description
    st.markdown("""
     :dart:  This Streamlit app is made to predict customer churn in a fictional telecommunication use case.
    The application is functional for both online prediction and batch data prediction. \n
    """)
    st.markdown("<h3></h3>", unsafe_allow_html=True)

    # Setting Application sidebar default
    add_selectbox = st.sidebar.selectbox(
        "How would you like to predict?", ("Online", "Batch")
    )
    st.sidebar.info('This app is created to predict Customer Churn')
    st.sidebar.image(image)

    if add_selectbox == "Online":
        st.info("Input data below")
        # Based on our optimal features selection
        st.subheader("Demographic data")
        seniorcitizen = st.selectbox('Senior Citizen:', ('Yes', 'No'))
        dependents = st.selectbox('Dependent:', ('Yes', 'No'))

        st.subheader("Payment data")
        tenure = st.slider('Number of months the customer has stayed with the company', min_value=0, max_value=72, value=0)
        contract = st.selectbox('Contract', ('Month-to-month', 'One year', 'Two year'))
        paperlessbilling = st.selectbox('Paperless Billing', ('Yes', 'No'))
        PaymentMethod = st.selectbox('PaymentMethod',('Electronic check', 'Mailed check', 'Bank transfer (automatic)','Credit card (automatic)'))
        monthlycharges = st.number_input('The amount charged to the customer monthly', min_value=0, max_value=150, value=0)
        totalcharges = st.number_input('The total amount charged to the customer',min_value=0, max_value=10000, value=0)

        st.subheader("Services signed up for")
        mutliplelines = st.selectbox("Does the customer have multiple lines",('Yes','No','No phone service'))
        phoneservice = st.selectbox('Phone Service:', ('Yes', 'No'))
        internetservice = st.selectbox("Does the customer have internet service", ('DSL', 'Fiber optic', 'No'))
        onlinesecurity = st.selectbox("Does the customer have online security",('Yes','No','No internet service'))
        onlinebackup = st.selectbox("Does the customer have online backup",('Yes','No','No internet service'))
        techsupport = st.selectbox("Does the customer have technology support", ('Yes','No','No internet service'))
        streamingtv = st.selectbox("Does the customer stream TV", ('Yes','No','No internet service'))
        streamingmovies = st.selectbox("Does the customer stream movies", ('Yes','No','No internet service'))

        data = {
                'SeniorCitizen': seniorcitizen,
                'Dependents': dependents,
                'tenure': tenure,
                'PhoneService': phoneservice,
                'MultipleLines': mutliplelines,
                'InternetService': internetservice,
                'OnlineSecurity': onlinesecurity,
                'OnlineBackup': onlinebackup,
                'TechSupport': techsupport,
                'StreamingTV': streamingtv,
                'StreamingMovies': streamingmovies,
                'Contract': contract,
                'PaperlessBilling': paperlessbilling,
                'PaymentMethod': PaymentMethod, 
                'MonthlyCharges': monthlycharges, 
                'TotalCharges': totalcharges
                }
        features_df = pd.DataFrame.from_dict([data])
        st.markdown("<h3></h3>", unsafe_allow_html=True)
        st.write('Overview of input is shown below')
        st.markdown("<h3></h3>", unsafe_allow_html=True)
        st.dataframe(features_df)

        # Preprocess inputs
        preprocess_df = preprocess(features_df, 'Online')

        prediction = model.predict(preprocess_df)

        if st.button('Predict'):
            if prediction == 1:
                st.warning('Yes, the customer will terminate the service.')
            else:
                st.success('No, the customer is happy with Telco Services.')
    else:
        st.subheader("Dataset upload")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            # Get overview of data
            st.write(data.head())
            st.markdown("<h3></h3>", unsafe_allow_html=True)
            # Preprocess inputs
            preprocess_df = preprocess(data, "Batch")
            if st.button('Predict'):
                # Get batch prediction
                prediction = model.predict(preprocess_df)
                prediction_df = pd.DataFrame(prediction, columns=["Predictions"])
                prediction_df = prediction_df.replace({1: 'Yes, the customer will terminate the service.', 
                                                       0: 'No, the customer is happy with Telco Services.'})

                st.markdown("<h3></h3>", unsafe_allow_html=True)
                st.subheader('Prediction')
                st.write(prediction_df)

# Registration
def register():
    st.title("User Registration")
    new_name = st.text_input("Enter your name")
    new_username = st.text_input("Enter a username")
    new_password = st.text_input("Enter a password", type="password")

    if st.button("Register"):
        if new_name and new_username and new_password:
            # Check if username already exists
            if new_username in usernames:
                st.warning("Username already exists. Please choose a different one.")
            else:
                # Hash the new password
                hashed_password = stauth.Hasher([new_password]).generate()[0]
                add_user(new_name, new_username, hashed_password)
                st.success("You have successfully registered!")
        else:
            st.warning("Please fill out all fields.")

if __name__ == '__main__':
    auth_option = st.sidebar.selectbox("Choose Authentication Option", ["Login", "Register"])

    if auth_option == "Login":
        name, authentication_status, username = authenticator.login('Login', 'main')
        if authentication_status:
            main()
        elif authentication_status == False:
            st.error('Username/password is incorrect')
        elif authentication
