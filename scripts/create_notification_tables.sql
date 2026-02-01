-- ============================================
-- DietNotify Notification System - Supabase Tables
-- Run this SQL in Supabase SQL Editor
-- ============================================

-- Table 1: Store FCM device tokens for push notifications
CREATE TABLE IF NOT EXISTS notification_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    fcm_token TEXT NOT NULL UNIQUE,
    device_info JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast user token lookups
CREATE INDEX IF NOT EXISTS idx_notification_tokens_user ON notification_tokens(user_id);

-- Table 2: Store user notification preferences
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    enabled BOOLEAN DEFAULT TRUE,
    lead_time_minutes INTEGER DEFAULT 5,
    custom_timings JSONB DEFAULT '{}',
    quiet_hours_start TIME DEFAULT NULL,
    quiet_hours_end TIME DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast preference lookups
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user ON notification_preferences(user_id);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE notification_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- Add custom_timings column if it doesn't exist (Safer approach)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='notification_preferences' AND column_name='custom_timings') THEN
        ALTER TABLE notification_preferences ADD COLUMN custom_timings JSONB DEFAULT '{}';
    END IF;
END $$;

-- Policy: Allow all operations for authenticated requests (using anon key)
-- NOTE: If you get "policy already exists" errors, you can safely ignore them 
-- as it means your security settings are already correctly configured.
DO $$ 
BEGIN
    BEGIN
        CREATE POLICY "Allow insert for anon" ON notification_tokens FOR INSERT WITH CHECK (true);
    EXCEPTION WHEN others THEN NULL; END;
    
    BEGIN
        CREATE POLICY "Allow select for anon" ON notification_tokens FOR SELECT USING (true);
    EXCEPTION WHEN others THEN NULL; END;
    
    BEGIN
        CREATE POLICY "Allow update for anon" ON notification_tokens FOR UPDATE USING (true);
    EXCEPTION WHEN others THEN NULL; END;
    
    BEGIN
        CREATE POLICY "Allow delete for anon" ON notification_tokens FOR DELETE USING (true);
    EXCEPTION WHEN others THEN NULL; END;

    -- Preferences
    BEGIN
        CREATE POLICY "Allow insert for anon" ON notification_preferences FOR INSERT WITH CHECK (true);
    EXCEPTION WHEN others THEN NULL; END;
    
    BEGIN
        CREATE POLICY "Allow select for anon" ON notification_preferences FOR SELECT USING (true);
    EXCEPTION WHEN others THEN NULL; END;
    
    BEGIN
        CREATE POLICY "Allow update for anon" ON notification_preferences FOR UPDATE USING (true);
    EXCEPTION WHEN others THEN NULL; END;
    
    BEGIN
        CREATE POLICY "Allow delete for anon" ON notification_preferences FOR DELETE USING (true);
    EXCEPTION WHEN others THEN NULL; END;
END $$;
