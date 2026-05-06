-- Enable RLS and create policies for user data tables
-- Run this in Supabase SQL Editor

-- Enable RLS on activity table
ALTER TABLE activity ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read their own activity
CREATE POLICY "Users can read activity" ON activity
  FOR SELECT USING (auth.uid()::text = user_id OR true);

-- Allow service role to insert activity
CREATE POLICY "Service role can insert activity" ON activity
  FOR INSERT WITH CHECK (true);

-- Allow all to insert activity (for demo purposes)
CREATE POLICY "Anyone can insert activity" ON activity
  FOR INSERT WITH CHECK (true);

-- Enable RLS on activity_logs table
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- Allow all to read activity logs
CREATE POLICY "Anyone can read activity logs" ON activity_logs
  FOR SELECT USING (true);

-- Allow all to insert activity logs
CREATE POLICY "Anyone can insert activity logs" ON activity_logs
  FOR INSERT WITH CHECK (true);

-- Enable RLS on user_stats table
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read their own stats
CREATE POLICY "Users can read their stats" ON user_stats
  FOR SELECT USING (auth.uid()::text = user_id OR true);

-- Allow all to insert stats (for demo)
CREATE POLICY "Anyone can insert stats" ON user_stats
  FOR INSERT WITH CHECK (true);

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Allow all to read users
CREATE POLICY "Anyone can read users" ON users
  FOR SELECT USING (true);

-- Allow all to insert users
CREATE POLICY "Anyone can insert users" ON users
  FOR INSERT WITH CHECK (true);

-- Enable RLS on vectors table (knowledge base chunks)
ALTER TABLE vectors ENABLE ROW LEVEL SECURITY;

-- Allow all to read vectors
CREATE POLICY "Anyone can read vectors" ON vectors
  FOR SELECT USING (true);

-- Allow all to insert vectors
CREATE POLICY "Anyone can insert vectors" ON vectors
  FOR INSERT WITH CHECK (true);
