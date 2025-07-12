-- Habit Tracker Database Schema
-- SQLite schema for habit tracking application

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Habits table
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    frequency VARCHAR(20) NOT NULL DEFAULT 'daily', -- daily, weekly, monthly
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Habit logs table - tracks completion of habits
CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
);

-- Streaks table - tracks current and longest streaks
CREATE TABLE IF NOT EXISTS streaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER UNIQUE NOT NULL,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_completed DATE,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id);
CREATE INDEX IF NOT EXISTS idx_habit_logs_habit_id ON habit_logs(habit_id);
CREATE INDEX IF NOT EXISTS idx_habit_logs_completed_at ON habit_logs(completed_at);
CREATE INDEX IF NOT EXISTS idx_streaks_habit_id ON streaks(habit_id);

-- Sample data for testing
INSERT OR IGNORE INTO users (username, email, password_hash) VALUES
('demo_user', 'demo@example.com', 'hashed_password_demo'),
('test_user', 'test@example.com', 'hashed_password_test');

INSERT OR IGNORE INTO habits (user_id, name, description, frequency) VALUES
(1, 'Morning Exercise', 'Do 30 minutes of exercise every morning', 'daily'),
(1, 'Read Books', 'Read at least 30 pages of a book', 'daily'),
(1, 'Meditation', 'Practice mindfulness meditation', 'daily'),
(2, 'Weekly Planning', 'Plan the upcoming week', 'weekly');

INSERT OR IGNORE INTO streaks (habit_id, current_streak, longest_streak, last_completed) VALUES
(1, 5, 10, date('now', '-1 day')),
(2, 3, 7, date('now', '-1 day')),
(3, 0, 5, date('now', '-3 days')),
(4, 1, 3, date('now', '-7 days'));
