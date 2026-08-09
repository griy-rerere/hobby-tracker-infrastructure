SELECT
    COUNT(*) AS activity_count,
    SUM(duration) AS total_duration,
    AVG(duration) AS avg_duration
FROM activity

WHERE ? <= started_at AND started_at < ?
