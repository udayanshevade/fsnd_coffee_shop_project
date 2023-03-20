# Coffee Shop Full Stack

## Full Stack Nano - IAM Final Project

The application:

1. Allows public users to view drink names and graphics.
2. Allows the shop baristas to see the recipe information.
3. Allows the shop managers to create new drinks and edit existing drinks.

## Instructions to run the app:

1. Clone or download the repo

To run the backend dev server:

1. `cd` into the `./backend` directory
2. Spin up a virtual env: `python3 -m venv env`
3. Activate the virtual env: `source env/bin/activate`
4. Install the required imports: `pip3 install -r requirements.txt`
5. `cd` into the `./src` folder in the backend directory
6. Export the FLASK_APP env var: `export FLASK_APP=api.py;`
7. Run the server: `flask run --reload`

To run the frontend dev server:

1. `cd` to the `./frontend` directory
2. Verify your `Node` version is 16: `node -v` (use `nvm` to downgrade if needed: `nvm use 16`)
3. Install the required packages: `npm i`
4. Start the frontend dev server: `ionic serve`

## Testing:

Open the provided collection from `./backend/udacity-fsnd-udaspicelatte.postman_collection.json` in Postman.
Run the tests for the 'public', 'barista' and 'manager' folders.

## More details

There are more detailed README files in the project folders:

1. [`./backend/`](./backend/README.md) - The `./backend` directory contains a Flask server with modules for SQLAlchemy data, authentication/authorization, and endpoints.
2. [`./frontend/`](./frontend/README.md) - The `./frontend` directory contains an Ionic frontend to consume the data from the Flask server.

## About the Stack

- Flask, SQLAlchemy, Auth0 for identity management
- Ionic, Node 16, TS
