-- Test Case 1: NBA player data loading and validation
CREATE DATABASE IF NOT EXISTS test_cases;
USE test_cases;

CREATE TABLE IF NOT EXISTS nba_players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Team VARCHAR(100) NOT NULL,
    Number INT,
    Position VARCHAR(10),
    Age INT,
    Height VARCHAR(10),
    Weight INT,
    College VARCHAR(150),
    Salary DECIMAL(12,2),
    CONSTRAINT uq_nba_player UNIQUE (Name, Team, Number)
);
