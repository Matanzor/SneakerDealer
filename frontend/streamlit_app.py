from pymongo import MongoClient
import streamlit as st
import json
import requests
from json.decoder import JSONDecodeError
from PIL import Image
import io
# from streamlit_extras.app_logo import add_logo 
from streamlit_extras.let_it_rain import rain 
from streamlit_extras.switch_page_button import switch_page 
from streamlit_extras.app_logo import add_logo
import random
from streamlit_extras.colored_header import colored_header 
from streamlit_extras.badges import badge


mongo_uri = "mongodb+srv://admin:admin123123@cluster0.xrhcmq8.mongodb.net/?retryWrites=true&w=majority"
USERS_SERVICE_URL = 'http://users-service:8000'
POSTS_SERVICE_URL = 'http://posts-service:8001'


def display_image(image_id, width=300):  # You can adjust the default width as needed
    # Replace the below URL with your actual endpoint for image retrieval
    image_response = requests.get(f"{POSTS_SERVICE_URL}/images/{image_id}")
    if image_response.status_code == 200:
        image_bytes = image_response.content
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, caption='Post Image', width=width)  # Set the width here
    else:
        st.error("Failed to retrieve image.")


def get_replies_for_post(post_id):
    response = requests.get(f"{POSTS_SERVICE_URL}/replies/{post_id}")
    if response.status_code == 200:
        replies = response.json()
        for reply in replies:
            # Fetch user details for each reply
            user_response = requests.get(f"{USERS_SERVICE_URL}/users/{reply['user_id']}")
            if user_response.status_code == 200:
                user_info = user_response.json()
                # Assuming the response contains a 'username' field
                reply['username'] = user_info['username']
            else:
                reply['username'] = "Unknown"
        return replies
    else:
        st.error("Failed to retrieve replies.")
        return []

def add_reply(post_id, user_id, content):
    reply_data = {"post_id": post_id, "user_id": user_id, "content": content}
    response = requests.post(f"{POSTS_SERVICE_URL}/replies/", json=reply_data)
    if response.status_code == 200:
        st.success('Reply added successfully.')
    else:
        st.error('Failed to add reply.')

def delete_reply(reply_id):
    # Assuming the user_id is stored in the session and POSTS_SERVICE_URL is correctly defined
    user_id = st.session_state['user_id']
    response = requests.delete(f"{POSTS_SERVICE_URL}/replies/{reply_id}?user_id={user_id}")
    if response.status_code == 204:
        st.success('Reply deleted successfully.')
    else:
        st.error('Failed to delete reply. You might not have the necessary permissions.')


def update_post(post_id, title, content, image=None):
    post_data = {"title": title, "content": content}

    if image is not None:
        files = {"file": (image.name, image.getvalue(), image.type)}
        image_response = requests.post(f"{POSTS_SERVICE_URL}/images/", files=files)
        if image_response.status_code == 200:
            post_data["image_id"] = image_response.json().get("image_id")
        else:
            st.error("Failed to upload new image.")
            return

    response = requests.put(f"{POSTS_SERVICE_URL}/posts/{post_id}", json=post_data)
    if response.status_code == 200:
        st.success('Post updated successfully.')
        # Force refresh the page to update the posts
        st.experimental_rerun()
    else:
        error_detail = response.json().get("detail", "An error occurred.")
        st.error(f'Failed to update post: {error_detail}')




def update_post_form(post_id):
    with st.form(key='update_post_form'):
        title = st.text_input("Post Title")
        content = st.text_area("Post Content")
        submit_button = st.form_submit_button(label="Update Post")
        if submit_button:
            update_post(post_id, title, content)


def delete_post(post_id):
    # Assuming POSTS_SERVICE_URL is the URL of your posts service
    response = requests.delete(f"{POSTS_SERVICE_URL}/posts/{post_id}")
    if response.status_code == 204:  # Update condition to check for 204 status code
        return True  # Deletion successful
    else:
        return False  # Deletion failed

