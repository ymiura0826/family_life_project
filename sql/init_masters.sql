-- 性別マスタ（m_sex）
INSERT INTO m_sex (id, name,order_id, created_at, updated_at)
VALUES
  (1, '男', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  (2, '女', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ミルク種別マスタ（m_milk_type）
INSERT INTO m_milk_type (id, name, order_id, created_at, updated_at)
VALUES
  (1, '母乳', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  (2, '搾乳', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  (3, '粉ミルク', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 排泄種別マスタ（m_excretion_type）
INSERT INTO m_excretion_type (id, name, order_id, created_at, updated_at)
VALUES
  (1, 'おしっこ', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  (2, 'うんち', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


-- 通知種別マスタ（m_notify_type）
INSERT INTO m_notify_type (id, name, order_id, created_at, updated_at)
VALUES
  (1, 'milk', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


-- 通知手段マスタ（m_notify_method）
INSERT INTO m_notify_method (id, name, order_id, created_at, updated_at)
VALUES
  (1, 'line_notfiy', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  (2, 'email', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

