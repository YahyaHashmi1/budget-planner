# Paycheck Budget Tracker

A simple personal budgeting application designed around **biweekly pay periods**. The goal is to replace spreadsheets and manual calculations for tracking expenses and recurring bills.

## MVP Features

* Add a new paycheck

  * Paycheck amount
  * Pay date
  * Automatically calculates the 14-day pay period
* Create expense categories

  * Name
  * Budget
  * Category type
  * Active/inactive status
* Add individual expenses to categories

  * Expense name
  * Amount
  * Automatically updates category spending
* Delete paychecks, categories, and expense items
* Track recurring bills across two pay periods
* Track fixed recurring and variable recurring expenses
* Display the current pay period and expense progress on the dashboard

## Expense Category Types

| Type                   | Resets Each Pay Period | Amount Known Upfront | Example              |
| ---------------------- | ---------------------- | -------------------- | -------------------- |
| Variable Non-Recurring | Yes                    | Yes                  | Food, Groceries, Gas |
| Fixed Recurring        | No                     | Yes                  | Insurance, Internet  |
| Variable Recurring     | No                     | No                   | Electricity          |

### Recurring Bill Flow

Recurring bills span two pay periods.

```text
Bill: $200

Pay Period 1
$100 paid
Status: First Half Paid

        ↓

Pay Period 2
$100 paid
Status: Complete
```

Fixed recurring bills have a known amount and only require confirmation.

Variable recurring bills require the user to enter the actual bill amount.

## Dashboard

The MVP uses a single dashboard containing:

```text
PAY PERIOD: 09/25/26 - 10/09/26

VARIABLE · NON-RECURRING

Food                 $60 / $160
  ├── Chipotle          $18
  ├── Taco Bell         $12
  └── Pizza             $30

Groceries            $60 / $200
  ├── Kroger            $45
  └── Kroger            $15

RECURRING BILLS

AWAITING CHARGE
Electricity          [Enter Amount]

IN PROGRESS
Car Insurance        $32 / $64
Gym                  $25 / $50

COMPLETE
(none)
```

## Database

The MVP uses six PostgreSQL tables:

```text
users
  │
  ├── paychecks
  │      │
  │      ├── expense_items
  │      │
  │      └── billing_cycle_payments
  │
  └── expense_categories
          │
          └── billing_cycles
```

### Tables

* `users` — User accounts and future JWT authentication
* `paychecks` — Paycheck information and 14-day pay periods
* `expense_categories` — Reusable expense category definitions
* `expense_items` — Individual purchases associated with a paycheck/category
* `billing_cycles` — Tracks recurring bills across two pay periods
* `billing_cycle_payments` — Records each half-payment of a recurring bill

## Planned Tech Stack

### Application

* React
* TypeScript
* Vite
* Tailwind CSS
* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic

### DevOps / Cloud

* Docker
* Docker Compose
* Terraform
* AWS
* GitHub Actions
* Amazon ECS
* Amazon RDS
* Amazon ECR
* CloudWatch

## Project Goals

This project is being built as both a personal budgeting tool and a hands-on **DevOps/Cloud engineering project**.

The initial focus is on building a functional application locally. Cloud infrastructure, Terraform, Docker, CI/CD, monitoring, and AWS deployment will be added as the project progresses.

## Status

**Current stage:** Database design / MVP planning

### MVP Roadmap

* [x] Define MVP requirements
* [x] Design database schema
* [ ] Create PostgreSQL database
* [ ] Build FastAPI backend
* [ ] Build dashboard
* [ ] Implement paycheck functionality
* [ ] Implement expense categories
* [ ] Implement expense items
* [ ] Implement recurring billing cycles
* [ ] Add Docker
* [ ] Add automated tests
* [ ] Add Terraform
* [ ] Deploy to AWS
* [ ] Add CI/CD
* [ ] Add monitoring
* [ ] Add JWT authentication