def render_post_management_section():
    st.header("Manage Your Posts")

    # Retrieve user's posts
    user_id = st.session_state['user_id']  # Assuming the user_id is stored in the session
    user_posts = get_user_posts(user_id)

    if user_posts:
        # Create a dictionary mapping post titles to post IDs for easier selection
        post_titles_to_ids = {post['title']: post['id'] for post in user_posts}

        # Display user's posts in a selectbox for selection by title
        selected_title = st.selectbox("Select a post to manage", list(post_titles_to_ids.keys()))

        # Use the selected title to get the corresponding post ID
        if selected_title:
            selected_post_id = post_titles_to_ids[selected_title]

            # Find the selected post object by its ID
            selected_post = next((post for post in user_posts if post['id'] == selected_post_id), None)

            if selected_post:
                # Display the selected post details and edit options
                if 'image_id' in selected_post and selected_post['image_id']:
                    display_image(selected_post['image_id'])
                
                st.subheader("Edit Post")
                updated_title = st.text_input('Edit Post Title', value=selected_post['title'])
                updated_content = st.text_area("Edit Post Content", value=selected_post['content'], height=200)
                
                # Allow the user to upload a new image for the post
                updated_image = st.file_uploader("Upload a new image (optional)", type=["jpg", "png"], key="new_image")

                if updated_image is not None:
                    # To read image file buffer with PIL, it needs to be converted to bytes
                    image_bytes = updated_image.getvalue()
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption='Uploaded Image', use_column_width=True)

                # Update button
                if st.button("Update"):
                    # If an image is uploaded, update the post with the new image_id
                    update_post(selected_post_id, updated_title, updated_content, updated_image)
                    st.success("Post updated successfully!")
                    # Re-fetch and display updated posts
                    st.experimental_rerun()

                # Delete button
                if st.button("Delete"):
                    # Call the function to delete the selected post
                    delete_post(selected_post_id)
                    st.success("Post deleted successfully!")
    else:
        st.error("You have no posts to manage.")




def get_user_posts(user_id):
    response = requests.get(f"{POSTS_SERVICE_URL}/posts/user/{user_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve user's posts.")
        return []

def search_posts(query):
    response = requests.get(f"{POSTS_SERVICE_URL}/posts/search?query={query}")
    if response.status_code == 200:
        posts_response = response.json()
        for post in posts_response:
            user_id = post['user_id']
            # Assuming there's an 'author_id' in post to fetch user details
            user_response = requests.get(f"{USERS_SERVICE_URL}/users/{user_id}")
            if user_response.status_code == 200:
                user = user_response.json()
                post['author_name'] = user['username']  # Fetch the username, assuming 'username' is the key
            else:
                post['author_name'] = "Unknown"  # Fallback if user details can't be fetched
        return posts_response
    else:
        print("Failed to retrieve search results.")
        return []


def get_all_posts():
    posts_response = requests.get(f"{POSTS_SERVICE_URL}/posts/")
    if posts_response.status_code == 200:
        posts = posts_response.json()
        # Fetch author's usernames for each post
        for post in posts:
            user_id = post['user_id']
            user_response = requests.get(f"{USERS_SERVICE_URL}/users/{user_id}")
            if user_response.status_code == 200:
                user = user_response.json()
                post['author_name'] = user['username']
            else:
                post['author_name'] = "Unknown"
        return posts
    else:
        st.error("Failed to retrieve posts.")
        return []


# Function to add a new post

