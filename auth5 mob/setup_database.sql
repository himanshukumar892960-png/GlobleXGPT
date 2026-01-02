-- ========================================
-- FIX SUPABASE AUTH & DATABASE (Robust Version)
-- ========================================

-- 1. CLEANUP: Drop potential conflict items first
drop trigger if exists on_auth_user_created on auth.users;
drop function if exists public.handle_new_user;

-- 2. TABLE: Ensure 'profiles' table exists
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  full_name text default '',
  avatar_url text default '',
  provider text default 'email',
  created_at timestamptz default now()
);

-- 3. SECURITY: Enable RLS
alter table public.profiles enable row level security;

-- 4. POLICIES: Clean up old policies to avoid "already exists" errors
drop policy if exists "read own profile" on public.profiles;
drop policy if exists "insert own profile" on public.profiles;
drop policy if exists "update own profile" on public.profiles;
drop policy if exists "Public profiles are viewable by everyone." on public.profiles;
drop policy if exists "Users can insert their own profile." on public.profiles;
drop policy if exists "Users can update own profile." on public.profiles;

-- 5. POLICIES: Create new standard policies
create policy "read own profile"
on public.profiles for select
using (auth.uid() = id);

create policy "insert own profile"
on public.profiles for insert
with check (auth.uid() = id);

create policy "update own profile"
on public.profiles for update
using (auth.uid() = id);

-- 6. AUTOMATION: Re-add the Trigger (Fixed)
-- This ensures a profile is created automatically when a user signs up
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, full_name, avatar_url)
  values (
    new.id, 
    new.email, 
    new.raw_user_meta_data->>'full_name', 
    new.raw_user_meta_data->>'avatar_url'
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- DONE: Run this entire script in Supabase SQL Editor
