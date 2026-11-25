CREATE DATABASE IF NOT EXISTS test_case_13;
USE test_case_13;

CREATE TABLE IF NOT EXISTS employees (
    employee_id INT PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    job_title VARCHAR(100),
    department VARCHAR(100),
    manager_id INT,
    salary DECIMAL(10,2),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

INSERT INTO employees
(employee_id, employee_name, job_title, department, manager_id, salary)
VALUES
(1, 'Robert', 'CEO', 'Management', NULL, 150000),
(2, 'Alice', 'CTO', 'Technology', 1, 120000),
(3, 'David', 'CFO', 'Finance', 1, 110000),
(4, 'Emma', 'COO', 'Operations', 1, 115000),
(5, 'Michael', 'Engineering Manager', 'Technology', 2, 95000),
(6, 'Sophia', 'IT Manager', 'Technology', 2, 90000),
(7, 'James', 'Senior Developer', 'Technology', 5, 80000),
(8, 'Olivia', 'Developer', 'Technology', 5, 70000),
(9, 'Daniel', 'Developer', 'Technology', 5, 72000),
(10, 'Liam', 'System Administrator', 'Technology', 6, 75000),
(11, 'Noah', 'Network Engineer', 'Technology', 6, 68000),
(12, 'Charlotte', 'Finance Manager', 'Finance', 3, 85000),
(13, 'William', 'Accountant', 'Finance', 12, 60000),
(14, 'Mia', 'Financial Analyst', 'Finance', 12, 65000),
(15, 'Benjamin', 'Operations Manager', 'Operations', 4, 88000),
(16, 'Lucas', 'Operations Executive', 'Operations', 15, 55000),
(17, 'Amelia', 'Operations Executive', 'Operations', 15, 58000);

-- Find the manager chain for employee 17.
WITH RECURSIVE manager_chain AS (
    SELECT employee_id, employee_name, job_title, department, manager_id, salary, 0 AS hierarchy_level
    FROM employees
    WHERE employee_id = 17
    UNION ALL
    SELECT e.employee_id, e.employee_name, e.job_title, e.department, e.manager_id, e.salary,
           mc.hierarchy_level + 1
    FROM employees AS e
    JOIN manager_chain AS mc ON e.employee_id = mc.manager_id
)
SELECT * FROM manager_chain;

-- Find the manager chain for employee 2.
WITH RECURSIVE manager_chain AS (
    SELECT employee_id, employee_name, job_title, department, manager_id, salary, 0 AS hierarchy_level
    FROM employees
    WHERE employee_id = 2
    UNION ALL
    SELECT e.employee_id, e.employee_name, e.job_title, e.department, e.manager_id, e.salary,
           mc.hierarchy_level + 1
    FROM employees AS e
    JOIN manager_chain AS mc ON e.employee_id = mc.manager_id
)
SELECT * FROM manager_chain;

-- Build the full employee hierarchy starting from the CEO.
WITH RECURSIVE employee_hierarchy AS (
    SELECT employee_id, employee_name, job_title, department, manager_id, salary,
           0 AS hierarchy_level
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    SELECT e.employee_id, e.employee_name, e.job_title, e.department, e.manager_id, e.salary,
           eh.hierarchy_level + 1
    FROM employees AS e
    JOIN employee_hierarchy AS eh ON e.manager_id = eh.employee_id
)
SELECT *
FROM employee_hierarchy
ORDER BY hierarchy_level, employee_id;