def add_post(title, content, uploaded_image):
    if 'user_id' in st.session_state and st.session_state['user_id']:
        user_id = str(st.session_state['user_id'])
        post_data = {"title": title, "content": content, "user_id": user_id}

        if uploaded_image is not None:
            # Use the uploaded_image directly for the files parameter in the request
            files = {"file": (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)}
            image_response = requests.post(f"{POSTS_SERVICE_URL}/images/", files=files)
            if image_response.status_code == 200:
                post_data["image_id"] = image_response.json().get("image_id")
            else:
                st.error('Failed to upload image. Please try again.')
                return

        response = requests.post(f"{POSTS_SERVICE_URL}/posts/", json=post_data)
        if response.status_code == 200:
            st.success('Post added successfully.')

            # Display the uploaded image using the display_image function
            if uploaded_image is not None:
                # Extract the image ID from the response
                image_id = response.json().get("image_id")
                # Call the display_image function to display the image
                display_image(image_id)
                
        else:
            st.error(f'Failed to add post: {response.json().get("detail", "Unknown error")}')
    else:
        st.error('User ID not found in session. Please log in.')

# Ensure the user_id is initialized in session state if it's not already set
# if 'user_id' not in st.session_state:
#     st.session_state['user_id'] = None




# Helper functions to convert user document from database to a dictionary
def user_helper(user) -> dict:
    # Assuming you have a user model with these fields
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "hashed_password": user["hashed_password"]
    }

# Function to register a new user
def register_user(username, email, full_name, password):
    user_data = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password
    }
    response = requests.post(f"{USERS_SERVICE_URL}/users/", json=user_data)
    if response.status_code == 200:
        st.success('Registration successful. You can now log in.')
        user_id = response.json().get('user_id')  # Capture the user_id
        # Set the user_id in session state
        st.session_state['user_id'] = user_id
    else:
        st.error(f'Registration failed: {response.json().get("detail", "Unknown error")}')


# Function to log in a user
def login_user(username, password):
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{USERS_SERVICE_URL}/token", data=login_data)
    if response.status_code == 200:
        st.success('Login successful.')
        token = response.json().get('access_token')
        
        # Ensure the backend sends user_id in the login response
        user_id = response.json().get('user_id')
        
        if user_id:
            # Set the token, username, and user_id in session state
            st.session_state['token'] = token
            st.session_state['username'] = username
            st.session_state['user_id'] = user_id  # Set user_id here
            
            # Optional: Print or log for debugging
            print("User ID set in session state:", st.session_state['user_id'])
        else:
            st.error('Login failed: User ID not returned from the server.')
    else:
        st.error('Login failed. Please check your username and password.')

def display_banner():
    st.image("https://github.com/Matanzor/SneakerDealer/assets/121384944/d29c8f95-8c36-487c-a138-e23476e3cca6")    

# Function to render the sidebar menu
def render_sidebar_menu():
    display_banner()
    st.sidebar.title("SneakerDealer")

    # If the user is logged in, display their username and a logout button
    if 'token' in st.session_state and st.session_state['token']:
        st.sidebar.write(f"You are logged in as {st.session_state['username']}.")
        if st.sidebar.button('Logout'):
            # Log out the user by clearing the session state
            st.session_state.clear()
            st.experimental_rerun()
    else:
        # if not st.session_state['token']:
        #     st.sidebar.write("Please log in.")
        rain(
        emoji="👟",
        font_size=54,
        falling_speed=5,
        animation_length="infinite",
    )
        # If the user is not logged in, show the options to Register or Login
        auth_option = st.sidebar.selectbox("Choose an option:", ["Register", "Login"])
        if auth_option == "Register":
            register_user_form()
        elif auth_option == "Login":
            login_user_form()

    # Display the rest of the menu items only if the user is logged in
    if 'token' in st.session_state and st.session_state['token']:
        menu = ["Home 🏠", "View Post 📋", "Add Post ➕", "Search 🔍", "Manage Blog 🔨"]
        choice = st.sidebar.selectbox("Menu", menu)
        handle_menu_choice(choice)



