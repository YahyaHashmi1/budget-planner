import { useEffect, useState } from "react";
import type { ComponentProps } from "react";

import { getJson, postJson } from "./api";
import type {
  Paycheck,
  PaycheckCreate,
  ExpenseCategory,
  ExpenseCategoryCreate,
  ExpenseItem,
  ExpenseItemCreate,
} from "./types";

import "./App.css";

// Read development configuration from the Vite environment.
const USER_ID = import.meta.env.VITE_DEMO_USER_ID;

// Derive the correct React form-submit event type without importing FormEvent.
type FormSubmitEvent = Parameters<
  NonNullable<ComponentProps<"form">["onSubmit"]>
>[0];

// Return today's date in local YYYY-MM-DD format for date inputs.
function getToday(): string {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

// Format monetary values consistently, including API decimal strings.
function formatCurrency(value: string | number | null | undefined): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(Number(value ?? 0));
}

function App() {
  // Dashboard data.
  const [paychecks, setPaychecks] = useState<Paycheck[]>([]);
  const [categories, setCategories] = useState<ExpenseCategory[]>([]);
  const [expenses, setExpenses] = useState<ExpenseItem[]>([]);

  // General page status.
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Add-paycheck form fields.
  const [paycheckAmount, setPaycheckAmount] = useState("");
  const [payDate, setPayDate] = useState(getToday());

  // Add-category form fields.
  const [categoryName, setCategoryName] = useState("");
  const [categoryBudget, setCategoryBudget] = useState("");
  const [categoryType, setCategoryType] =
    useState<ExpenseCategory["type"]>("VARIABLE_NON_RECURRING");

  // Add-expense form fields.
  const [expenseCategoryId, setExpenseCategoryId] = useState("");
  const [expenseName, setExpenseName] = useState("");
  const [expenseAmount, setExpenseAmount] = useState("");
  const [spentOn, setSpentOn] = useState(getToday());

  // The latest paycheck is the active paycheck for this dashboard.
  const currentPaycheck = paychecks[0];

  // Only non-recurring categories can receive ordinary expense items.
  const regularCategories = categories.filter(
    (category) => category.type === "VARIABLE_NON_RECURRING",
  );

  // Load the user's paychecks and active expense categories.
  async function loadDashboard() {
    if (!USER_ID) {
      throw new Error(
        "Set VITE_DEMO_USER_ID in frontend/.env to your existing user UUID.",
      );
    }

    // Retrieve both collections concurrently.
    const [paycheckData, categoryData] = await Promise.all([
      getJson<Paycheck[]>("/paychecks"),
      getJson<ExpenseCategory[]>(
        `/expense-categories?user_id=${encodeURIComponent(USER_ID)}`,
      ),
    ]);

    // Keep only this development user's paychecks and sort newest first.
    const userPaychecks = paycheckData
      .filter((paycheck) => paycheck.user_id === USER_ID)
      .sort((a, b) => {
        // Use pay date first, with creation order as a tie-breaker.
        const dateComparison = b.pay_date.localeCompare(a.pay_date);
        if (dateComparison !== 0) return dateComparison;

        return b.period_start.localeCompare(a.period_start);
      });

    // Hide deactivated categories from the dashboard.
    const activeCategories = categoryData.filter(
      (category) => category.active,
    );

    setPaychecks(userPaychecks);
    setCategories(activeCategories);
  }

  // Load the dashboard when the component first mounts.
  useEffect(() => {
    async function initializeDashboard() {
      try {
        await loadDashboard();
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load the dashboard.",
        );
      } finally {
        setLoading(false);
      }
    }

    void initializeDashboard();
  }, []);

  // Keep the selected category valid as categories are added or changed.
  useEffect(() => {
    if (regularCategories.length === 0) {
      setExpenseCategoryId("");
      return;
    }

    // Preserve the existing selection if it is still available.
    const selectionIsValid = regularCategories.some(
      (category) => category.id === expenseCategoryId,
    );

    if (!selectionIsValid) {
      setExpenseCategoryId(regularCategories[0].id);
    }
  }, [categories, expenseCategoryId]);

  // Fetch expenses whenever the current paycheck changes.
  useEffect(() => {
    let cancelled = false;

    async function loadExpenses() {
      // Clear old expenses when there is no current paycheck.
      if (!currentPaycheck) {
        setExpenses([]);
        return;
      }

      try {
        // The active paycheck determines which expenses are displayed.
        const expenseData = await getJson<ExpenseItem[]>(
          `/expense-items?paycheck_id=${encodeURIComponent(currentPaycheck.id)}`,
        );

        // Avoid updating state if the effect has been cleaned up.
        if (!cancelled) {
          setExpenses(expenseData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load expenses.",
          );
        }
      }
    }

    void loadExpenses();

    // Ignore stale results if the user switches to another paycheck.
    return () => {
      cancelled = true;
    };
  }, [currentPaycheck?.id]);

  // Add a new paycheck and refresh the dashboard.
  async function handleAddPaycheck(event: FormSubmitEvent) {
    event.preventDefault();
    setSaving("paycheck");
    setError("");
    setMessage("");

    try {
      if (!USER_ID) {
        throw new Error("Configure VITE_DEMO_USER_ID in frontend/.env.");
      }

      // The backend calculates the 14-day pay period from pay_date.
      const paycheckData: PaycheckCreate = {
        user_id: USER_ID,
        amount: paycheckAmount,
        pay_date: payDate,
      };

      await postJson<Paycheck, PaycheckCreate>(
        "/paychecks",
        paycheckData,
      );

      // Refresh the paycheck list so the new paycheck becomes current.
      await loadDashboard();

      // Reset the form after a successful submission.
      setPaycheckAmount("");
      setPayDate(getToday());
      setMessage("Paycheck added successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to add paycheck.",
      );
    } finally {
      setSaving("");
    }
  }

  // Create a category; its budget is optional.
  async function handleAddCategory(event: FormSubmitEvent) {
    event.preventDefault();
    setSaving("category");
    setError("");
    setMessage("");

    try {
      if (!USER_ID) {
        throw new Error("Configure VITE_DEMO_USER_ID in frontend/.env.");
      }

      // Send null when the optional budget field is left blank.
      const categoryData: ExpenseCategoryCreate = {
        user_id: USER_ID,
        name: categoryName.trim(),
        budget: categoryBudget.trim() === "" ? null : categoryBudget,
        type: categoryType,
        active: true,
      };

      await postJson<ExpenseCategory, ExpenseCategoryCreate>(
        "/expense-categories",
        categoryData,
      );

      // Reload categories so the new one appears immediately.
      await loadDashboard();

      // Reset the category form.
      setCategoryName("");
      setCategoryBudget("");
      setCategoryType("VARIABLE_NON_RECURRING");
      setMessage("Expense category added successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to add expense category.",
      );
    } finally {
      setSaving("");
    }
  }

  // Add an expense to the current paycheck automatically.
  async function handleAddExpense(event: FormSubmitEvent) {
    event.preventDefault();
    setSaving("expense");
    setError("");
    setMessage("");

    // Expenses cannot be created until a paycheck exists.
    if (!currentPaycheck) {
      setError("Add a paycheck before adding expenses.");
      setSaving("");
      return;
    }

    try {
      // Always use the current paycheck; there is no paycheck dropdown.
      const expenseData: ExpenseItemCreate = {
        category_id: expenseCategoryId,
        paycheck_id: currentPaycheck.id,
        name: expenseName.trim(),
        amount: expenseAmount,
        spent_on: spentOn,
      };

      await postJson<ExpenseItem, ExpenseItemCreate>(
        "/expense-items",
        expenseData,
      );

      // Reload expenses immediately after a successful submission.
      const updatedExpenses = await getJson<ExpenseItem[]>(
        `/expense-items?paycheck_id=${encodeURIComponent(currentPaycheck.id)}`,
      );

      setExpenses(updatedExpenses);

      // Reset the purchase-specific fields.
      setExpenseName("");
      setExpenseAmount("");
      setSpentOn(getToday());
      setMessage("Expense added successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to add expense.",
      );
    } finally {
      setSaving("");
    }
  }

  // Display a loading message while the initial dashboard request runs.
  if (loading) {
    return (
      <main className="dashboard">
        <h1>Paycheck Tracker</h1>
        <p>Loading dashboard...</p>
      </main>
    );
  }

  return (
    <main className="dashboard">
      <header>
        <h1>Paycheck Tracker</h1>
        <p>Track your paychecks, expenses, and spending budgets.</p>
      </header>

      {/* Show request errors and successful-action messages. */}
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {message && (
        <p className="success-message" role="status">
          {message}
        </p>
      )}

      {/* Current paycheck summary. */}
      <section className="panel">
        <h2>Current Paycheck</h2>

        {currentPaycheck ? (
          <>
            <p className="summary-amount">
              {formatCurrency(currentPaycheck.amount)}
            </p>

            <p>
              Pay period: {currentPaycheck.period_start} –{" "}
              {currentPaycheck.period_end}
            </p>

            <p>Pay date: {currentPaycheck.pay_date}</p>
          </>
        ) : (
          <p>No paycheck has been added yet.</p>
        )}
      </section>

      {/* Add-paycheck form. */}
      <section className="panel">
        <h2>Add Paycheck</h2>

        <form onSubmit={handleAddPaycheck}>
          <label>
            Paycheck amount
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={paycheckAmount}
              onChange={(event) => setPaycheckAmount(event.target.value)}
              placeholder="3000.00"
              required
            />
          </label>

          <label>
            Pay date
            <input
              type="date"
              value={payDate}
              onChange={(event) => setPayDate(event.target.value)}
              required
            />
          </label>

          <button type="submit" disabled={saving !== ""}>
            {saving === "paycheck" ? "Adding..." : "Add Paycheck"}
          </button>
        </form>
      </section>

      {/* Add-category form. */}
      <section className="panel">
        <h2>Add Expense Category</h2>

        <form onSubmit={handleAddCategory}>
          <label>
            Category name
            <input
              type="text"
              value={categoryName}
              onChange={(event) => setCategoryName(event.target.value)}
              placeholder="Groceries"
              maxLength={100}
              required
            />
          </label>

          <label>
            Budget (optional)
            <input
              type="number"
              min="0"
              step="0.01"
              value={categoryBudget}
              onChange={(event) => setCategoryBudget(event.target.value)}
              placeholder="Leave blank for no budget"
            />
          </label>

          <label>
            Category type
            <select
              value={categoryType}
              onChange={(event) =>
                setCategoryType(event.target.value as ExpenseCategory["type"])
              }
              required
            >
              <option value="VARIABLE_NON_RECURRING">
                Variable non-recurring
              </option>
              <option value="FIXED_RECURRING">Fixed recurring</option>
              <option value="VARIABLE_RECURRING">Variable recurring</option>
            </select>
          </label>

          <button type="submit" disabled={saving !== ""}>
            {saving === "category" ? "Adding..." : "Add Category"}
          </button>
        </form>
      </section>

      {/* Display active categories and their configured budgets. */}
      <section className="panel">
        <h2>Expense Categories</h2>

        {categories.length === 0 ? (
          <p>No expense categories yet. Add one above.</p>
        ) : (
          <ul className="record-list">
            {categories.map((category) => (
              <li key={category.id}>
                <div>
                  <strong>{category.name}</strong>
                  <p>{category.type.replaceAll("_", " ")}</p>
                </div>

                <span>
                  {category.budget === null
                    ? "No budget"
                    : `Budget: ${formatCurrency(category.budget)}`}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Add-expense form; the current paycheck is selected automatically. */}
      <section className="panel">
        <h2>Add Expense</h2>

        {!currentPaycheck ? (
          <p>Add a paycheck first to start recording expenses.</p>
        ) : regularCategories.length === 0 ? (
          <p>
            Add a variable non-recurring category first, such as Groceries or
            Eating Out.
          </p>
        ) : (
          <form onSubmit={handleAddExpense}>
            <p>
              Adding expense to paycheck dated{" "}
              <strong>{currentPaycheck.pay_date}</strong>.
            </p>

            <label>
              Expense category
              <select
                value={expenseCategoryId}
                onChange={(event) => setExpenseCategoryId(event.target.value)}
                required
              >
                {regularCategories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Expense name
              <input
                type="text"
                value={expenseName}
                onChange={(event) => setExpenseName(event.target.value)}
                placeholder="Weekly groceries"
                maxLength={150}
                required
              />
            </label>

            <label>
              Amount
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={expenseAmount}
                onChange={(event) => setExpenseAmount(event.target.value)}
                placeholder="75.50"
                required
              />
            </label>

            <label>
              Date of purchase
              <input
                type="date"
                value={spentOn}
                onChange={(event) => setSpentOn(event.target.value)}
                required
              />
            </label>

            <button type="submit" disabled={saving !== ""}>
              {saving === "expense" ? "Adding..." : "Add Expense"}
            </button>
          </form>
        )}
      </section>

      {/* Display expenses associated with the current paycheck only. */}
      <section className="panel">
        <h2>Current Paycheck Expenses</h2>

        {!currentPaycheck ? (
          <p>Add a paycheck to view its expenses.</p>
        ) : expenses.length === 0 ? (
          <p>No expenses recorded for this paycheck yet.</p>
        ) : (
          <ul className="record-list">
            {expenses.map((expense) => {
              // Find the category name for a more readable expense list.
              const category = categories.find(
                (item) => item.id === expense.category_id,
              );

              return (
                <li key={expense.id}>
                  <div>
                    <strong>{expense.name}</strong>
                    <p>
                      {category?.name ?? "Unknown category"} · {expense.spent_on}
                    </p>
                  </div>

                  <strong>{formatCurrency(expense.amount)}</strong>
                </li>
              );
            })}
          </ul>
        )}

        {/* Summarize the expenses currently displayed. */}
        {expenses.length > 0 && (
          <p className="summary-amount">
            Total:{" "}
            {formatCurrency(
              expenses.reduce(
                (total, expense) => total + Number(expense.amount),
                0,
              ),
            )}
          </p>
        )}
      </section>
    </main>
  );
}

export default App;