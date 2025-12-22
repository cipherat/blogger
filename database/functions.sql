DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'blog_state') THEN
        CREATE TYPE blog_state AS ENUM ('drafted', 'published');
    END IF;
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


CREATE OR REPLACE FUNCTION fn_enforce_published_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.state = 'published' AND NEW.published_at IS NULL THEN
        NEW.published_at := CURRENT_TIMESTAMP;
    END IF;

    NEW.last_update := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trg_set_published_date ON blogs;
CREATE TRIGGER trg_set_published_date
BEFORE INSERT OR UPDATE ON blogs
FOR EACH ROW
EXECUTE FUNCTION fn_enforce_published_date();


CREATE OR REPLACE FUNCTION fn_get_paged_blogs(
    p_state blog_state DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
) 
RETURNS TABLE (
    id VARCHAR, title TEXT, category VARCHAR, keywords TEXT[], 
    created_at TIMESTAMP WITH TIME ZONE, published_at TIMESTAMP WITH TIME ZONE, 
    last_update TIMESTAMP WITH TIME ZONE, content_file TEXT, 
    "references" TEXT[], state blog_state, total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH filtered AS (
        SELECT 
            b.id, b.title, b.category, b.keywords, 
            b.created_at, b.published_at, b.last_update, 
            b.content_file, b."references", b.state 
        FROM blogs b
        WHERE (p_state IS NULL OR b.state = p_state)
    ),
    total_count_val AS (
        SELECT count(*) as total FROM filtered
    )
    SELECT f.*, t.total
    FROM filtered f, total_count_val t
    ORDER BY f.published_at DESC NULLS LAST, f.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_blog_by_id(p_id VARCHAR)
RETURNS TABLE (
    id VARCHAR, title TEXT, category VARCHAR, keywords TEXT[], 
    created_at TIMESTAMP WITH TIME ZONE, published_at TIMESTAMP WITH TIME ZONE, 
    last_update TIMESTAMP WITH TIME ZONE, content_file TEXT, 
    "references" TEXT[], state blog_state
) AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        b.id, b.title, b.category, b.keywords, 
        b.created_at, b.published_at, b.last_update, 
        b.content_file, b."references", b.state 
    FROM blogs b 
    WHERE b.id = p_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_blog_by_permalink(
    p_year TEXT, p_month TEXT, p_day TEXT, p_slug TEXT
)
RETURNS TABLE (
    id VARCHAR, title TEXT, category VARCHAR, keywords TEXT[], 
    created_at TIMESTAMP WITH TIME ZONE, published_at TIMESTAMP WITH TIME ZONE, 
    last_update TIMESTAMP WITH TIME ZONE, content_file TEXT, 
    "references" TEXT[], state blog_state
) AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        b.id, b.title, b.category, b.keywords, 
        b.created_at, b.published_at, b.last_update, 
        b.content_file, b."references", b.state 
    FROM blogs b 
    WHERE TO_CHAR(COALESCE(b.published_at, b.created_at), 'YYYY') = p_year
      AND TO_CHAR(COALESCE(b.published_at, b.created_at), 'MM') = p_month
      AND TO_CHAR(COALESCE(b.published_at, b.created_at), 'DD') = p_day
      AND TRIM(BOTH '-' FROM LOWER(REGEXP_REPLACE(b.title, '[^a-zA-Z0-9]+', '-', 'g'))) = LOWER(p_slug);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_add_blog(
    p_id VARCHAR, p_title TEXT, p_category VARCHAR, p_keywords TEXT[],
    p_created_at TIMESTAMP WITH TIME ZONE, p_published_at TIMESTAMP WITH TIME ZONE,
    p_last_update TIMESTAMP WITH TIME ZONE, p_content_file TEXT,
    p_references TEXT[], p_state blog_state
) RETURNS VOID AS $$
BEGIN
    INSERT INTO blogs (
        id, title, category, keywords, 
        created_at, published_at, last_update, 
        content_file, "references", state
    )
    VALUES (
        p_id, p_title, p_category, p_keywords, 
        p_created_at, p_published_at, p_last_update, 
        p_content_file, p_references, p_state
    );
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_update_blog(
    p_id VARCHAR, p_title TEXT, p_category VARCHAR, p_keywords TEXT[],
    p_published_at TIMESTAMP WITH TIME ZONE, p_content_file TEXT,
    p_references TEXT[], p_state blog_state
) RETURNS VOID AS $$
BEGIN
    UPDATE blogs SET
        title = p_title,
        category = p_category,
        keywords = p_keywords,
        published_at = p_published_at,
        content_file = p_content_file,
        "references" = p_references,
        state = p_state
    WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_delete_blog(p_id VARCHAR)
RETURNS VOID AS $$
BEGIN
    DELETE FROM blogs WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;
