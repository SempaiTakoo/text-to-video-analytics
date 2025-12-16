CREATE TABLE raw_video_json (
    payload jsonb NOT NULL
);

COMMENT ON TABLE raw_video_json IS
'Сырая загрузка JSON для последующего парсинга в нормализованные таблицы.';


INSERT INTO raw_video_json (payload)
SELECT pg_read_file('/docker-entrypoint-initdb.d/data.json')::jsonb;


INSERT INTO creators (id)
SELECT DISTINCT (video->>'creator_id')::uuid
FROM raw_video_json,
     jsonb_array_elements(payload->'videos') AS video
ON CONFLICT DO NOTHING;


INSERT INTO videos (
    id,
    creator_id,
    video_created_at,
    views_count,
    likes_count,
    reports_count,
    comments_count,
    created_at,
    updated_at
)
SELECT
    (video->>'id')::uuid,
    (video->>'creator_id')::uuid,
    (video->>'video_created_at')::timestamptz,
    (video->>'views_count')::bigint,
    (video->>'likes_count')::bigint,
    (video->>'reports_count')::bigint,
    (video->>'comments_count')::bigint,
    (video->>'created_at')::timestamptz,
    (video->>'updated_at')::timestamptz
FROM raw_video_json,
     jsonb_array_elements(payload->'videos') AS video;


INSERT INTO video_snapshots (
    id,
    video_id,
    views_count,
    likes_count,
    reports_count,
    comments_count,
    delta_views_count,
    delta_likes_count,
    delta_reports_count,
    delta_comments_count,
    created_at,
    updated_at
)
SELECT
    (snap->>'id')::uuid,
    (snap->>'video_id')::uuid,
    (snap->>'views_count')::bigint,
    (snap->>'likes_count')::bigint,
    (snap->>'reports_count')::bigint,
    (snap->>'comments_count')::bigint,
    (snap->>'delta_views_count')::bigint,
    (snap->>'delta_likes_count')::bigint,
    (snap->>'delta_reports_count')::bigint,
    (snap->>'delta_comments_count')::bigint,
    (snap->>'created_at')::timestamptz,
    (snap->>'updated_at')::timestamptz
FROM raw_video_json,
     jsonb_array_elements(payload->'videos') AS video,
     jsonb_array_elements(video->'snapshots') AS snap;


DROP TABLE raw_video_json;
