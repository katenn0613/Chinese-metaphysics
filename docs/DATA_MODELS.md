# 初版数据结构设计

## 1. UserProfile

本地存储字段：

- `id`
- `display_name`
- `gender`
- `birth_info`
- `tags`
- `notes`
- `created_at`
- `updated_at`

UI 展示字段：

- `display_label`
- `birth_summary`
- `last_used_at`

## 2. BirthInfo

本地存储字段：

- `calendar_type`: solar/lunar
- `birth_datetime`
- `timezone`
- `birthplace_name`
- `longitude`
- `latitude`
- `use_true_solar_time`
- `gender`

计算中间字段：

- `normalized_solar_datetime`
- `true_solar_datetime`
- `timezone_offset_minutes`
- `calendar_conversion_notes`

## 3. BaziChart

本地存储字段：

- `id`
- `birth_info`
- `pillars`
- `day_master`
- `five_element_scores`
- `yin_yang_scores`
- `calculation_notes`
- `algorithm_version`
- `created_at`

计算中间字段：

- `solar_terms`
- `hidden_stems`
- `ten_gods`（当前已写入各柱天干关系）
- `luck_cycles`
- `void_branches`

UI 展示字段：

- `chart_table`
- `five_element_chart_data`
- `summary_badges`

## 4. InterpretationResult

本地存储字段：

- `id`
- `chart_id`
- `mode`: professional/beginner
- `summary`
- `sections`
- `created_at`
- `generator_version`

AI 解释结果字段：

- `ai_model`
- `prompt_version`
- `confidence_notes`
- `follow_up_questions`

UI 展示字段：

- `reading_mode_label`
- `section_cards`
- `highlighted_terms`

## 5. FortuneConsultationSession

本地存储字段：

- `id`
- `chart_id`
- `title`
- `messages`
- `created_at`
- `updated_at`

AI 解释结果字段：

- `provider`
- `model`
- `system_prompt_version`
- `token_usage`

## 6. AlmanacDateSelection

本地存储字段：

- `id`
- `purpose`
- `date_range_start`
- `date_range_end`
- `constraints`
- `candidate_dates`
- `created_at`

计算中间字段：

- `day_stems_branches`
- `avoid_rules`
- `score_breakdown`

UI 展示字段：

- `recommendation_level`
- `reason_tags`
- `calendar_table_rows`

## 7. HistoryRecord

本地存储字段：

- `id`
- `record_type`
- `title`
- `payload`
- `tags`
- `created_at`
- `updated_at`

UI 展示字段：

- `record_icon`
- `subtitle`
- `preview_text`

## 8. ExportTask / ReportTemplate

本地存储字段：

- `id`
- `record_id`
- `template_id`
- `format`
- `status`
- `output_path`
- `created_at`
- `finished_at`

UI 展示字段：

- `progress_label`
- `open_file_action`

## 9. AppSettings

当前 SQLite 表：`app_settings`

本地存储字段：

- `key`
- `value_json`
- `updated_at`

当前已使用设置：

- `default_timezone`
- `default_true_solar_time`

## 10. SQLite Tables

当前 schema：

- `history_records`
- `app_settings`
- `user_profiles`

当前索引：

- `idx_history_records_recent`
- `idx_user_profiles_recent`
