# budget-planner
# Budget & savings tracker app
#
# Tech stack: FastAPI, React JS, & PostegreSQL
#
# MVP Database Design
#
# paychecks
# ---------------
# id | INT PK
# pay_date | DATE
# period_start | DATE
# period_end | DATE
# amount | DECIMAL
# created_at | TIMESTAMP
#
# expense_categories
# ---------------
# id | INT PK
# name | VARCHAR
# budget | DECIMAL
# type | VARCHAR
# active | BOOLEAN
# created_at | TIMESTAMP
#
# paycheck_expenses
# ---------------
# id | INT PK
# paycheck_id | INT FK | → paychecks.id
# category_id | FK | → expense_categories.id
# spent | DECIMAL
# created_at | TIMESTAMP
