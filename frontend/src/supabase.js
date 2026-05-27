import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://nxdjqmwbjmcfgcwzztdz.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im54ZGpxbXdiam1jZmdjd3p6dGR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NDk2OTAsImV4cCI6MjA5NTQyNTY5MH0.o_J_C4GUx_r50b4Amh11AUJoUVXG4sJf8txrjNRpp2g";

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);