CREATE TABLE creators (
    id uuid PRIMARY KEY
);


CREATE TABLE videos (
    id uuid PRIMARY KEY,

    creator_id uuid NOT NULL,
    video_created_at timestamptz NOT NULL,

    views_count bigint NOT NULL DEFAULT 0,
    likes_count bigint NOT NULL DEFAULT 0,
    reports_count bigint NOT NULL DEFAULT 0,
    comments_count bigint NOT NULL DEFAULT 0,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT fk_videos_creator
        FOREIGN KEY (creator_id)
        REFERENCES creators (id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE videos IS
'Видео как основная бизнес-сущность. Хранит текущее агрегированное состояние метрик.';

COMMENT ON COLUMN videos.id IS
'Уникальный идентификатор видео.';

COMMENT ON COLUMN videos.creator_id IS
'Идентификатор автора (создателя), которому принадлежит видео.';

COMMENT ON COLUMN videos.video_created_at IS
'Дата и время фактического создания или публикации видео в продукте.';

COMMENT ON COLUMN videos.views_count IS
'Текущее общее количество просмотров видео.';

COMMENT ON COLUMN videos.likes_count IS
'Текущее общее количество лайков видео.';

COMMENT ON COLUMN videos.reports_count IS
'Текущее общее количество жалоб на видео.';

COMMENT ON COLUMN videos.comments_count IS
'Текущее общее количество комментариев к видео.';

COMMENT ON COLUMN videos.created_at IS
'Дата и время создания записи видео в базе данных.';

COMMENT ON COLUMN videos.updated_at IS
'Дата и время последнего обновления записи видео в базе данных.';


CREATE TABLE video_snapshots (
    id uuid PRIMARY KEY,

    video_id uuid NOT NULL,

    views_count bigint NOT NULL,
    likes_count bigint NOT NULL,
    reports_count bigint NOT NULL,
    comments_count bigint NOT NULL,

    delta_views_count bigint NOT NULL,
    delta_likes_count bigint NOT NULL,
    delta_reports_count bigint NOT NULL,
    delta_comments_count bigint NOT NULL,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT fk_video_snapshots_video
        FOREIGN KEY (video_id)
        REFERENCES videos (id)
        ON DELETE CASCADE
);

COMMENT ON TABLE video_snapshots IS
'Исторические срезы метрик видео на конкретные моменты времени. Используются для аналитики и временных рядов.';

COMMENT ON COLUMN video_snapshots.id IS
'Уникальный идентификатор snapshot (среза метрик).';

COMMENT ON COLUMN video_snapshots.video_id IS
'Идентификатор видео, к которому относится данный snapshot.';

COMMENT ON COLUMN video_snapshots.views_count IS
'Количество просмотров видео на момент создания snapshot.';

COMMENT ON COLUMN video_snapshots.likes_count IS
'Количество лайков видео на момент создания snapshot.';

COMMENT ON COLUMN video_snapshots.reports_count IS
'Количество жалоб на видео на момент создания snapshot.';

COMMENT ON COLUMN video_snapshots.comments_count IS
'Количество комментариев к видео на момент создания snapshot.';

COMMENT ON COLUMN video_snapshots.delta_views_count IS
'Изменение количества просмотров по сравнению с предыдущим snapshot.';

COMMENT ON COLUMN video_snapshots.delta_likes_count IS
'Изменение количества лайков по сравнению с предыдущим snapshot.';

COMMENT ON COLUMN video_snapshots.delta_reports_count IS
'Изменение количества жалоб по сравнению с предыдущим snapshot.';

COMMENT ON COLUMN video_snapshots.delta_comments_count IS
'Изменение количества комментариев по сравнению с предыдущим snapshot.';

COMMENT ON COLUMN video_snapshots.created_at IS
'Дата и время создания snapshot в базе данных.';

COMMENT ON COLUMN video_snapshots.updated_at IS
'Дата и время последнего обновления snapshot в базе данных.';


CREATE INDEX idx_videos_creator_id
    ON videos (creator_id);

COMMENT ON INDEX idx_videos_creator_id IS
'Индекс для быстрого получения всех видео конкретного автора.';


CREATE INDEX idx_video_snapshots_video_id
    ON video_snapshots (video_id);

COMMENT ON INDEX idx_video_snapshots_video_id IS
'Индекс для быстрого получения всех snapshot-ов конкретного видео.';


CREATE INDEX idx_video_snapshots_video_created_at
    ON video_snapshots (video_id, created_at DESC);

COMMENT ON INDEX idx_video_snapshots_video_created_at IS
'Индекс для эффективных запросов по временным рядам snapshot-ов видео.';
