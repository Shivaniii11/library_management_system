import streamlit as st
import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='1111',
    database='week4'
)

mycursor = db.cursor(buffered=True)

st.title("Welcome Page")
choice = st.selectbox('What would you like to do',['Change Username','Change Password','Delete Account'])
if choice == 'Change Username':
    user=st.text_input('Enter you current username')
    new_user=st.text_input('Enter your new user name')
    change = st.button('Submit')
    if change:
        if len(new_user) < 5:
            st.error('username should have more than 5 characters')
        else:
            mycursor.execute('update user set username = %s where username = %s',(new_user,user))
            db.commit()
            st.success('Username changed successfully!!!')

if choice == 'Change Password':
    user = st.text_input('Enter your username')
    passw = st.text_input('Enter current password',type='password')
    new_passw = st.text_input('Enter you new password',type='password')
    submit = st.button('Submit')
    if submit:
        ch = "!@#$%^&*(),.?\":{}|<>"
        if len(new_passw) < 8:
            st.error("Password must be at least 8 characters long.")
        elif not any(c.isupper() for c in new_passw):
            st.error("Password must include an uppercase letter.")
        elif not any(c.islower() for c in new_passw):
            st.error("Password must include a lowercase letter.")
        elif not any(c.isdigit() for c in new_passw):
            st.error("Password must include a digit.")
        elif not any(c in ch for c in new_passw):
            st.error("Password must include a special character.")
        else:
            mycursor.execute('update user set password = %s where username = %s',(new_passw,user))
            db.commit()
            st.success('Password changed successfully!!!')

if choice == 'Delete Account':
    select = st.checkbox('Are you sure you want to delete your account')
    if select:
        user = st.text_input('Enter your username')
        but = st.button('Delete')
        if but:
            mycursor.execute('delete from peop where username = %s',(user,))
            db.commit()
            st.success('Account deleted successfully!!!')

        

    


            

