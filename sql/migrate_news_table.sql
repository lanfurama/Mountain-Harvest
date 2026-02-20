-- Migration: Update news table structure
-- Add content and author columns, remove summary column

ALTER TABLE news 
  ADD COLUMN IF NOT EXISTS content TEXT,
  ADD COLUMN IF NOT EXISTS author VARCHAR(255),
  DROP COLUMN IF EXISTS summary;
