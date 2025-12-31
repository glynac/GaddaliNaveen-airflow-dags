CREATE TABLE IF NOT EXISTS public.email_thread_details (
    thread_id INTEGER NOT NULL,
    subject TEXT NULL,
    "from" TEXT NOT NULL,
    "to" TEXT NULL,
    body TEXT NULL,
    "timestamp" TIMESTAMP NULL,
    PRIMARY KEY (thread_id)
);
