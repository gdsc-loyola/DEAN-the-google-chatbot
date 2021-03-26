# DEAN-the-google-chatbot
Dean brings easy access to information to every Filipino. Using Free Facebook Mobile Data, we bring Google Search to all at no cost. Dean is a Facebook chatbot the can search Google!

## Getting Started
1. Fork the repository
    * Create your virtual environment and install all dependencies.
2. Make a .env file (We will add necessary tokens in this later)
3. Use ngrok to make your app accessible online (for testing and development)
    * Download ngrok here: https://ngrok.com/download.
    * Ngrok connects your localhost to an accessible domain.
4. Test it out on your Facebook Page!
    * Create a Facebook Developer account and project, and follow these docs https://developers.facebook.com/docs/messenger-platform/getting-started.
    * Ensure that you have admin rights to the page that you will use.

### Prerequisites
* Python
* Ngrok
* Flask
* Other dependencies can be installed using the command:
    ```bash
    pip install -r requirements.txt
    ```

### Installation
Step by step installation guide

#### 1. Python
* If downloaded through website:
    * https://www.python.org/

* If using Conda
    ```bash
    conda update python
    ```

#### 2. ngrok
* Can be downloaded through this website
    * https://ngrok.com/download

#### 3. Install all required dependencies
* Make sure your virtual environment is activated (We advice you to install these in your virtual environment) ex:
    ```bash
    <virtuelenv>/scripts/activate
    ```
* By using pip install, all dependencies in the requirements.txt file can be installed automatically.
    ```bash
    pip install -r requirements.txt
    ```

## Creating and activating the Development Environment
Step by step process of how to create the Development environment

### Facebook Developers
1. Create a Facebook Developer account (https://developers.facebook.com/)
2. Create your app
3. Navigate to Add Products in the Dashboard screen and set up the Messenger product to the project
4. Click settings under the Messenger Product and link your page to the app. Make sure to get the Access Token that was generated when linking the page.
5. Paste the Page Access Token in the .env folder:
    ```env
    PAGE_ACCESS_TOKEN=<Your Page Access Token>
    ```
6. Add a Verify Token to the .env file
    * You create your own Verify Token
    ```env
    VERIFY_TOKEN=<Your Verify Token>
    ```
7. Go back to the Messenger Product settings and link your Webhook by inputting your Webhook URL (See **Local Machine** steps to get your webhook URL) and the Verify Token you created. 
    * What are webhooks: 
        * https://developers.facebook.com/docs/messenger-platform/webhook
        * https://developers.facebook.com/docs/messenger-platform/getting-started/webhook-setup
8. Click on "messages" and "messaging_postbacks" for the subscriptions fields of the webhook.

### Local Machine
1. Start your server by running main.py
    ```bash
    python main.py
    ```
2. Open your ngrok terminal. By default it should be in the .ngrok directory
    ```bash
    C:/Users/<username>/.ngrok
    ```
3. Open the ngrok shell and type in this command:
    ```bash
    ngrok http 5000
    ```
4. The https link will be the **WEBHOOK URL** of your app

**Congratulations! You have set up your Development environment. Try sending a message to your chatbot to see if it works!**

## Reactivating the Development Environment
Step by step process of how to reactivate your Development Environment. 

### Local Machine
1. Run the server
    ```bash
    python main.py
    ```
2. Activate Ngrok
    ```bash
    ngrok http 5000
    ```
3. Get the https link. That will be your Webhook URL

### Facebook Developers
1. Ngrok creates new URLS every time it is activated. Make sure to update your webhook URL in your Facebook Developer app

## Deployment
Heroku was used in Deploying the Chatbot.

### Facebook Developers App Approval
1. In the dashboard, navigate to app review, open it and click permissions and features
2. You will need to request for Advanced Access to pages_messaging, public_profile, and email in order to get your chatbot up and running for production.
    * Requirements
        * 1024 x 1024 App icon
        * Privacy Policy URL
        * Screen recording of the App being used
3. Once your app is approved, deploy the code on **Heroku** and update your webhook URL

### Heroku
1. Create a Heroku account and create your project. 
2. Under the Deployment field, link your github account and repository.
3. Make sure all the changes have been pushed.
4. You can set up any of your branches for Automatic deploys or Manual deploys, any will work.
5. Once the repository is deployed, copy the URL. This will be your new webhook.

**Congratulations! You have deployed your chatbot to Heroku**

## Built with
* Flask - Web Framework
* Heroku - Deployment
* Beautiful Soap - Web Scraping

## Authors
* Alec Wang
* Francis Guevara 
* Franz Taborlupa
* Gio Divino