# Function to handle menu choice
def handle_menu_choice(choice):    
    st.session_state['current_choice'] = choice
  
    if choice == "Home 🏠":
        rain(
        emoji="👟",
        font_size=54,
        falling_speed=5,
        animation_length="infinite",
    )
        # Display home page content here

    elif choice == "View Post 📋":
        colored_header(label="View Posts",description = None, color_name = "violet-70")
        all_posts = get_all_posts()  # Fetch all posts from the posts service

        if all_posts:
            for index, post in enumerate(all_posts):
                with st.container():
                    st.markdown(f"#### {post['title']}")
                    st.caption(f"Author: {post['author_name']}")

                    # Display the image if an image_id is associated with the post
                    if 'image_id' in post and post['image_id']:
                        display_image(post['image_id'])

                    st.text(f"Content: {post['content']}")

                    # Reply section
                    with st.form(key=f"reply_form_{post['id']}"):
                        reply_content = st.text_area("Write a reply", key=f"reply_content_{post['id']}")
                        submit_reply = st.form_submit_button("Post Reply")
                        if submit_reply:
                            add_reply(post['id'], st.session_state['user_id'], reply_content)
                            st.success("Reply posted successfully!")

                    # Display existing replies
                    with st.expander("View Replies"):
                        replies = get_replies_for_post(post['id'])
                        if replies:
                            for reply_index, reply in enumerate(replies):
                                st.markdown(f"- {reply['content']} (User: {reply['username']})")
                                # Display the delete button only for replies created by the logged-in user
                                if reply['user_id'] == st.session_state['user_id']:
                                    if st.button("Delete", key=f"delete_{reply['id']}"):
                                        delete_reply(reply['id'])

                                # Add a separator after each reply and its delete button, except after the last one
                                if reply_index < len(replies) - 1:
                                    st.markdown("---")
                        else:
                            st.write("No replies yet.")

                    # Separator line after each post
                    st.markdown("---")
        else:
            st.write("No posts to display.")


                
        

        # Display post viewing functionality here
    elif choice == "Add Post ➕":
        st.subheader("Add Your Post")
        
        # Begin the form for adding a post
        with st.form(key='add_post_form'):
            title = st.text_input("Post Title")
            content = st.text_area("Post Content", height=200)

            # Button to submit the form and add the post
            submit_button = st.form_submit_button(label="Add Post")

        # Image uploader placed after the form to ensure it's displayed below the post content
        uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png"])
        if uploaded_image is not None:
            # Display the uploaded image immediately below the post content
            image_bytes = uploaded_image.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption='Uploaded Image Preview', use_column_width=True)

        # Form submission logic outside the 'with st.form' block
        if submit_button:
            # Call the add_post function with the uploaded image only after the form is submitted
            add_post(title, content, uploaded_image)



    elif choice == "Search 🔍":
        st.subheader("Search Posts")

        # Use session state to retain the search query
        if 'search_query' not in st.session_state:
            st.session_state['search_query'] = ''

        # Input for search query with session state
        search_query = st.text_input("Enter search keywords", value=st.session_state['search_query'])
        
        # Update session state and rerun on search
        if st.button("Search"):
            st.session_state['search_query'] = search_query
            st.experimental_rerun()

        # Perform search using the query stored in session state
        if st.session_state['search_query']:
            results = search_posts(st.session_state['search_query'])
            if results:
                for index, post in enumerate(results):
                    with st.container():
                        st.markdown(f"#### {post['title']}")
                        st.caption(f"Author: {post['author_name']}")
                        st.write(f"Posted on: {post.get('created_at', 'Unknown')}")

                        # Display the image if an image_id is associated with the post
                        if 'image_id' in post and post['image_id']:
                            display_image(post['image_id'])

                        st.text(f"Content: {post['content']}")

                        # Reply section
                        with st.form(key=f"reply_form_{post['id']}"):
                            reply_content = st.text_area("Write a reply", key=f"reply_content_{post['id']}")
                            submit_reply = st.form_submit_button("Post Reply")
                            if submit_reply:
                                add_reply(post['id'], st.session_state['user_id'], reply_content)
                                st.success("Reply posted successfully!")
                                st.experimental_rerun()  # Rerun the app to refresh the replies section

                        # Display existing replies
                        with st.expander("View Replies"):
                            replies = get_replies_for_post(post['id'])
                            if replies:
                                for reply in replies:
                                    st.markdown("---")
                                    st.markdown(f"- {reply['content']} (User: {reply['username']})")
                                    # Display the delete button only for replies created by the logged-in user
                                    if reply['user_id'] == st.session_state['user_id']:
                                        if st.button("Delete", key=f"delete_{reply['id']}"):
                                            delete_reply(reply['id'])
                                            st.experimental_rerun()  # Rerun the app to refresh the replies section
                            else:
                                st.write("No replies yet.")

                        st.markdown("---")  # Separator line after each post
            else:
                st.write("No results found.")



    elif choice == "Manage Blog 🔨":
        st.subheader("Manage Blog")
        render_post_management_section()
        # Display blog management functionality here


