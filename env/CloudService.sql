CREATE DATABASE CloudService;
USE CloudService;

CREATE TABLE subscription_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    api_permissions TEXT,
    usage_limit INT NOT NULL
);

CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    api_endpoint VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE user_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    plan_id INT NOT NULL,
    usage_count INT DEFAULT 0,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
);

SELECT * FROM subscription_plans;
SELECT * FROM permissions;
SELECT * FROM user_subscriptions;
