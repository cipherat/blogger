DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'blog_state') THEN
        CREATE TYPE blog_state AS ENUM ('drafted', 'published');
    END IF;
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


CREATE TABLE IF NOT EXISTS blogs (
    id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    keywords TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    last_update TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    content_file TEXT NOT NULL,
    "references" TEXT[],
    state blog_state DEFAULT 'drafted' NOT NULL
);


CREATE INDEX IF NOT EXISTS idx_blogs_state_published ON blogs (state, published_at DESC);
