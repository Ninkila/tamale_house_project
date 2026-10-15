# Tamale House Market 🏠

**Tamale House Market** is a house-rental platform designed to help people find rental properties in Tamale, Ghana, while providing landlords with a digital way to showcase their available properties.

The project aims to make house hunting more accessible, organized, and convenient by bringing property listings and prospective tenants together through one platform.

> **Project status:** Under development.

## 🎯 The Problem

Finding a house to rent in Tamale can be challenging. Prospective tenants may have difficulty discovering available properties, comparing rental prices, and connecting with landlords.

Landlords may also lack a convenient digital platform for advertising their properties to potential tenants.

Tamale House Market aims to address these challenges by creating a centralized platform for rental property discovery.

## 💡 The Solution

The platform is being developed to provide a digital space where:

* Tenants can discover available rental properties.
* Users can explore property information and rental prices.
* Landlords can showcase their properties.
* Property seekers and landlords can connect more conveniently.

## ✨ Key Features

The following features represent the platform's intended functionality. Availability depends on the current development stage.

* **Property Listings:** Display rental properties and their details.
* **House Search:** Help users find properties that match their needs.
* **Rental Prices:** Present property prices clearly.
* **Landlord Accounts:** Support landlord registration and authentication.
* **Tenant Accounts:** Support tenant registration and authentication.
* **Role-Based Access:** Distinguish between landlord and tenant permissions.
* **Property Management:** Provide a foundation for managing rental listings.

## 🛠️ Technology Stack

The project uses or is being developed with the following technologies:

* **Backend:** Python and Flask
* **Frontend:** HTML, CSS, and JavaScript
* **Database:** PostgreSQL
* **Database Connectivity:** Psycopg
* **Configuration:** Environment variables using a `.env` file
* **Version Control:** Git and GitHub

The exact technologies and components may evolve during development.

## 📁 Project Structure

The project structure may vary as development continues.

```text
tamale_house_finder/
├── frontend/       # Frontend assets and user interface
├── src/            # Application modules and backend logic
├── data/           # Project data and related resources
├── .env            # Local environment variables (not committed)
├── .gitignore      # Files excluded from version control
└── README.md       # Project documentation
```

## ⚙️ Getting Started

### Prerequisites

Install the following before running the application:

* Python 3
* PostgreSQL
* Git

A code editor such as Visual Studio Code is recommended.

### 1. Clone the repository

```bash
git clone 'https://github.com/Ninkila/tamale_house_project'
```

Replace `https://github.com/Ninkila/tamale_house_project` with the actual URL of your GitHub repository.

### 2. Navigate to the project directory

```bash
cd tamale_house_finder
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

Install the dependencies listed in the project's dependency file.

If a `requirements.txt` file exists, run:

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create a local `.env` file and configure the required environment variables.

For example, the application may require a PostgreSQL connection string and other application settings.

**Important:** Never commit real database passwords, secret keys, or other credentials to GitHub.

### 7. Configure the database

Ensure PostgreSQL is running and the required database exists.

Configure the database connection using the environment variables expected by the application.

Initialize the database using the project's existing setup process.

### 8. Run the application

Start the Flask application using the project's configured entry point.

Consult the application code for the correct startup command.

## 🔐 Security

Security is an important consideration for a platform involving user accounts and property information.

Development priorities include:

* Secure password storage.
* Authentication and authorization.
* Role-based access control.
* Environment-based configuration.
* Protection of database credentials.
* Validation of user input.

## 🚧 Development Roadmap

Potential areas for continued development include:

* [ ] Complete the tenant-facing interface.
* [ ] Complete the landlord dashboard.
* [ ] Improve property search and filtering.
* [ ] Implement property listing management.
* [ ] Strengthen authentication and authorization.
* [ ] Improve mobile responsiveness.
* [ ] Add property images and detailed descriptions.
* [ ] Test the application and improve error handling.
* [ ] Prepare the application for deployment.

The checklist should be updated as features are implemented.

## 🌍 Vision

The long-term vision of Tamale House Market is to make finding and advertising rental properties in Tamale easier through technology, with the potential to expand to other locations in Ghana.

## 👨‍💻 Contributing

The project is currently under development.

Suggestions, feedback, and contributions that improve the platform's usability, security, and reliability are welcome.

## 📄 License

No license has been specified yet.
