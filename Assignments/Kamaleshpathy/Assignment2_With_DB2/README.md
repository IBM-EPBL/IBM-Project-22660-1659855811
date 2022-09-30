
# Flask App with IBM DB2 database

___

This application is developed with Python's Flask framework, uses Bootstrap for CSS
has a home page, about page, sign in page, sign up page, user info page to show the info of the logged in user.

> ___NOTE: To run this application credentials for IBM-DB2 is required, due to security reasons the credentials and the SSL certificate are removed.___  
> Add your credentials to run this on your side.

Run the following command to run the server

```
flask --debug run
```

The flask application will be running on 

```
localhost:5000
```

## Output Screen shots

___

### Home page

<img src="./outputs/home.png" width=700 />

> The list of registered useres will be shown in this page, these information are reterived from the IBM-DB2.

### Records on IBM-DB2

<img src="./outputs/IBM_DB2.png" width=700 />

### About page

<img src="./outputs/about.png" width=700 />

### Sign up page

<img src="./outputs/signup.png" width=700 />

### Sign in page

<img src="./outputs/signin.png" width=700 />

### User info page

<img src="./outputs/users_page.png" width=700 />

> This page shows the details of logged in user, the sign in page redirects to this page, this page uses dynamic routes.