# Function to show register user form
def register_user_form():
    with st.sidebar.form(key='register_form'):
        new_username = st.text_input("New Username", key="reg_username")
        new_email = st.text_input("Email", key="reg_email")
        new_full_name = st.text_input("Full Name", key="reg_full_name")
        new_password = st.text_input("New Password", type="password", key="reg_password")
        submit_button = st.form_submit_button(label="Register")
        if submit_button:
            register_user(new_username, new_email, new_full_name, new_password)

# Function to show login user form
def login_user_form():
    with st.sidebar.form(key='login_form'):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button(label="Login")
        if submit_button:
            login_user(username, password)
        

# Main function to coordinate the app
def main():
    # Initialize session state for token if it doesn't exist
    icon_size = 22
    if 'token' not in st.session_state:
        st.session_state['token'] = None      

    # Render the sidebar menu
    render_sidebar_menu()

    # Check if the user is logged in and display the main page
    if not st.session_state['token']:
        st.sidebar.write("Please log in.")

    if st.session_state.get('current_choice') not in ["View Post 📋", "Add Post ➕", "Search 🔍", "Manage Blog 🔨"]:
        colored_header(label="Welcome to SneakerDealer",description = None, color_name = "violet-70")
        st.write("Welcome to the ultimate destination for sneaker enthusiasts – a vibrant community where passion for sneakers transcends the ordinary. Dive into our world where every step tells a story; a place where you can unleash your sneaker obsession, showcase your collection, and connect with fellow aficionados. Whether you're here to discover the latest trends, buy the pair you've been dreaming of, sell gems from your collection, or trade kicks with others, you've found your haven. Our blog is the pulse of sneaker culture, offering insights, reviews, and discussions on everything from vintage classics to the newest drops. Join us in celebrating the art and soul of sneakers. Step in and make your mark in the ever-evolving sneaker saga. 👟")


        st.write("Compare prices with [StockX](https://stockx.com/)")   

        st.write("Check future drops with [Droplist](https://www.drop-list.com/)")       
    

if __name__ == "__main__":
    main()


# Function to delete an existing post
def delete_post(post_id):
    response = requests.delete(f"{POSTS_SERVICE_URL}/posts/{post_id}")
    if response.status_code == 204:
        st.success('Post deleted successfully.')
    else:
        st.error(f'Failed to delete post: {response.json().get("detail", "Unknown error")}')

# Function to show the add post form
def add_post_form():
    with st.form(key='add_post_form'):
        title = st.text_input("Post Title")
        content = st.text_area("Post Content")
        uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png"])

        # Display the uploaded image immediately
        if uploaded_image is not None:
            # To read image file buffer with PIL, it needs to be converted to bytes
            image_bytes = uploaded_image.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption='Uploaded Image', use_column_width=True)

        submit_button = st.form_submit_button(label="Add Post")

    # Handling form submission outside the 'with st.form' block
    if submit_button:
        add_post(title, content, uploaded_image)