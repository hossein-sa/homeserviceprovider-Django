# Home Service Provider Platform

A Django-based platform where customers can request home services, and specialists can offer their services. The platform includes a wallet-based payment system for customer transactions with automatic commission distribution to the admin.

## Features

- **User Roles**: Customers, Specialists, and Admins.
- **Wallet System**: Rechargeable wallets for customers and specialists with commission calculation.
- **Order Management**: Customers can create and manage service requests, and specialists can propose services.
- **Payment Processing**: Simulated payment processing for wallet recharges and order payments.
- **Admin Commission**: The system automatically distributes a 30% commission to the admin and 70% to the specialist.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/homeserviceprovider.git
   cd homeserviceprovider
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser**:

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

## Usage

### User Roles and Permissions

- **Customer**: Can create and manage orders, recharge wallets, and mark orders as completed.
- **Specialist**: Can view available orders and submit proposals for customer orders.
- **Admin**: Manages users and has access to the admin dashboard.

### Order Workflow

1. **Order Creation**: Customers create orders specifying the required service.
2. **Proposal Submission**: Specialists submit proposals for orders in their area of expertise.
3. **Proposal Selection**: Customers select a proposal from the list of submissions.
4. **Order Completion and Payment**: Once work is completed, the customer marks the order as completed, and payment is distributed.

### Wallet System

Customers and specialists have wallets managed by the system. Admin receives a 30% commission on each completed order, and the remaining 70% goes to the specialist.

### Simulated Payment for Wallet Recharge

The platform includes a simulated payment form for recharging customer wallets, styled with Bootstrap to resemble a bank’s payment page.

## Project Structure

```plaintext
├── users/
│   ├── models.py         # User, Wallet, and Transaction models
│   ├── views.py          # Views for wallet recharge and user management
│   ├── urls.py           # URL configurations for users app
│
├── services/
│   ├── models.py         # Models for MainService and SubService
│   ├── admin.py          # Admin configurations
│
├── orders/
│   ├── models.py         # Order and Proposal models
│   ├── views.py          # Order management views
│   ├── utils.py          # Payment processing logic
│   ├── urls.py           # URL configurations for orders app
│
├── templates/
│   ├── users/
│   │   ├── recharge_wallet.html     # Wallet recharge form
│   │   ├── wallet.html              # Wallet balance display
│   ├── orders/
│   │   ├── payment_form.html        # Order payment simulation form
│
└── README.md            # Project documentation
```

## API Endpoints

| Endpoint                     | Method | Description |
|------------------------------|--------|-------------|
| `/api/users/register/`       | POST   | Register a new user (customer or specialist) |
| `/api/orders/create/`        | POST   | Create a new order (customer only) |
| `/api/orders/proposal/`      | POST   | Submit a proposal for an order (specialist only) |
| `/api/orders/select-proposal/`| PUT   | Select a proposal for an order (customer only) |
| `/api/users/recharge-wallet/` | POST   | Recharge the customer’s wallet |
| `/admin/`                    | GET    | Admin dashboard |

## Contributing

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push to the branch.
5. Open a pull request.

## License

This project is licensed under the MIT License.
